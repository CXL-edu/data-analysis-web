# AI Data Assistant Backend - Implementation Guide

## 📋 概述

本项目是一个基于Flask的AI数据分析助手后端，实现了完整的用户认证、会话管理、文件上传和数据分析功能。项目采用模块化架构，分离了数据库操作、业务逻辑和API层。

## 🏗️ 架构设计

### 项目结构

```
backend/
├── app/                          # 应用核心
│   ├── __init__.py              # 应用工厂
│   ├── config.py                # 配置文件
│   ├── extensions.py            # Flask扩展初始化
│   ├── api/                     # API层
│   │   ├── v1/                  # API v1版本
│   │   │   ├── auth.py          # 认证端点
│   │   │   ├── sessions.py      # 会话管理端点
│   │   │   ├── files.py         # 文件管理端点
│   │   │   ├── chat.py          # 聊天端点
│   │   │   └── analysis.py      # 分析端点
│   │   └── schemas/             # 请求/响应模式
│   ├── services/                # 业务服务层
│   │   ├── auth_service.py      # 认证服务
│   │   ├── session_service.py   # 会话服务
│   │   ├── file_service.py      # 文件服务
│   │   ├── chat_service.py      # 聊天服务
│   │   └── analysis_service.py  # 分析服务
│   └── utils/                   # 工具模块
│       ├── decorators.py        # 装饰器
│       └── exceptions.py        # 异常处理
├── database/                    # 数据库层
│   ├── models/                  # 数据模型
│   │   ├── user.py             # 用户模型
│   │   ├── session.py          # 会话模型
│   │   ├── file.py             # 文件模型
│   │   ├── message.py          # 消息模型
│   │   └── analysis.py         # 分析结果模型
│   └── repositories/           # 数据访问层
│       ├── user_repository.py   # 用户数据访问
│       └── ...                 # 其他仓库类
├── storage/                    # 文件存储
│   └── uploads/                # 上传文件目录
├── init_database.py           # 数据库初始化脚本
├── run.py                     # 应用入口
└── requirements.txt           # 依赖包
```

### 核心技术栈

- **Web框架**: Flask + Flask-RESTX
- **数据库**: PostgreSQL + SQLAlchemy ORM
- **认证**: JWT (Flask-JWT-Extended)
- **邮件**: Flask-Mail
- **数据分析**: Pandas + NumPy
- **API文档**: Flask-RESTX (Swagger UI)

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 复制环境变量配置文件
copy .env.example .env
# 或者在Linux/macOS: cp .env.example .env

# 编辑 .env 文件，填入实际配置值
# 详细的数据库配置请参考 POSTGRESQL_SETUP_GUIDE.md
```

#### .env 文件配置示例

```env
# 开发环境配置
FLASK_CONFIG=development
SECRET_KEY=your-very-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# 数据库配置 (选择其一)
# SQLite (开发环境推荐)
# DATABASE_URL=sqlite:///app.db

# PostgreSQL (生产环境推荐)
DATABASE_URL=postgresql://username:password@localhost:5432/fumadocs_ai

# 邮件配置 (用于邮箱验证)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 2. 数据库配置和初始化

#### 使用SQLite（快速开始）
```bash
# 直接初始化SQLite数据库（无需额外配置）
python init_database.py

# 创建测试用户（开发模式）
python init_database.py test-user
```

#### 使用PostgreSQL（推荐生产环境）
```bash
# 1. 首先按照 POSTGRESQL_SETUP_GUIDE.md 安装和配置PostgreSQL
# 2. 在 .env 文件中配置PostgreSQL连接
# 3. 初始化数据库表
python init_database.py
```

> 📖 **详细的PostgreSQL配置指南**: 请查看 [`POSTGRESQL_SETUP_GUIDE.md`](./POSTGRESQL_SETUP_GUIDE.md) 文件，包含完整的安装、配置和优化说明。

### 3. 启动服务

```bash
# 启动开发服务器
python run.py
```

服务启动后访问：
- API文档: http://localhost:5000/api/docs/
- API基础路径: http://localhost:5000/api/v1/

## 📚 API接口文档

### 认证接口

#### 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

#### 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}
```

响应:
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_email_verified": true
  }
}
```

#### 获取用户信息
```http
GET /api/v1/auth/profile
Authorization: Bearer <access_token>
```

### 会话管理接口

#### 获取用户会话列表
```http
GET /api/v1/sessions
Authorization: Bearer <access_token>
```

#### 创建新会话
```http
POST /api/v1/sessions
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "数据分析会话"
}
```

