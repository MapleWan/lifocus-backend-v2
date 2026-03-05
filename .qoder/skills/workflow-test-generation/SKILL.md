---
name: workflow-test-generation
description: 基于 spec.md 或被测代码生成单元测试、集成测试、性能测试。当用户请求生成测试、采用 TDD 模式、或代码生成完成后需要补充测试时使用。
---

# 测试生成

## 触发条件

- 用户请求生成测试
- TDD 模式：设计完成后，编码前
- `workflow-code-generation` 完成后，用户选择编写测试

## 工作流程

### Step 0: 检查 spec.md

尝试读取 `docs/design-docs/<module>/<feature>/spec.md`：

**有 spec.md**：
1. 读取 "7. 测试计划"
2. 测试计划明确 → 直接生成测试
3. 测试计划不完整 → 补充读取 "2. 目标"、"3. 需求"、"4. 设计方案"，自行判断

**无 spec.md**（为已有代码补测试）：

```json
{
  "questions": [{
    "id": "no_spec_action",
    "question": "未找到 spec.md，请选择：",
    "options": [
      "先澄清需求生成 spec.md（推荐）",
      "直接告诉我要测试什么（快速）"
    ],
    "multiSelect": false
  }]
}
```

- 选择 "先澄清需求" → 调用 `workflow-requirements-clarification` skill
- 选择 "直接测试" → 询问要测哪些函数/类，基于代码生成

### Step 1: 确定测试类型

根据代码特征自动判断，**无法判断时才询问**：

| 特征 | 测试类型 |
|------|----------|
| 纯函数、无外部依赖 | 单元测试 |
| 涉及数据库操作、API 调用 | 集成测试 |
| spec.md 有性能指标要求 | 性能测试 |

### Step 2: 分析被测代码

- 识别公共接口（只测公共方法）
- 识别输入、输出、副作用
- 识别依赖（需要 mock 的部分）

### Step 3: 应用边界条件

**必须参考** [reference/boundary-checklist.md](reference/boundary-checklist.md)，选择适用的边界条件。

### Step 4: 制定测试计划

列出要测试的函数/类及对应场景，使用 `todo_write` 创建测试任务清单：

```
示例：
1. [pending] test_user_login_success - 正常路径
2. [pending] test_user_login_invalid_password - 异常场景
3. [pending] test_user_login_boundary_username - 边界条件
4. [pending] test_create_article_integration - 集成测试
```

**与用户确认**测试计划后再开始生成。

### Step 5: 逐个生成测试

按 todo 逐个生成，每个测试包含三类场景：
1. **正常路径** - happy path
2. **边界条件** - 基于 checklist
3. **异常场景** - 错误输入、异常处理

每完成一个，标记 `[completed]`，运行验证后继续下一个。

---

## 单元测试

### FIRST 原则

| 原则 | 检查点 |
|------|--------|
| **Fast** | 无真实 I/O、网络、数据库 |
| **Independent** | 无共享可变状态 |
| **Repeatable** | 无真实时间、随机数 |
| **Self-Validating** | 明确 Pass/Fail |
| **Timely** | TDD 或与代码同步 |

### AAA 结构

```python
def test_user_login_success(client):
    # Arrange: 准备输入和 mock
    login_data = {'username': 'testuser', 'password': 'correctpass'}
    
    # Act: 执行被测方法（单次调用）
    response = client.post('/api/auth/login', json=login_data)
    
    # Assert: 验证输出/状态
    assert response.status_code == 200
    assert response.json['code'] == 200
    assert 'access_token' in response.json['data']
```

---

## 性能测试

| 原则 | 说明 |
|------|------|
| **基线对比** | 与历史数据对比 |
| **可复现** | 固定数据集、配置 |
| **预热** | 排除冷启动影响 |
| **多次运行** | 取 P99，避免抖动 |

---

## Mock 原则

| 原则 | 说明 |
|------|------|
| **只 mock 架构边界** | 网络、数据库、文件系统 |
| **不 mock 内部协作者** | 避免测试实现细节 |
| **优先使用 Fake** | 内存实现 > 复杂 mock |

**检验标准**：重构内部实现时，测试不应失败。

---

## 反模式

| 反模式 | 正确做法 |
|--------|----------|
| 测试实现细节 | 测试行为/契约 |
| 测试中有 if/for | 测试应线性简单 |
| time.sleep 等待 | 用 pytest 的 freeze_time |
| 共享可变状态 | 每个测试独立 setup，使用 fixture |
| 弱断言（assert is not None） | 断言具体值 |
| 直接操作数据库 | 使用测试客户端或 mock |

---

## 模块专项参考

| 测试类型 | 参考资料 |
|----------|----------|
| **边界条件** | [reference/boundary-checklist.md](reference/boundary-checklist.md) |

---

## Flask 测试规范

### 测试结构

```
tests/
├── conftest.py          # 共享 fixture
├── unit/                # 单元测试
│   ├── test_models.py
│   └── test_utils.py
├── integration/         # 集成测试
│   ├── test_auth_api.py
│   └── test_article_api.py
└── fixtures/            # 测试数据
    └── users.json
```

### 常用 Fixture 示例

```python
# conftest.py
import pytest
from app import create_app
from app.extension import db

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """获取认证 headers"""
    resp = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    token = resp.json['data']['access_token']
    return {'Authorization': f'Bearer {token}'}
```

### 数据库测试

```python
def test_user_model_save(app):
    """测试模型保存"""
    with app.app_context():
        user = User(username='test', email='test@example.com')
        db.session.add(user)
        db.session.commit()
        
        saved = User.query.filter_by(username='test').first()
        assert saved is not None
        assert saved.email == 'test@example.com'
```

### API 测试

```python
def test_login_api(client):
    """测试登录接口"""
    # 正常路径
    resp = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'correct'
    })
    assert resp.status_code == 200
    assert resp.json['code'] == 200
    
    # 边界条件：缺少参数
    resp = client.post('/api/auth/login', json={})
    assert resp.status_code == 400
    
    # 异常场景：密码错误
    resp = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'wrong'
    })
    assert resp.status_code == 400
```

---

## 强制规则

1. **必须覆盖三类场景**：正常路径 + 边界条件 + 异常场景
2. **必须应用边界条件 checklist**
3. **必须可运行**：`pytest tests/` 通过
4. **单元测试遵循 FIRST + AAA**
5. **禁止测试私有方法**（以 `_` 开头的方法）
6. **禁止 time.sleep**，使用 `freezegun` 冻结时间
7. **数据库测试必须清理**：使用 fixture 或 `db.session.rollback()`
