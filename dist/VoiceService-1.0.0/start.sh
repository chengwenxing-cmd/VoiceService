#!/bin/bash

# 检查是否在Python虚拟环境中
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "未检测到Python虚拟环境，开始创建并激活虚拟环境..."
    # 创建Python3.9虚拟环境
    python3.9 -m venv venv
    # 激活虚拟环境
    source venv/bin/activate
    # 安装依赖
    pip install -r requirements.txt
    echo "虚拟环境已创建并激活，依赖已安装。"
else
    echo "已在Python虚拟环境中: $VIRTUAL_ENV"
fi

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

# 检查端口占用情况（默认使用8000端口，可根据实际情况调整）
PORT=8763
echo "检查端口 $PORT 是否被占用..."
if command -v lsof > /dev/null; then
    PORT_PIDS=$(lsof -ti:$PORT)
    if [ ! -z "$PORT_PIDS" ]; then
        echo "警告: 端口 $PORT 已被占用，进程ID: $PORT_PIDS"
        echo "自动终止占用端口的进程..."
        for PID in $PORT_PIDS; do
            echo "终止进程 $PID..."
            kill -9 $PID
        done
        sleep 1
        
        # 再次检查端口是否已释放
        PORT_PIDS_AFTER=$(lsof -ti:$PORT)
        if [ ! -z "$PORT_PIDS_AFTER" ]; then
            echo "错误: 无法释放端口 $PORT，进程ID: $PORT_PIDS_AFTER"
            echo "请手动终止这些进程后再运行脚本"
            exit 1
        else
            echo "端口 $PORT 已成功释放"
        fi
    else
        echo "端口 $PORT 可用"
    fi
else
    echo "警告: 无法检查端口占用情况 (lsof命令不可用)"
    echo "继续执行，但可能会遇到端口占用错误"
fi

# 运行应用
echo "启动语音意图识别服务..."
python run.py
