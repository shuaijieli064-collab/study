#!/bin/bash
# 智校通 - 服务器部署脚本 (CentOS/RHEL)

set -e

APP_NAME="zhixiaotong"
APP_DIR="/var/www/zhixiaotong"
DOMAIN="${DOMAIN:-123.56.84.160}"

echo "=========================================="
echo "智校通 - 服务器部署脚本"
echo "=========================================="

# 1. 更新系统
echo "[1/7] 更新系统..."
yum update -y

# 2. 安装Python和依赖
echo "[2/7] 安装Python环境..."
yum install -y python3 python3-pip nginx certbot python3-certbot-nginx

# 3. 创建应用目录
echo "[3/7] 创建应用目录..."
mkdir -p $APP_DIR
cp -r backend frontend data .env deploy.sh $APP_DIR/ 2>/dev/null || true

# 4. 创建虚拟环境并安装依赖
echo "[4/7] 创建虚拟环境..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 5. 配置systemd服务
echo "[5/7] 配置系统服务..."
cat > /etc/systemd/system/zhixiaotong.service << 'EOF'
[Unit]
Description=Zhixiaotong Flask App
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/zhixiaotong/backend
Environment="PATH=/var/www/zhixiaotong/venv/bin"
EnvironmentFile=/var/www/zhixiaotong/.env
ExecStart=/var/www/zhixiaotong/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. 配置Nginx
echo "[6/7] 配置Nginx..."
cat > /etc/nginx/conf.d/zhixiaotong.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 7. 启动服务
echo "[7/7] 启动服务..."
nginx -t
systemctl daemon-reload
systemctl enable zhixiaotong
systemctl restart zhixiaotong
systemctl restart nginx

# 开放防火墙端口
echo "开放��火墙端口..."
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload

echo ""
echo "=========================================="
echo "部署完成！"
echo "访问地址: http://$DOMAIN"
echo "=========================================="
echo ""
echo "常用命令："
echo "查看状态: systemctl status zhixiaotong"
echo "查看日志: journalctl -u zhixiaotong -f"
echo "重启服务: systemctl restart zhixiaotong"