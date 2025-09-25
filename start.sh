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
python -m pip install --upgrade pip >/dev/null 2>&1 || true
pip install -r requirements.txt

# 环境变量检查
if [ -z "$PICGO_API_KEY" ]; then
    echo "⚠️  提示：未检测到 PICGO_API_KEY 环境变量。你可以在运行前导出："
    echo "    export PICGO_API_KEY=你的PicGoAPIKey"
    echo "    export PICGO_API_URL=https://www.picgo.net/api/1/upload  # 可选，默认已是此地址"
fi

echo "🌟 启动Flask服务器..."
echo "📱 后端API将运行在: http://localhost:8000"
echo "📖 API文档: http://localhost:8000 (可查看所有端点)"
echo "🛑 按 Ctrl+C 停止服务器"
echo ""

python app.py