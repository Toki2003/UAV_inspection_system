#!/bin/bash

# UAV 无人机巡检系统 - 前端启动脚本

echo "========================================"
echo "UAV 无人机巡检系统 - 前端启动脚本"
echo "========================================"
echo ""

# 检查 Node.js 版本
if ! command -v node &> /dev/null
then
    echo "错误: 检测不到 Node.js，请确保已安装 Node.js 14.0+"
    exit 1
fi

echo "检测到 Node.js:"
node -v
npm -v
echo ""

# 检查 package.json
if [ ! -f "package.json" ]; then
    echo "错误: 未找到 package.json，请在项目根目录运行此脚本"
    exit 1
fi

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "检测到首次运行，正在安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo ""
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

echo ""
echo "启动开发服务器..."
echo "访问地址: http://localhost:5173"
echo "按 Ctrl+C 停止服务器"
echo ""

# 运行开发服务器
npm run dev
