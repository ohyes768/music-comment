#!/bin/bash
# 网易云音乐评论桌面应用启动脚本

cd "$(dirname "$0")/.."

echo "=========================================="
echo "网易云音乐评论桌面应用"
echo "=========================================="

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "错误: 虚拟环境不存在，请先运行: uv venv"
    exit 1
fi

# 激活虚拟环境并运行应用
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash)
    .venv/Scripts/python.exe src/main.py "$@"
else
    # Linux/Mac
    source .venv/bin/activate
    python src/main.py "$@"
fi
