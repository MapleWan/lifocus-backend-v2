from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import user_ns
from app.models.entities.user import User
class UserResource(Resource):
    """
    根据用户 id 获取用户信息
    """
    @jwt_required()
    @user_ns.doc(description='根据用户ID获取用户信息')
    def get(self):
        current_user_id = get_jwt_identity()
        try:
            user = User.get_user_by_id(current_user_id)
            if not user:
                return {'code': 404, 'message': '用户不存在'}, 404
            return {'code': 200, 'message': '查询成功', 'data': user.dict()}, 200
        except Exception as e:
            return {'code': 500, 'message': str(e)}, 500

        