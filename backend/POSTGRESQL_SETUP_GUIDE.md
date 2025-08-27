# PostgreSQL 数据库配置指南

## 📋 概述

本指南详细说明如何为AI数据分析助手项目配置PostgreSQL数据库，包括安装、配置和连接设置。

## 🛠️ PostgreSQL 安装

### Windows 安装

#### 1. 下载PostgreSQL
- 访问 [PostgreSQL官网](https://www.postgresql.org/download/windows/)
- 下载Windows安装程序（推荐最新稳定版本）
- 或者使用包管理器：`winget install PostgreSQL.PostgreSQL`

#### 2. 安装过程
1. **运行安装程序**
2. **选择安装目录** (默认: `C:\Program Files\PostgreSQL\15\`)
3. **选择组件** (默认全选即可)
4. **设置数据目录** (默认: `C:\Program Files\PostgreSQL\15\data`)
5. **设置超级用户密码** (记住这个密码！)
6. **设置端口** (默认: 5432)
7. **选择区域设置** (默认: [Default locale])
8. **完成安装**

#### 3. 验证安装
```cmd
# 检查PostgreSQL服务状态
sc query postgresql-x64-15

# 或者在服务管理器中查看PostgreSQL服务
```

### macOS 安装

```bash
# 使用Homebrew安装
brew install postgresql@15

# 启动服务
brew services start postgresql@15
```

### Linux (Ubuntu/Debian) 安装

```bash
# 更新包索引
sudo apt update

# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 启动PostgreSQL服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## 🗄️ 数据库设置

### 1. 连接到PostgreSQL

#### Windows
```cmd
# 使用pgAdmin GUI工具 (推荐)
# 或者使用命令行
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

#### macOS/Linux
```bash
# 切换到postgres用户并连接
sudo -u postgres psql
```

### 2. 创建项目数据库

```sql
-- 创建数据库用户
CREATE USER fumadocs_user WITH PASSWORD 'your_secure_password';

-- 创建数据库
CREATE DATABASE fumadocs_ai OWNER fumadocs_user;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE fumadocs_ai TO fumadocs_user;

-- 退出psql
\q
```

### 3. 测试连接

```bash
# 测试新用户连接
psql -h localhost -U fumadocs_user -d fumadocs_ai

# 如果成功，你将看到数据库提示符
fumadocs_ai=>
```

## ⚙️ 项目配置

### 1. 复制环境变量文件

```bash
cd F:\project\Web\fumadocs\backend
copy .env.example .env
```

### 2. 编辑 .env 文件

打开 `.env` 文件，找到数据库配置部分：

```env
# ==============================================
# 数据库配置
# ==============================================
# 开发环境 - SQLite (默认，注释掉以使用PostgreSQL)
# DATABASE_URL=sqlite:///app.db

# 生产环境 - PostgreSQL (取消注释并填入实际值)
DATABASE_URL=postgresql://fumadocs_user:your_secure_password@localhost:5432/fumadocs_ai

# 如果使用默认postgres用户
# DATABASE_URL=postgresql://postgres:your_password@localhost:5432/fumadocs_ai
```

### 3. 安装Python PostgreSQL驱动

```bash
# 确保安装了PostgreSQL驱动
pip install psycopg2-binary
```

### 4. 初始化数据库表

```bash
# 初始化数据库
python init_database.py

# 输出应该显示PostgreSQL连接信息
```

## 🔧 连接字符串格式

### 标准格式
```
postgresql://username:password@host:port/database
```

### 示例连接字符串

```bash
# 本地开发环境
DATABASE_URL=postgresql://fumadocs_user:mypassword@localhost:5432/fumadocs_ai

# 本地开发环境使用默认postgres用户
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/fumadocs_ai

# 生产环境示例
DATABASE_URL=postgresql://user:pass@db.example.com:5432/production_db

# 云服务示例 (如Heroku Postgres)
DATABASE_URL=postgresql://username:password@hostname:5432/database?sslmode=require
```

## 🛡️ 安全配置

### 1. 用户权限管理

```sql
-- 连接到PostgreSQL作为超级用户
psql -U postgres

-- 创建只读用户（用于备份和监控）
CREATE USER fumadocs_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE fumadocs_ai TO fumadocs_readonly;
GRANT USAGE ON SCHEMA public TO fumadocs_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO fumadocs_readonly;

-- 创建限制权限的应用用户
CREATE USER fumadocs_app WITH PASSWORD 'app_password';
GRANT CONNECT ON DATABASE fumadocs_ai TO fumadocs_app;
GRANT USAGE, CREATE ON SCHEMA public TO fumadocs_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO fumadocs_app;
```

### 2. 连接限制配置

编辑 `postgresql.conf` 文件：

```conf
# 连接设置
max_connections = 100
shared_buffers = 256MB

# 日志设置
log_statement = 'mod'
log_duration = on

# 安全设置
ssl = on
```

### 3. 认证配置

编辑 `pg_hba.conf` 文件：

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# 本地连接
local   all             postgres                                md5
local   fumadocs_ai     fumadocs_user                          md5

# IPv4本地连接
host    fumadocs_ai     fumadocs_user   127.0.0.1/32           md5
host    fumadocs_ai     fumadocs_user   localhost               md5
```

## 🔍 故障排除

### 常见问题及解决方案

#### 1. 连接被拒绝
```bash
psql: could not connect to server: Connection refused
```

**解决方案：**
- 检查PostgreSQL服务是否运行
- 验证端口5432是否开放
- 检查防火墙设置

```bash
# Windows检查服务
sc query postgresql-x64-15

# 启动服务
sc start postgresql-x64-15
```

#### 2. 认证失败
```bash
psql: FATAL: password authentication failed for user "fumadocs_user"
```

**解决方案：**
- 检查用户名和密码
- 验证用户是否存在
- 检查pg_hba.conf配置

```sql
-- 检查用户
SELECT usename FROM pg_user WHERE usename = 'fumadocs_user';

-- 重置密码
ALTER USER fumadocs_user WITH PASSWORD 'new_password';
```

#### 3. 数据库不存在
```bash
psql: FATAL: database "fumadocs_ai" does not exist
```

**解决方案：**
```sql
-- 列出所有数据库
\l

-- 创建数据库
CREATE DATABASE fumadocs_ai;
```

#### 4. Python连接错误
```python
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
```

**解决方案：**
- 安装psycopg2驱动：`pip install psycopg2-binary`
- 检查连接字符串格式
- 验证数据库服务运行状态

## 📊 性能优化

### 1. 基本优化设置

```sql
-- 连接到数据库
\c fumadocs_ai

-- 创建索引（数据库初始化后）
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_uuid ON sessions(uuid);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_session_id ON uploaded_files(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_session_id ON analysis_results(session_id);
```

### 2. 配置调优

```sql
-- 查看当前配置
SHOW all;

-- 常用性能参数
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';

-- 重新加载配置
SELECT pg_reload_conf();
```

## 🔄 备份和恢复

### 1. 创建备份

```bash
# 完整数据库备份
pg_dump -U fumadocs_user -h localhost fumadocs_ai > backup.sql

# 压缩备份
pg_dump -U fumadocs_user -h localhost fumadocs_ai | gzip > backup.sql.gz

# 仅数据备份
pg_dump -U fumadocs_user -h localhost --data-only fumadocs_ai > data_backup.sql
```

### 2. 恢复备份

```bash
# 恢复数据库
psql -U fumadocs_user -h localhost fumadocs_ai < backup.sql

# 从压缩文件恢复
gunzip -c backup.sql.gz | psql -U fumadocs_user -h localhost fumadocs_ai
```

## 🚀 生产环境配置

### 1. 安全清单

- [ ] 更改默认postgres用户密码
- [ ] 创建专用应用用户
- [ ] 配置SSL连接
- [ ] 设置防火墙规则
- [ ] 配置连接池
- [ ] 设置定期备份
- [ ] 监控数据库性能

### 2. 连接池配置

```python
# 在config.py中添加
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 30
}
```

### 3. 环境变量示例

```env
# 生产环境配置
FLASK_CONFIG=production
DATABASE_URL=postgresql://app_user:secure_password@localhost:5432/fumadocs_production
SECRET_KEY=your-very-secure-secret-key
JWT_SECRET_KEY=your-very-secure-jwt-key
```

## 📋 完整设置检查清单

### 安装阶段
- [ ] PostgreSQL服务安装完成
- [ ] 服务正常运行
- [ ] 可以连接到默认postgres用户

### 数据库配置
- [ ] 创建项目专用用户
- [ ] 创建项目数据库
- [ ] 授予适当权限
- [ ] 测试用户连接

### 项目集成
- [ ] 复制并配置.env文件
- [ ] 安装psycopg2驱动
- [ ] 测试应用连接
- [ ] 运行数据库初始化脚本
- [ ] 验证表创建成功

### 安全配置
- [ ] 更改默认密码
- [ ] 配置用户权限
- [ ] 设置连接限制
- [ ] 配置SSL（生产环境）

通过以上步骤，您的PostgreSQL数据库就配置完成了！🎉