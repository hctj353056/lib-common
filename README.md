# lib-common

> 蜉熵阁的 Python 通用基础库：把重复的工程能力整理成可复用、可测试、可组合的模块。

当前开发版本：**0.2.0**（PR 分支，尚未发布 PyPI 新版本）

## 设计目标

- **少重复**：配置、HTTP、缓存、日志、并发、文件与编码等常见能力集中维护。
- **易组合**：模块独立使用，也可从 `lib_common` 统一导入。
- **可验证**：重要行为由自动化测试覆盖。
- **边界明确**：网络超时、插件执行超时、SSH 主机密钥验证等安全边界显式化。
- **渐进兼容**：尽量保留旧模块与函数名，修正明显的接口行为错误。

## 安装

从源码安装：

```bash
git clone https://github.com/hctj353056/lib-common.git
cd lib-common
python -m pip install -e .
```

开发安装并运行测试：

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

## 模块总览

| 模块 | 用途 |
|---|---|
| `ai` | OpenAI 兼容接口、DeepSeek、火山引擎 ARK、SSE 流式输出 |
| `network` | HTTP 请求、会话复用、响应封装、原子下载 |
| `ssh` | SSH 命令执行、流式输出、SFTP 上传下载 |
| `config` | 环境变量读取、布尔/整数解析、设置映射 |
| `cache` | 线程安全、容量受限、TTL 缓存 |
| `logging` | 统一 Logger 获取与可选日志配置 |
| `concurrency` | 保持输入顺序的线程池并发映射 |
| `utils` | JSON、哈希、Base64、文件、时间、重试、分块 |
| `nlp` | 轻量分词与正则解析 |
| `vm` | 简单字节码虚拟机与表达式工具 |
| `godimport` | Python、JavaScript、Lua、Bash 插件调用适配 |

## 快速使用

### HTTP

```python
from lib_common.network import HttpClient

with HttpClient(timeout=15, headers={"User-Agent": "my-app/1.0"}) as http:
    response = http.get("https://example.com/api")
    response.raise_for_status()
    data = response.json()
```

HTTP 客户端使用可复用的 `requests.Session`。下载采用临时文件写入，成功后替换目标文件，避免网络中断留下半个文件。

### AI 对话与流式输出

```python
from lib_common.ai import DeepSeek, Message

with DeepSeek(api_key="YOUR_API_KEY") as client:
    answer = client.chat("deepseek-chat", "解释什么是形式系统")
    messages = [Message("user", "用一句话说明第一性原理")]
    for chunk in client.chat_stream("deepseek-chat", messages):
        print(chunk, end="", flush=True)
```

`chat(..., stream=True)` 会返回拼接后的完整文本；需要边生成边处理时，使用 `chat_stream()`。

### 配置

```python
from lib_common.config import env_bool, env_int, Settings

debug = env_bool("APP_DEBUG", default=False)
port = env_int("APP_PORT", 8000, minimum=1, maximum=65535)
settings = Settings(prefix="APP_")
token = settings.require("API_TOKEN")
```

布尔值接受 `1/0`、`true/false`、`yes/no`、`on/off`（不区分大小写）；其他值会明确报错。

### TTL 缓存

```python
from lib_common.cache import TTLCache

cache = TTLCache(ttl=30, maxsize=500)
cache.set("user:42", {"name": "example"})
user = cache.get("user:42")
```

缓存使用单调时钟计算过期时间，容量达到上限时按最近使用顺序淘汰。它是进程内缓存，不是持久化或分布式缓存。

### 日志与并发

```python
from lib_common.logging import get_logger, configure_logging
from lib_common.concurrency import map_parallel

configure_logging()
logger = get_logger(__name__)
results = map_parallel(fetch_one, urls, max_workers=8)
```

`map_parallel` 保留输入顺序；任务异常会向调用方传播。

### 文件与重试

```python
from lib_common import utils

utils.save_json({"name": "蜉蝣"}, "profile.json")  # 默认原子写入
digest = utils.sha256_file("profile.json")

@utils.retryable(times=4, delay=0.5, backoff=2)
def request_with_retry():
    ...
```

`retry_call` 与 `retryable` 支持指定重试次数、延迟、指数退避和异常类型。请只对可安全重试的操作使用重试，避免重复提交不可幂等的请求。

## SSH 安全说明

```python
from lib_common.ssh import SSHClient

with SSHClient("server.example", username="deploy", key_path="~/.ssh/id_ed25519") as ssh:
    result = ssh.exec("uname -a")
    if not result.success:
        raise RuntimeError(result.stderr)
```

默认使用系统 `known_hosts` 并拒绝未知主机密钥，防止自动信任未知服务器。自定义主机密钥文件可传入 `known_hosts="path/to/known_hosts"`。

只有在明确理解风险、且处于受控测试环境时，才使用 `allow_unknown_hosts=True`。不要把它作为生产默认值。私钥不会被库自动 chmod；请自行确保私钥文件权限正确。

## godimport 插件

`godimport` 可统一调用多种语言插件。插件通过 JSON 输入/输出协议与宿主通信：

```python
from lib_common.godimport import import_plugin

plugin = import_plugin("plugins/calc.py")
result = plugin.call("add", 2, 3)
```

插件通常会执行外部代码。**只加载你信任的插件**；`eval` 更是任意代码执行入口，不是沙箱。子进程适配器具备执行超时，但这不等于操作系统级隔离。

## 兼容与版本

- 旧的 `lib_common.network.HttpClient`、`lib_common.ai`、`lib_common.ssh` 和 `lib_common.utils` 入口保留。
- `chat_stream()` 修正为真正逐块 yield；此前它实际返回拼接字符串的行为不再保留。若要完整字符串，请使用 `chat(..., stream=True)`。
- SSH 默认主机密钥策略从自动接受改为拒绝未知密钥。首次连接前应将服务器公钥加入可信的 `known_hosts`。
- 本次版本仅在 PR 中准备，合并后仍需发布流程才能成为正式 PyPI 版本。

## 项目结构

```
src/
  __init__.py             # lib_common package root
  ai/                     # AI providers and streaming
  cache.py                # TTL cache
  config.py               # environment/settings
  concurrency.py           # parallel helpers
  logging.py               # logging helpers
  network/                 # HTTP client
  ssh/                    # SSH/SFTP
  utils/                  # common utilities
  nlp/ vm/ godimport/     # experimental modules
tests/                    # automated tests
.github/workflows/         # CI
```

## 许可证

MIT License
