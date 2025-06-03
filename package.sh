#!/bin/bash
set -e

# 显示脚本执行步骤
set -x

# 配置变量
APP_NAME="VoiceService"
VERSION=$(grep -o 'APP_VERSION = "[^"]*"' app/config.py | cut -d'"' -f2)
PACKAGE_DIR="dist/${APP_NAME}-${VERSION}"
VENV_DIR="venv"
PYTHON="python3"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 输出信息函数
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 检查Python版本
info "检查Python环境..."
if ! command -v ${PYTHON} &> /dev/null; then
    error "未找到Python。请安装Python 3.8或更高版本。"
fi

PYTHON_VERSION=$(${PYTHON} --version | cut -d " " -f 2)
info "检测到Python版本: ${PYTHON_VERSION}"

# 创建打包目录
info "准备打包目录..."
mkdir -p ${PACKAGE_DIR}

# 确保虚拟环境存在
if [ ! -d "${VENV_DIR}" ]; then
    info "创建虚拟环境..."
    ${PYTHON} -m venv ${VENV_DIR}
fi

# 激活虚拟环境
source ${VENV_DIR}/bin/activate || error "无法激活虚拟环境"
info "已激活虚拟环境"

# 安装/更新依赖
info "安装项目依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 运行测试（如果有）
if [ -d "tests" ]; then
    info "运行测试..."
    pytest tests/ || warn "测试失败，但将继续打包"
fi

# 复制必要文件到打包目录
info "打包应用文件..."
cp -r app ${PACKAGE_DIR}/
cp run.py ${PACKAGE_DIR}/
cp requirements.txt ${PACKAGE_DIR}/
cp start.sh ${PACKAGE_DIR}/
cp README.md ${PACKAGE_DIR}/ 2>/dev/null || true

# 复制环境配置文件
if [ -f ".env" ]; then
    info "复制现有.env配置文件..."
    cp .env ${PACKAGE_DIR}/
fi

# 生成.env模板文件（如果不存在）
if [ ! -f ".env.template" ]; then
    info "生成.env模板文件..."
    cat > ${PACKAGE_DIR}/.env.template << EOF
# 服务器设置
DEBUG=False
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 大模型配置
DASHSCOPE_API_KEY=
QWEN_MODEL_NAME=qwen-max

# 第三方API配置
AMAP_API_KEY=

# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/voice_service

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=logs
EOF
else
    cp .env.template ${PACKAGE_DIR}/
fi

# 创建打包归档文件
info "创建归档文件..."
ARCHIVE_NAME="${APP_NAME}-${VERSION}.tar.gz"
mkdir -p dist
tar -czf "dist/${ARCHIVE_NAME}" -C dist "${APP_NAME}-${VERSION}"

# 显示打包结果
info "打包完成: dist/${ARCHIVE_NAME}"
info "应用版本: ${VERSION}"
info "打包大小: $(du -h dist/${ARCHIVE_NAME} | cut -f1)"

# 创建部署说明
cat > dist/DEPLOY.md << EOF
# ${APP_NAME} 部署说明

## 准备工作

1. 确保目标服务器已安装Python 3.8或更高版本
2. 确保PostgreSQL数据库可用

## 部署步骤

1. 解压应用包：
   \`\`\`bash
   tar -xzf ${ARCHIVE_NAME}
   cd ${APP_NAME}-${VERSION}
   \`\`\`

2. 配置环境变量：
   \`\`\`bash
   # 如果包中已包含配置好的.env文件，可以直接使用
   # 如需修改配置，编辑.env文件
   nano .env
   \`\`\`

3. 创建虚拟环境并安装依赖：
   \`\`\`bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   \`\`\`

4. 启动应用：
   \`\`\`bash
   ./start.sh
   \`\`\`

## 生产环境部署建议

对于生产环境，建议使用进程管理工具（如Supervisor）来管理应用：

1. 安装Supervisor：
   \`\`\`bash
   apt-get install supervisor  # Debian/Ubuntu
   # 或
   yum install supervisor      # CentOS/RHEL
   \`\`\`

2. 创建Supervisor配置：
   \`\`\`
   [program:${APP_NAME}]
   command=/path/to/${APP_NAME}-${VERSION}/venv/bin/python /path/to/${APP_NAME}-${VERSION}/run.py
   directory=/path/to/${APP_NAME}-${VERSION}
   user=www-data
   autostart=true
   autorestart=true
   stopasgroup=true
   killasgroup=true
   environment=PYTHONPATH="/path/to/${APP_NAME}-${VERSION}"
   \`\`\`

3. 重启Supervisor：
   \`\`\`bash
   supervisorctl reread
   supervisorctl update
   supervisorctl start ${APP_NAME}
   \`\`\`
EOF

info "已生成部署说明文件: dist/DEPLOY.md"
info "打包脚本执行完成！" 