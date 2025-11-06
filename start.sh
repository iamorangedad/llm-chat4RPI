#!/bin/bash

# 树莓派 LLM 助手启动脚本

echo "======================================"
echo "  树莓派 LLM 助手启动脚本"
echo "======================================"
echo ""

# 检查 Ollama 是否运行
echo "检查 Ollama 服务状态..."
if ! systemctl is-active --quiet ollama; then
    echo "❌ Ollama 服务未运行，尝试启动..."
    sudo systemctl start ollama
    sleep 2
fi

if systemctl is-active --quiet ollama; then
    echo "✅ Ollama 服务正在运行"
else
    echo "❌ Ollama 服务启动失败，请手动检查"
    exit 1
fi

# 检查模型是否存在
echo ""
echo "检查 Qwen3 模型..."
if ollama list | grep -q "qwen3:0.6b"; then
    echo "✅ Qwen3 模型已安装"
else
    echo "⚠️  Qwen3 模型未找到，开始下载..."
    ollama pull qwen3:0.6b
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo ""
    echo "激活 Python 虚拟环境..."
    source venv/bin/activate
fi

# 检查 Python 依赖
echo ""
echo "检查 Python 依赖..."
pip list | grep -q fastapi || pip install -r requirements.txt

# 启动后端服务（后台运行）
echo ""
echo "启动后端服务..."
cd backend
python main.py &
BACKEND_PID=$!
echo "后端服务已启动，PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 启动前端服务
echo ""
echo "启动前端服务..."
cd ../frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
echo "前端服务已启动，PID: $FRONTEND_PID"

echo ""
echo "======================================"
echo "✅ 所有服务已启动！"
echo "======================================"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:3000"
echo "  后端: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 保存 PID 到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 等待用户中断
trap cleanup INT

cleanup() {
    echo ""
    echo "正在停止服务..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    rm -f .backend.pid .frontend.pid
    echo "所有服务已停止"
    exit 0
}

# 保持脚本运行
wait