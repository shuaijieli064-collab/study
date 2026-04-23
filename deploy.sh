#!/bin/bash
# 智校通 - 阿里云ECS服务器部署脚本
# 适用于: Alibaba Cloud Linux 3.2104 LTS 64位
# 使用方法: bash deploy.sh

set -e

# 配置
APP_NAME="zhixiaotong"
APP_DIR="/var/www/zhixiaotong"
PYTHON_VERSION="3.10"
DOMAIN="${DOMAIN:-example.com}"
EMAIL="${EMAIL:-admin@example.com}"

echo "=========================================="
echo "智校通 - 阿里云服务器部署脚本"
echo "系统: Alibaba Cloud Linux 3.2104 LTS"
echo "=========================================="

# 1. 更新系统
echo "[1/8] 更新系统..."
dnf update -y

# 2. 安装Python和依赖
echo "[2/8] 安装Python环境..."
dnf install -y python3 python3-pip python3-venv

# 3. 安装 Nginx 和 Certbot
echo "[3/8] 安装Nginx和SSL证书工具..."
dnf install -y nginx certbot python3-certbot-nginx

# 4. 创建应用目录
echo "[4/8] 创建应用目录..."
mkdir -p $APP_DIR
cp -r backend frontend data $APP_DIR/ 2>/dev/null || true

# 5. 创建虚拟环境
echo "[5/8] 创建虚拟环境..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 6. 配置环境变量
echo "[6/8] 配置环境变量..."
cat > $APP_DIR/.env << 'EOF'
AI_API_KEY=sk-c74edeb3cb8044b59931115d523d873e
AI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-plus
AI_TIMEOUT_SECONDS=120
DEBUG=false
EOF

# 7. 配置systemd服务
echo "[7/8] 配置系统服务..."
cat > /etc/systemd/system/zhixiaotong.service << EOF
[Unit]
Description=Zhixiaotong Flask App
After=network.target

[Service]
User=nginx
Group=nginx
WorkingDirectory=$APP_DIR/backend
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 8. 配置Nginx
echo "[8/8] 配置Nginx..."
cat > /etc/nginx/conf.d/zhixiaotong.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 16M;

    location / {
        root $APP_DIR/frontend;
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
EOF

# 启动服务
echo ""
echo "启动服务..."
systemctl daemon-reload
systemctl enable nginx zhixiaotong
systemctl start nginx
systemctl restart zhixiaotong

# 检查状态
sleep 2
systemctl status zhixiaotong --no-pager

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "访问地址: http://你的服务器IP"
echo ""
echo "后续步骤:"
echo "1. 在阿里云控制台开放端口: 80, 443"
echo "2. 购买域名并配置DNS解析"
echo "3. 申请SSL证书: certbot --nginx -d 你的域名"
echo ""
echo "管理命令:"
echo "  查看状态: systemctl status zhixiaotong"
echo "  重启服务: systemctl restart zhixiaotong"
echo "  查看日志: journalctl -u zhixiaotong -f"
echo "=========================================="