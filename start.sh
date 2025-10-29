#!/bin/bash

# YOLOv11在线训练平台 - 启动脚本 (Linux/Mac)

echo "========================================"
echo "  YOLOv11在线训练平台 - 启动脚本"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] 未检测到Node.js，请先安装Node.js 16+"
    exit 1
fi

echo "[1/4] 检查后端虚拟环境..."
if [ ! -d "backend/venv" ]; then
    echo "[信息] 创建Python虚拟环境..."
    cd backend
    python3 -m venv venv
    cd ..
fi

echo "[2/4] 检查后端依赖..."
if [ ! -d "backend/venv/lib/python3"*/site-packages/flask ]; then
    echo "[信息] 安装后端依赖（首次运行可能需要几分钟）..."
    cd backend
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ..
fi

echo "[3/4] 检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "[信息] 安装前端依赖（首次运行可能需要几分钟）..."
    cd frontend
    npm install
    cd ..
fi

echo "[4/4] 启动服务..."
echo ""
echo "========================================"
echo "  启动后端服务 (http://localhost:5000)"
echo "========================================"

cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 5

echo ""
echo "========================================"
echo "  启动前端服务 (http://localhost:3000)"
echo "========================================"

cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  服务已启动！"
echo "========================================"
echo ""
echo "后端地址: http://localhost:5000"
echo "前端地址: http://localhost:3000"
echo "后端PID: $BACKEND_PID"
echo "前端PID: $FRONTEND_PID"
echo ""
echo "请在浏览器中打开: http://localhost:3000"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待中断信号
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

# 保持脚本运行
wait
