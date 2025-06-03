# 语音意图识别服务 (VoiceService)

## 项目简介

这是一个基于Python和Qwen大模型的语音意图识别服务系统，支持通过Android客户端实时录音，在服务端进行意图识别并触发相应动作。系统采用分层架构设计，实现了高度解耦和可扩展性。

### 主要功能

- **语音采集**：Android客户端实时录音，监测声音活动
- **语音转文本**：将录制的语音转换为文本
- **意图识别**：使用Qwen大模型分析文本并识别用户意图
- **动作触发**：基于识别的意图生成动作指令，下发到客户端执行

## 系统架构

### 整体架构

系统分为客户端和服务端两大部分：

- **客户端**：Android应用，负责音频采集、语音转文本和动作执行
- **服务端**：Python应用，负责意图识别和动作生成

### 服务端架构

服务端采用分层架构设计，主要包括：

1. **控制层(Controller)**：处理HTTP请求和响应，负责输入验证和路由管理
2. **领域层(Domain)**：包含业务实体、值对象和领域逻辑
3. **服务层(Service)**：实现业务逻辑，协调各种操作
4. **基础设施层(adapters)**：提供技术支持，包括日志、数据访问、LLM集成等

### 项目结构

```
VoiceService/
├── app/
│   ├── __init__.py
│   ├── main.py                     # 应用入口点
│   ├── config.py                   # 配置设置
│   ├── common/                     # 通用组件
│   │   ├── logging/                # 日志模块
│   │   ├── exception/              # 异常处理
│   │   └── utils/                  # 通用工具
│   ├── controller/                 # 控制层
│   │   ├── base_controller.py      # 基础控制器
│   │   └── intent_controller.py    # 意图识别控制器
│   ├── domain/                     # 领域层
│   │   ├── entity/                 # 实体
│   │   ├── value_object/           # 值对象
│   │   └── repository/             # 仓储接口
│   ├── service/                    # 服务层
│   │   ├── base_service.py         # 基础服务
│   │   ├── intent_service.py       # 意图识别服务
│   │   └── llm_service.py          # 大模型服务
│   └── adapters/             # 基础设施
│       ├── repository/             # 仓储实现
│       └── llm/                    # 大模型集成
├── logs/                           # 日志文件
├── docker/                         # Docker配置
├── requirements.txt                # 依赖项
└── run.py                          # 应用程序运行器
```

## 技术栈

### 服务端
- **框架**：FastAPI (高性能异步Web框架)
- **大模型**：Qwen (通义千问大模型)
- **部署**：Docker + Nginx
- **日志系统**：自定义封装的多级别日志系统

### 客户端
- **平台**：Android (Kotlin)
- **语音转文本**：Google Speech-to-Text API或本地Whisper模型
- **网络通信**：Retrofit

## API接口

### 意图识别接口

- **URL**: `/api/intent/recognize`
- **方法**: POST
- **请求体**:
```json
{
    "text": "打开空调并设置温度为26度"
}
```
- **响应**:
```json
{
    "success": true,
    "message": "Success",
    "data": {
        "intent": "control_device",
        "confidence": 0.95,
        "action": {
            "type": "device_control",
            "target": "air_conditioner",
            "operation": "turn_on",
            "parameters": {
                "temperature": 26
            }
        }
    }
}
```

### 健康检查接口

- **URL**: `/api/health`
- **方法**: GET
- **响应**:
```json
{
    "success": true,
    "message": "Service is healthy",
    "data": {
        "status": "up",
        "version": "1.0.0"
    }
}
```

## 安装与配置

### 环境要求
- Python 3.9+
- Docker (可选，用于容器化部署)

### 安装步骤

1. **克隆代码库**
```bash
git clone <repository-url>
cd VoiceService
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **环境配置**
复制示例环境文件并根据需要修改:
```bash
cp .env.example .env
```

5. **运行服务**
```bash
python run.py
```

### Docker部署

1. **构建镜像**
```bash
docker-compose build
```

2. **启动服务**
```bash
docker-compose up -d
```

## 客户端集成

Android客户端需要实现以下功能：

1. **音频录制**：使用AudioRecord API进行实时录音
2. **语音活动检测**：识别用户是否在说话
3. **语音转文本**：将音频转换为文本
4. **API通信**：将文本发送到服务端并接收意图响应
5. **动作执行**：根据服务端返回的动作指令执行相应功能

## 项目扩展

### 添加新意图

1. 在`domain/entity/intent.py`中定义新的意图类型
2. 在`service/intent_service.py`中添加对应的意图处理逻辑
3. 在`adapters/llm/prompt_templates.py`中更新提示模板以支持新意图

### 添加新动作

1. 在`domain/entity/action.py`中定义新的动作类型
2. 在`service/intent_service.py`中添加意图到动作的映射逻辑

## 日志与监控

系统采用分级日志机制，包括：

- INFO级别：记录正常操作
- WARNING级别：记录潜在问题
- ERROR级别：记录错误信息
- DEBUG级别：记录调试信息

日志文件位于`logs/`目录下，按日期和大小自动轮转。

## 贡献指南

欢迎贡献代码或提出问题。请遵循以下步骤：

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

[MIT License](LICENSE)
