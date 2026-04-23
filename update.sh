#!/bin/bash
# 智校通 - 更新代码脚本
# 用于在服务器上更新代码

APP_DIR="/var/www/zhixiaotong"

echo "正在更新智校通..."

# 进入目录
cd $APP_DIR

# 拉取最新代码（如果是git仓库）
if [ -d ".git" ]; then
    git pull
else
    echo "注意: 不是git仓库，请手动上传更新文件"
fi

# 重启服务
systemctl restart zhixiaotong
echo "服务已重启"