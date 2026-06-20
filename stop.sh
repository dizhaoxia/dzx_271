#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "正在停止服务..."

for pid_file in backend.pid frontend.pid; do
    if [ -f "$ROOT_DIR/$pid_file" ]; then
        PID=$(cat "$ROOT_DIR/$pid_file")
        if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
            kill -9 "$PID" 2>/dev/null
            echo "已停止进程: $PID ($pid_file)"
        fi
        rm -f "$ROOT_DIR/$pid_file"
    fi
done

for port in 30001 50001; do
    PIDS=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "清理端口 $port 上的进程: $PIDS"
        kill -9 $PIDS 2>/dev/null
    fi
done

rm -f "$ROOT_DIR"/*.log 2>/dev/null

echo "服务已全部停止"
