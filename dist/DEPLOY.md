# VoiceService 部署说明

## 准备工作

1. 确保目标服务器已安装Python 3.8或更高版本
2. 确保PostgreSQL数据库可用

## 部署步骤

1. 解压应用包：
   ```bash
   tar -xzf VoiceService-1.0.0.tar.gz
   cd VoiceService-1.0.0
   ```

2. 配置环境变量：
   ```bash
   # 如果包中已包含配置好的.env文件，可以直接使用
   # 如需修改配置，编辑.env文件
   nano .env
   ```

3. 创建虚拟环境并安装依赖：
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. 启动应用：
   ```bash
   ./start.sh
   ```

## 生产环境部署建议

对于生产环境，建议使用进程管理工具（如Supervisor）来管理应用：

1. 安装Supervisor：
   ```bash
   apt-get install supervisor  # Debian/Ubuntu
   # 或
   yum install supervisor      # CentOS/RHEL
   ```

2. 创建Supervisor配置：
   ```
   [program:VoiceService]
   command=/path/to/VoiceService-1.0.0/venv/bin/python /path/to/VoiceService-1.0.0/run.py
   directory=/path/to/VoiceService-1.0.0
   user=www-data
   autostart=true
   autorestart=true
   stopasgroup=true
   killasgroup=true
   environment=PYTHONPATH="/path/to/VoiceService-1.0.0"
   ```

3. 重启Supervisor：
   ```bash
   supervisorctl reread
   supervisorctl update
   supervisorctl start VoiceService
   ```
