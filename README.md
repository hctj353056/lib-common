# lib-common

通用Python工具库 - 网络、SSH、AI、虚拟机

## 安装

```bash
pip install lib-common
```

或从源码：

```bash
git clone https://github.com/hctj353056/lib-common
cd lib-common
pip install -e .
```

## 快速开始

### SSH连接

```python
from lib_common import ssh

# 方式1: 使用上下文管理器
with ssh.SSHClient("192.168.1.1", key_path="./key.pem") as client:
    result = client.exec("ls -la")
    print(result.stdout)

# 方式2: 快速执行
from lib_common.ssh import quick_exec
print(quick_exec("192.168.1.1", "./key.pem", "uname -a"))
```

### AI对话

```python
from lib_common import ai

# OpenAI兼容格式
client = ai.OpenAICompatible("https://api.deepseek.com/v1", "your-api-key")
response = client.chat("deepseek-chat", [{"role": "user", "content": "你好"}])
print(response)

# DeepSeek专用
client = ai.DeepSeek("your-deepseek-api-key")
print(client.chat("deepseek-chat", [{"role": "user", "content": "解释量子力学"}]))

# 火山引擎ARK
client = ai.VolcengineARK("your-ark-api-key")
print(client.chat("doubao-pro-32k", [{"role": "user", "content": "你好"}]))
```

### HTTP请求

```python
from lib_common import network

client = network.HttpClient()

# GET
response = client.get("https://api.example.com/data")
print(response.json())

# POST
response = client.post("https://api.example.com/create", json={"name": "test"})
print(response.text)

# 下载文件
client.download("https://example.com/file.zip", "./file.zip")
```

### 虚拟机

```python
from lib_common import vm

# 简单算术
bytecode = [
    ("PUSH", 10),      # 压入10
    ("PUSH", 20),      # 压入20
    ("ADD", None),     # 相加
    ("PRINT", None),   # 打印结果
]

vm.run_bytecode(bytecode)  # 输出: 30
```

## 模块结构

```
lib_common/
├── ssh/          # SSH连接
├── ai/           # AI模型调用
├── network/      # HTTP请求
├── vm/           # 虚拟机/解释器
├── nlp/          # NLP处理 (待开发)
└── utils/        # 通用工具
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 代码格式化
black src/
```

## 许可证

MIT License
