#!/bin/bash

# 创建日志目录
mkdir -p logs

# 检查本地PostgreSQL是否可用
echo "检查PostgreSQL服务是否可用..."
if command -v pg_isready > /dev/null; then
    if pg_isready -h localhost -p 5432 -U postgres > /dev/null 2>&1; then
        echo "PostgreSQL服务已就绪！"
    else
        echo "警告: PostgreSQL服务似乎未运行。请确保您的PostgreSQL服务已启动。"
        echo "可以使用以下命令启动PostgreSQL服务："
        echo "  - macOS: brew services start postgresql"
        echo "  - Linux: sudo service postgresql start"
        echo "  - Windows: 通过服务管理控制台启动PostgreSQL服务"
        
        read -p "是否继续启动应用? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "警告: 未检测到pg_isready命令，无法检查PostgreSQL状态。"
    echo "请确保您的PostgreSQL服务已启动。"
fi

# 创建数据库（如果不存在）
echo "检查数据库是否存在..."
if command -v psql > /dev/null; then
    if ! psql -h localhost -U postgres -lqt | cut -d \| -f 1 | grep -qw voice_service; then
        echo "创建voice_service数据库..."
        psql -h localhost -U postgres -c "CREATE DATABASE voice_service;" || true
    else
        echo "数据库voice_service已存在。"
    fi
else
    echo "警告: 未检测到psql命令，无法创建数据库。"
    echo "请确保voice_service数据库已创建。"
fi

# 设置Python路径，确保能找到app包
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "已设置PYTHONPATH: $PYTHONPATH"

# 运行应用
echo "启动语音意图识别服务..."
python run.py
