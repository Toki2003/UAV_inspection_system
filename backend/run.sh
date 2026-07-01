#!/bin/bash

# UAV 无人机巡检系统 - 后端启动脚本

echo "========================================"
echo "UAV 无人机巡检系统 - 后端启动脚本"
echo "========================================"
echo ""

# 检查 Java 版本
if ! command -v java &> /dev/null
then
    echo "错误: 检测不到 Java，请确保已安装 JDK 1.8+"
    exit 1
fi

echo "检测到 Java:"
java -version
echo ""

# 检查 pom.xml
if [ ! -f "pom.xml" ]; then
    echo "错误: 未找到 pom.xml，请在项目根目录运行此脚本"
    exit 1
fi

# 编译和运行
echo "正在构建项目..."
mvn clean package -DskipTests

if [ $? -ne 0 ]; then
    echo ""
    echo "错误: 项目构建失败"
    exit 1
fi

echo ""
echo "构建完成，正在启动应用..."
echo ""

# 查找并运行 JAR 文件
JAR_FILE=$(find target -name "inspection-system*.jar" -type f | head -1)

if [ -z "$JAR_FILE" ]; then
    echo "错误: 未找到构建的 JAR 文件"
    exit 1
fi

java -jar "$JAR_FILE"
