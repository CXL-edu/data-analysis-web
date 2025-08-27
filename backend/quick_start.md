# 🚀 快速启动指南

## 最简单的启动方式（使用SQLite）

```bash
# 1. 进入后端目录
cd F:\project\Web\fumadocs\backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库（使用默认SQLite）
python init_database.py

# 4. 启动服务器
python run.py
```

## 💡 启动成功提示

启动成功后，您将看到类似输出：

```
============================================================
🗄️ AI Data Assistant - Database Initialization
============================================================
📊 Configuration: development
🔗 Database URI: sqlite:///app.db

🏗️ Creating database tables...
✅ Tables created successfully

📋 Created tables:
  - users
  - sessions
  - uploaded_files
  - chat_messages
  - analysis_results

👤 Creating test user...
✅ Test user created:
   Email: test@example.com
   Password: testpass123
   Username: testuser

============================================================
🚀 AI Data Analysis Assistant - Backend Server
============================================================
📊 Configuration: development
🌐 Server URL: http://localhost:5000
📡 API Base: http://localhost:5000/api/v1
📖 API Docs: http://localhost:5000/api/docs/
```

## 🧪 测试API

### 1. 访问API文档
打开浏览器访问: http://localhost:5000/api/docs/

### 2. 测试用户登录
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

### 3. 创建会话
```bash
# 使用上面返回的token
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"title": "我的第一个会话"}'
```

## ❗ 常见问题

### 文件未找到错误
```
python: can't open file 'init_database.py'
```
**解决**: 确保在 `F:\project\Web\fumadocs\backend` 目录下运行命令

### 依赖包缺失
```
ModuleNotFoundError: No module named 'flask'
```
**解决**: 运行 `pip install -r requirements.txt`

### 端口占用
```
Address already in use
```
**解决**: 更改端口或停止占用5000端口的程序

## 🔄 重置数据库

如果需要重置数据库（删除所有数据）：

```bash
# 删除数据库文件
del app.db

# 重新初始化
python init_database.py
```

## 🎯 下一步

- 查看 `IMPLEMENTATION_GUIDE.md` 了解详细功能
- 查看 `POSTGRESQL_SETUP_GUIDE.md` 配置PostgreSQL
- 查看 `FRONTEND_INTEGRATION_GUIDE.md` 集成前端