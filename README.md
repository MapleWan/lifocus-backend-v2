# LiFocus Backend

LiFocus 后端服务 - 一个基于 Flask 的个人知识管理与内容创作平台。

## 项目介绍

### 项目功能

LiFocus 是一个功能完善的个人知识管理系统，主要包含以下功能模块：

- **用户认证系统**：JWT 令牌机制，支持用户注册、登录、登出和令牌刷新
- **项目管理**：创建和管理个人项目，支持项目分类和归档
- **目录管理**：层级化的目录结构，便于组织和管理内容
- **文章管理**：支持富文本文章创作、编辑、分享和归档
- **字典管理**：自定义字典数据，支持系统配置和枚举值管理
- **时间线管理**：记录项目或文章的重要时间节点

### 项目特点

- **RESTful API 设计**：遵循 RESTful 规范，接口清晰易用
- **JWT 认证**：基于 Token 的无状态认证机制，支持令牌黑名单
- **多数据库支持**：支持 MySQL 和 PostgreSQL 两种数据库
- **数据迁移**：使用 Alembic 进行数据库版本管理
- **Redis 缓存**：使用 Redis 存储 JWT 黑名单等临时数据
- **跨域支持**：内置 CORS 支持，方便前端对接
- **环境配置**：支持开发、生产等多环境配置
- **密码安全**：采用 PBKDF2 HMAC SHA256 加盐哈希存储密码

## 技术栈说明

### 后端框架

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.12 | 编程语言 |
| Flask | 3.1.1 | Web 框架 |
| Flask-SQLAlchemy | 3.1.1 | ORM 框架 |
| Flask-Migrate | 4.1.0 | 数据库迁移 |
| Flask-RESTful | 0.3.10 | REST API 扩展 |
| Flask-JWT-Extended | 4.7.1 | JWT 认证 |
| flask-cors | 6.0.1 | 跨域支持 |

### 数据库与缓存

| 技术 | 版本 | 说明 |
|------|------|------|
| SQLAlchemy | 2.0.41 | ORM 核心 |
| Alembic | 1.16.2 | 数据库迁移工具 |
| PyMySQL | 1.1.1 | MySQL 驱动 |
| Redis | 7.1.0 | 缓存数据库 |

### 其他依赖

| 技术 | 版本 | 说明 |
|------|------|------|
| python-dotenv | 1.1.1 | 环境变量管理 |
| cryptography | 45.0.4 | 加密库 |
| flasgger | 0.9.7.1 | API 文档生成 |

## 项目结构说明

```
lifocus-backend-v2/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── app.py                    # Flask 应用工厂
│   ├── config.py                 # 配置文件
│   ├── extension.py              # 扩展初始化
│   ├── config/                   # 配置模块
│   ├── controllers/              # 控制器（API 接口）
│   │   ├── article/              # 文章模块
│   │   ├── auth/                 # 认证模块
│   │   ├── category/             # 目录模块
│   │   ├── dict/                 # 字典模块
│   │   ├── project/              # 项目模块
│   │   ├── search/               # 搜索模块
│   │   ├── timeline/             # 时间线模块
│   │   └── user/                 # 用户模块
│   ├── enums/                    # 枚举定义
│   ├── models/                   # 数据模型
│   │   └── entities/             # 实体模型
│   └── utils/                    # 工具函数
├── migrations/                   # 数据库迁移文件
│   └── versions/                 # 迁移版本
├── docs/                         # 文档目录
├── .env.dev                      # 开发环境配置
├── .env.develop                  # 开发环境配置
├── .env.production               # 生产环境配置
├── requirements.txt              # 依赖列表
└── run.py                        # 应用入口
```

### 目录结构详解

- **app/controllers/**：按功能模块组织的 API 控制器，每个模块包含 API 模型定义和业务逻辑管理器
- **app/models/entities/**：SQLAlchemy 实体模型定义
- **app/enums/**：系统枚举类型定义
- **app/utils/**：通用工具函数（密码处理、字符串处理等）
- **migrations/**：Alembic 数据库迁移脚本

**文件组织**

- 每个模块独立目录，包含 `__init__.py`、API 模型、管理器
- 控制器放在 `controllers/` 目录下
- 模型放在 `models/entities/` 目录下
- 工具函数放在 `utils/` 目录下



## 快速开始

### 环境要求

- Python 3.8+
- MySQL 8.0+ 或 PostgreSQL 12+
- Redis 6.0+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制 `.env.develop` 为 `.env` 并根据实际情况修改配置：

```bash
cp .env.develop .env
```

### 初始化数据库

```bash
# 初始化迁移
flask -e .env.develop db init

# 创建迁移脚本
flask -e .env.develop db migrate -m '初始化数据库'

# 执行迁移
flask -e .env.develop db upgrade
```

### 启动服务

```bash
# 开发环境
flask -e .env.develop run

# 或使用 Python 直接运行
python run.py
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI：`http://127.0.0.1:5003/api/docs/`
