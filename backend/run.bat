# 后端启动脚本 (Windows)
@echo off
setlocal enabledelayedexpansion

echo ========================================
echo UAV 无人机巡检系统 - 后端启动脚本
echo ========================================
echo.

:: 检查 Java 版本
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 检测不到 Java，请确保已安装 JDK 1.8+
    pause
    exit /b 1
)

:: 显示 Java 版本
echo 检测到 Java:
java -version
echo.

:: 检查 pom.xml
if not exist "pom.xml" (
    echo 错误: 未找到 pom.xml，请在项目根目录运行此脚本
    pause
    exit /b 1
)

:: 编译和运行
echo 正在构建项目...
call mvn clean package -DskipTests

if %errorlevel% neq 0 (
    echo.
    echo 错误: 项目构建失败
    pause
    exit /b 1
)

echo.
echo 构建完成，正在启动应用...
echo.

for /f %%a in ('dir /b /s target\*.jar ^| findstr /r "inspection-system.*\.jar$"') do (
    java -jar "%%a"
    goto :end
)

:end
pause
