#!/bin/bash

echo "🚀 启动文章管理系统后端..."

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "❌ 请在backend目录运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

echo "🔧 激活虚拟环境..."
source venv/bin/activate

echo "📥 安装/更新依赖..."
./venv/bin/pip install -r requirements.txt

echo "🌟 启动Flask服务器..."
echo "📱 后端API将运行在: http://localhost:8000"
echo "📖 API文档: http://localhost:8000 (可查看所有端点)"
echo "🛑 按 Ctrl+C 停止服务器"
echo ""

./venv/bin/python app.py