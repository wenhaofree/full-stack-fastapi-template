# 🚀 部署指南

## 📋 目录
- [部署概览](#部署概览)
- [环境准备](#环境准备)
- [Docker 部署](#docker-部署)
- [传统部署](#传统部署)
- [生产环境配置](#生产环境配置)
- [监控与维护](#监控与维护)
- [故障排除](#故障排除)

## 🌐 部署概览

### 支持的部署方式
- **Docker Compose** (推荐)
- **Docker 单容器**
- **传统服务器部署**
- **云平台部署** (AWS, GCP, Azure)

### 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   FastAPI App   │    │   PostgreSQL    │
│    (Nginx)      │───▶│   (Uvicorn)     │───▶│    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 环境准备

### 生产环境要求
- **CPU**: 2+ 核心
- **内存**: 4GB+ RAM
- **存储**: 20GB+ 可用空间
- **网络**: 稳定的互联网连接
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Docker

### 必需软件
- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0
- **Git**: 版本控制
- **Nginx**: 反向代理 (可选)

## 🐳 Docker 部署

### 1. 使用 Docker Compose (推荐)

#### 1.1 准备配置文件

```bash
# 克隆项目
git clone <repository-url>
cd full-stack-fastapi-template

# 复制环境配置
cp .env.example .env
```

#### 1.2 配置生产环境变量

```bash
# 编辑 .env 文件
vim .env
```

**关键生产配置:**
```bash
# 环境设置
ENVIRONMENT=production

# 安全配置
SECRET_KEY=your-super-secret-key-here-change-this
FIRST_SUPERUSER_PASSWORD=secure-admin-password

# 数据库配置
POSTGRES_SERVER=db
POSTGRES_DB=fastapi_prod
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=secure-db-password

# 域名配置
DOMAIN=yourdomain.com
FRONTEND_HOST=https://yourdomain.com

# 日志配置
LOG_LEVEL=INFO
LOG_REQUEST_DETAILS=false
LOG_FUNCTION_PARAMS=false
```

#### 1.3 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 2. 单独 Docker 部署

#### 2.1 构建镜像

```bash
cd backend

# 构建生产镜像
docker build -t fastapi-backend:latest .
```

#### 2.2 运行容器

```bash
# 启动 PostgreSQL
docker run -d \
  --name postgres-prod \
  -e POSTGRES_DB=fastapi_prod \
  -e POSTGRES_USER=fastapi_user \
  -e POSTGRES_PASSWORD=secure-password \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15

# 启动 FastAPI 应用
docker run -d \
  --name fastapi-backend \
  --link postgres-prod:db \
  -e POSTGRES_SERVER=db \
  -e POSTGRES_DB=fastapi_prod \
  -e POSTGRES_USER=fastapi_user \
  -e POSTGRES_PASSWORD=secure-password \
  -e SECRET_KEY=your-secret-key \
  -p 8000:8000 \
  fastapi-backend:latest
```

## 🖥️ 传统部署

### 1. 系统准备

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv postgresql nginx

# CentOS/RHEL
sudo yum update
sudo yum install python310 postgresql-server nginx
```

### 2. 应用部署

```bash
# 创建应用用户
sudo useradd -m -s /bin/bash fastapi
sudo su - fastapi

# 克隆代码
git clone <repository-url> /home/fastapi/app
cd /home/fastapi/app/backend

# 安装依赖
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e .

# 配置环境变量
cp ../.env.example ../.env
vim ../.env
```

### 3. 数据库设置

```bash
# 初始化 PostgreSQL
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE fastapi_prod;
CREATE USER fastapi_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE fastapi_prod TO fastapi_user;
\q
```

### 4. 应用初始化

```bash
# 运行数据库迁移
alembic upgrade head

# 创建初始数据
python app/initial_data.py
```

### 5. 系统服务配置

#### 5.1 创建 systemd 服务

```bash
sudo vim /etc/systemd/system/fastapi.service
```

```ini
[Unit]
Description=FastAPI application
After=network.target

[Service]
Type=exec
User=fastapi
Group=fastapi
WorkingDirectory=/home/fastapi/app/backend
Environment=PATH=/home/fastapi/app/backend/.venv/bin
ExecStart=/home/fastapi/app/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 5.2 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl start fastapi
sudo systemctl enable fastapi
sudo systemctl status fastapi
```

### 6. Nginx 配置

```bash
sudo vim /etc/nginx/sites-available/fastapi
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 生产环境配置

### 1. 安全配置

#### 1.1 SSL/TLS 证书

```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

#### 1.2 防火墙配置

```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. 性能优化

#### 2.1 Uvicorn 配置

```bash
# 多进程启动
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker
```

#### 2.2 数据库优化

```sql
-- PostgreSQL 配置优化
-- /etc/postgresql/15/main/postgresql.conf

shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 3. 监控配置

#### 3.1 日志轮转

```bash
sudo vim /etc/logrotate.d/fastapi
```

```
/home/fastapi/app/backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 fastapi fastapi
    postrotate
        systemctl reload fastapi
    endscript
}
```

#### 3.2 健康检查

```bash
# 创建健康检查脚本
vim /home/fastapi/health_check.sh
```

```bash
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/utils/health-check)
if [ $response -eq 200 ]; then
    echo "Service is healthy"
    exit 0
else
    echo "Service is unhealthy"
    exit 1
fi
```

## 📊 监控与维护

### 1. 日志监控

```bash
# 查看应用日志
tail -f /home/fastapi/app/backend/logs/app.log

# 查看系统服务日志
sudo journalctl -u fastapi -f

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. 性能监控

```bash
# 系统资源监控
htop
iostat -x 1
free -h

# 数据库监控
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

### 3. 备份策略

```bash
# 数据库备份脚本
#!/bin/bash
BACKUP_DIR="/backup/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U fastapi_user fastapi_prod > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

## 🔧 故障排除

### 常见问题

#### 1. 服务无法启动

```bash
# 检查服务状态
sudo systemctl status fastapi

# 查看详细日志
sudo journalctl -u fastapi -n 50

# 检查端口占用
sudo netstat -tlnp | grep :8000
```

#### 2. 数据库连接失败

```bash
# 测试数据库连接
python -c "from app.core.db import engine; print(engine.url)"

# 检查 PostgreSQL 状态
sudo systemctl status postgresql
```

#### 3. 内存不足

```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 重启服务释放内存
sudo systemctl restart fastapi
```

### 紧急恢复

```bash
# 快速重启所有服务
sudo systemctl restart postgresql
sudo systemctl restart fastapi
sudo systemctl restart nginx

# 从备份恢复数据库
pg_restore -h localhost -U fastapi_user -d fastapi_prod backup_file.sql
```

---

**🎉 部署完成！访问 https://yourdomain.com/docs 查看 API 文档**
