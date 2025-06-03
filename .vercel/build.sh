#!/bin/bash

# 安装Python依赖
pip install -r requirements.txt

# 复制静态文件（如果需要）
mkdir -p .vercel/output/static
cp -r app/static/* .vercel/output/static/

# 创建输出配置
mkdir -p .vercel/output
cat > .vercel/output/config.json << EOF
{
  "version": 3,
  "routes": [
    { "src": "/static/(.*)", "dest": "/static/$1" },
    { "src": "/(.*)", "dest": "/api/index.py" }
  ]
}
EOF

# 创建函数目录
mkdir -p .vercel/output/functions/api
cp api/index.py .vercel/output/functions/api/

echo "构建完成" 