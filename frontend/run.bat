# 前端启动脚本 (Windows)
@echo off
setlocal enabledelayedexpansion

echo ========================================
echo UAV 无人机巡检系统 - 前端启动脚本
echo ========================================
echo.

:: 检查 Node.js 版本
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 检测不到 Node.js，请确保已安装 Node.js 14.0+
    pause
    exit /b 1
)

:: 显示 Node.js 版本
echo 检测到 Node.js:
node -v
npm -v
echo.

:: 检查 package.json
if not exist "package.json" (
    echo 错误: 未找到 package.json，请在项目根目录运行此脚本
    pause
    exit /b 1
)

:: 安装依赖（如果需要）
if not exist "node_modules" (
    echo 检测到首次运行，正在安装依赖...
    call npm install
    if %errorlevel% neq 0 (
        echo.
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo 启动开发服务器...
echo 访问地址: http://localhost:5173
echo 按 Ctrl+C 停止服务器
echo.

:: 运行开发服务器
call npm run dev

pause
