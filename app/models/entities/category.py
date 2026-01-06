from datetime import datetime
from app.extension import db
from app.utils import format_datetime_to_string

class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True, comment='目录ID')
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False, comment='项目ID')
    name = db.Column(db.String(255), nullable=False, comment='目录名称')
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True, comment='父目录ID', )  # 自引用外键，nullable=True表示可以为空，表示一个目录可以没有父目录
    icon = db.Column(db.String(255), nullable=True, comment='目录图标')
    description = db.Column(db.String(255), nullable=True, comment='目录描述')
    is_deleted = db.Column(db.Boolean, nullable=False, default=False, comment='是否删除目录')
    delete_time = db.Column(db.DateTime, nullable=True, comment='删除时间')
    create_time = db.Column(db.DateTime, default=datetime.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), comment='更新时间')

    articles = db.relationship('Article', back_populates='category', lazy=True)

    # 自关联：子目录
    '''
    1. 'Category'
        - 表示这个关系关联到 同一个模型 （Category 类本身）
        - 实现了 自关联 ，即一个 Category 可以包含多个子 Category
    2. backref=db.backref('parent', remote_side=[id])
        - backref='parent' : 创建反向引用，从子目录可以通过 category.parent 访问父目录
        - remote_side=[id] : 指定 id 字段为关系的"远端"，明确哪一端是父级
    - 这样 SQLAlchemy 知道 parent_id 指向的是父目录的 id
    - 避免了循环引用的歧义
    3. lazy='dynamic'
        - 延迟加载策略，返回一个查询对象而不是直接加载所有子目录
        - 可以进一步过滤： category.children.filter_by(is_deleted=False)
        - 节省内存，按需加载
    '''
    children = db.relationship(
        'Category',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )

    # 打印目录信息
    def dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'parent_id': self.parent_id,
            'icon': self.icon,
            'description': self.description,
            'is_deleted': self.is_deleted,
            'delete_time': format_datetime_to_string(self.delete_time) if self.delete_time else None,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time),
            # 'children': [child.dict() for child in self.children if not child.is_deleted]
        }
    
    @classmethod
    def add_category(cls, project_id, name, parent_id=None, icon=None, description=None):
        """
        创建目录
        :param project_id: 项目ID（UUID字符串）
        :param name: 目录名
        :param parent_id: 父目录ID（可选）
        :return: (category, error_msg)
        """
        # 检查父目录是否存在（且属于同一项目、未删除）
        # if parent_id is not None:
        #     parent = cls.query.filter_by(
        #         id=parent_id,
        #         project_id=project_id,
        #         is_deleted=False
        #     ).first()
        #     if not parent:
        #         return None, "父目录不存在或不属于当前项目"

        # 防止目录名重复（在同一项目+同一父级下）
        existing = cls.query.filter_by(
            project_id=project_id,
            parent_id=parent_id,
            name=name,
            is_deleted=False
        ).first()
        if existing:
            return None, "同级目录下已存在相同名称"
        try:
            category = cls(
                project_id=project_id,
                name=name,
                parent_id=parent_id,
                icon=icon,
                description=description
            )
            db.session.add(category)
            db.session.commit()
            return category, "创建成功"
        except Exception as e:
            db.session.rollback()
            return None, f"创建失败: {str(e)}"

    @classmethod
    def get_category_by_id(cls, category_id, include_deleted=False):
        """根据ID获取目录"""
        query = cls.query.filter_by(id=category_id)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.first()

    @classmethod
    def list_by_project_parent(cls, project_id, parent_id=None, include_deleted=False):
        """
        获取某项目下的某一层的目录列表
        :param project_id: 项目ID
        :param parent_id: 父ID（None 表示只查一级目录）
        :param include_deleted: 是否包含已删除
        """
        query = cls.query.filter_by(project_id=project_id)
        if parent_id is not None:
            query = query.filter_by(parent_id=parent_id)
        else:
            # 一级目录：parent_id IS NULL
            query = query.filter(cls.parent_id.is_(None))

        if not include_deleted:
            query = query.filter_by(is_deleted=False)

        return query.order_by(cls.create_time.asc()).all()

    def update_category(self, name=None, parent_id=None, icon=None, description=None):
        """
        更新目录信息
        :return: (success: bool, error_msg: str)
        """
        if name is not None:
            # 检查同级下是否重名
            existing = Category.query.filter(
                Category.project_id == self.project_id,
                Category.parent_id == (parent_id if parent_id is not None else self.parent_id),
                Category.name == name,
                Category.id != self.id,
                Category.is_deleted == False
            ).first()
            if existing:
                return False, "同级目录下已存在相同名称"

        # 如果要更新 parent_id，需验证新父目录有效性
        if parent_id is not None and parent_id != self.parent_id:
            parent = Category.query.filter_by(
                id=parent_id,
                project_id=self.project_id,
                is_deleted=False
            ).first()
            if not parent:
                return False, "父目录不存在或不属于当前项目"
            # 防止循环引用（简单检查：不能把祖先设为子）
            if self._would_cause_cycle(parent_id):
                return False, "不能将目录移动到其子目录下"

        # 执行更新
        if name is not None: self.name = name
        if parent_id is not None: self.parent_id = parent_id
        if icon is not None: self.icon = icon
        if description is not None: self.description = description

        try:
            db.session.commit()
            return True, self
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def _would_cause_cycle(self, new_parent_id):
        """
        简单检测是否会导致父子循环（递归向上查），
        new_parent_id 为新的父目录ID，以下为检测 new_parent_id 是否在当前目录的祖先路径中
        """
        current = new_parent_id
        visited = set()
        while current is not None:
            if current == self.id:
                return True
            if current in visited:  # 防止无限循环（理论上不会）
                break
            visited.add(current)
            parent = Category.query.get(current)
            current = parent.parent_id if parent else None
        return False

    def soft_delete(self):
        """
        软删除目录（及其所有子目录）
        """
        try:
            # 递归标记子目录为删除
            def _delete_recursive(cat):
                cat.is_deleted = True
                cat.delete_time = datetime.now()
                for article in cat.articles:
                    article.soft_delete_article()
                for child in cat.children:
                    _delete_recursive(child)

            _delete_recursive(self)
            db.session.commit()
            return True, self
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @classmethod
    def soft_delete_by_project_id(cls, project_id):
        """
        根据项目ID软删除项目下所有目录（及其所有子目录）
        """
        all_categories = cls.query.filter_by(project_id=project_id).all()
        for category in all_categories:
            category.soft_delete()
        return True, "删除成功"

    @classmethod
    def get_all_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id, is_deleted=False).all()

    @classmethod
    def get_tree(cls, project_id):
        """
        获取项目下的完整目录树（仅未删除的）
        返回嵌套 dict 列表，适合前端渲染
        """
        # 获取所有未删除目录
        all_categories = cls.query.filter_by(
            project_id=project_id,
            is_deleted=False
        ).order_by(cls.create_time.asc()).all()

        # 构建 ID -> 对象 映射
        cat_map = {cat.id: cat for cat in all_categories}
        tree = []

        for cat in all_categories:
            if cat.parent_id is None:
                tree.append(cat._to_tree_node(cat_map))
            else:
                parent = cat_map.get(cat.parent_id)
                if parent:
                    if not hasattr(parent, '_children_list'):
                        parent._children_list = []
                    parent._children_list.append(cat._to_tree_node(cat_map))

        # 清理临时属性
        def _clean(obj):
            if hasattr(obj, '_children_list'):
                obj['children'] = obj.pop('_children_list')
                for child in obj['children']:
                    _clean(child)
            return obj

        result = []
        for cat in all_categories:
            if cat.parent_id is None:
                node = cat.dict()
                # 计算完整路径
                node['full_path'] = cat._get_full_path(cat_map)
                if hasattr(cat, '_children_list'):
                    node['children'] = cat._children_list
                result.append(_clean(node))

        return result

    def _get_full_path(self, cat_map):
        """获取从根目录到当前目录的完整路径"""
        path_parts = []
        current = self
        
        while current is not None:
            path_parts.insert(0, current.name)  # 从根开始添加
            if current.parent_id is not None:
                current = cat_map.get(current.parent_id)
            else:
                current = None
        
        return '/'.join(path_parts)

    def _to_tree_node(self, cat_map):
        """辅助：生成树节点（包含递归子节点）"""
        node = self.dict()
        # 添加完整路径信息
        node['full_path'] = self._get_full_path(cat_map)
        children = [
            child._to_tree_node(cat_map)
            for child in self.children
            if not child.is_deleted and child.id in cat_map
        ]
        if children:
            node['children'] = children
        return node