#### 获取会话详情
```http
GET /api/v1/sessions/{session_uuid}
Authorization: Bearer <access_token>
```

### 文件管理接口

#### 上传文件到会话
```http
POST /api/v1/files/upload/{session_uuid}
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file=@data.csv
```

#### 获取文件预览
```http
GET /api/v1/files/{file_id}/preview
Authorization: Bearer <access_token>
```

### 聊天接口

#### 流式聊天
```http
POST /api/v1/chat/{session_uuid}/stream
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "请分析一下数据的基本统计信息"
}
```

响应为Server-Sent Events流:
```
data: {"type": "user_message", "message": {...}}
data: {"type": "ai_chunk", "chunk": "正在分析数据..."}
data: {"type": "ai_complete", "message": {...}}
data: [DONE]
```

### 数据分析接口

#### 执行数据分析
```http
POST /api/v1/analysis/{session_uuid}/analyze
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "analysis_type": "descriptive_stats",
  "file_ids": [1, 2],
  "parameters": {}
}
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|-------|------|--------|
| FLASK_CONFIG | 运行环境 | development |
| SECRET_KEY | Flask密钥 | - |
| JWT_SECRET_KEY | JWT密钥 | - |
| DATABASE_URL | 数据库连接 | sqlite:///app.db |
| MAIL_SERVER | 邮件服务器 | localhost |
| MAIL_USERNAME | 邮件用户名 | - |
| MAIL_PASSWORD | 邮件密码 | - |
| UPLOAD_FOLDER | 文件上传目录 | storage/uploads |

### 配置类

```python
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/dev_db'
    
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

## 🛠️ 开发指南

### 添加新的API端点

1. 在 `app/api/v1/` 创建新的模块
2. 定义Flask-RESTX资源类
3. 在 `app/api/v1/__init__.py` 注册命名空间

```python
# app/api/v1/new_feature.py
from flask_restx import Namespace, Resource

feature_ns = Namespace('feature', description='New feature operations')

@feature_ns.route('/')
class FeatureResource(Resource):
    def get(self):
        return {'message': 'Hello from new feature'}
```

### 添加新的服务层

1. 在 `app/services/` 创建服务类
2. 实现业务逻辑方法
3. 在API层调用服务

```python
# app/services/new_service.py
class NewService:
    def __init__(self):
        pass
    
    def process_data(self, data):
        # 业务逻辑处理
        return processed_data
```

### 添加数据模型

1. 在 `database/models/` 创建模型类
2. 在 `database/repositories/` 创建仓库类
3. 运行数据库迁移

```python
# database/models/new_model.py
from database.models.base import BaseModel
from app.extensions import db

class NewModel(BaseModel):
    __tablename__ = 'new_models'
    
    name = db.Column(db.String(100), nullable=False)
```

## 🧪 测试

### 单元测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_api.py
```

### API测试

使用提供的测试脚本：

```bash
# 测试完整流程
python test_full_flow.py

# 测试流式响应
python test_streaming.py
```

## 📦 部署

### Docker部署（可选）

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

### 生产环境配置

1. 设置环境变量 `FLASK_CONFIG=production`
2. 配置PostgreSQL数据库
3. 设置邮件服务器
4. 配置反向代理（Nginx）
5. 使用WSGI服务器（Gunicorn）

```bash
# 使用Gunicorn启动
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

## 🔍 故障排除

### 常见问题

1. **数据库连接错误**
   - 检查DATABASE_URL环境变量
   - 确认PostgreSQL服务运行
   - 验证数据库权限

2. **JWT令牌错误**
   - 检查JWT_SECRET_KEY环境变量
   - 验证令牌格式和有效期

3. **文件上传失败**
   - 检查上传目录权限
   - 验证文件大小限制
   - 确认支持的文件格式

4. **邮件发送失败**
   - 检查邮件服务器配置
   - 验证SMTP设置
   - 确认邮件账户权限

### 日志查看

```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 在代码中使用
current_app.logger.info("Info message")
current_app.logger.error("Error message")
```

## 📈 性能优化

### 数据库优化
- 添加适当的索引
- 使用连接池
- 优化查询语句

### 缓存策略
- Redis缓存热点数据
- 文件级缓存
- API响应缓存

### 异步处理
- Celery任务队列
- 后台数据处理
- 邮件异步发送

## 🔒 安全考虑

### 认证安全
- JWT令牌过期时间
- 刷新令牌机制
- 密码加密存储

### API安全
- 请求速率限制
- 输入数据验证
- CORS配置

### 数据安全
- 敏感数据加密
- 文件访问控制
- 数据备份策略

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。