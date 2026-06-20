#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========== SCL-90 症状自评量表系统启动 =========="
echo ""

BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

BACKEND_PORT=30001
FRONTEND_PORT=50001

echo "[1/4] 启动后端服务 (端口: $BACKEND_PORT)..."
cd "$BACKEND_DIR"
python3 manage.py runserver 0.0.0.0:$BACKEND_PORT > "$ROOT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"

sleep 2

echo ""
echo "[2/4] 启动前端服务 (端口: $FRONTEND_PORT)..."
cd "$FRONTEND_DIR"
npm run dev > "$ROOT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"

sleep 3

echo ""
echo "[3/4] 写入 PID 文件..."
echo "$BACKEND_PID" > "$ROOT_DIR/backend.pid"
echo "$FRONTEND_PID" > "$ROOT_DIR/frontend.pid"

echo ""
echo "[4/4] 启动完成！"
echo ""
echo "  后端地址: http://127.0.0.1:$BACKEND_PORT"
echo "  API 文档: http://127.0.0.1:$BACKEND_PORT/swagger/"
echo "  前端地址: http://127.0.0.1:$FRONTEND_PORT"
echo ""
echo "  管理员账号: 13800138000 / admin123"
echo ""
echo "  停止服务: ./stop.sh"
echo "  查看日志: tail -f backend.log 或 tail -f frontend.log"
echo ""
echo "================================================"
