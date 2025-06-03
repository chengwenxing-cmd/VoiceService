FROM python:3.9-slim

WORKDIR /app

# 设置Python环境
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户运行应用
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "run.py"]
