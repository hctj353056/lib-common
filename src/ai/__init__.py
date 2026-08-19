# -*- coding: utf-8 -*-
"""
lib-common.ai: AI模型调用模块

支持：
- OpenAI兼容API
- DeepSeek
- 火山引擎ARK
- 流式输出
- Function Calling

示例:
    from lib_common.ai import OpenAICompatible, DeepSeek
    
    # OpenAI兼容格式
    client = OpenAICompatible(base_url, api_key)
    response = client.chat("gpt-4", "你好")
    
    # DeepSeek
    client = DeepSeek(api_key)
    response = client.chat("deepseek-chat", "解释量子力学")
"""

import requests
import json
from typing import List, Dict, Optional, Generator, Any, Callable
from dataclasses import dataclass


@dataclass
class Message:
    """对话消息"""
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict:
        d = {"role": self.role, "content": self.content}
        if self.name:
            d["name"] = self.name
        return d


class BaseAIClient:
    """AI客户端基类"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def _post(self, endpoint: str, payload: Dict) -> Dict:
        """POST请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, json=payload, headers=self.headers, timeout=60)
        response.raise_for_status()
        return response.json()
    
    def _post_stream(self, endpoint: str, payload: Dict, 
                     on_chunk: Callable[[str], None]):
        """流式POST请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, json=payload, headers=self.headers, 
                               stream=True, timeout=60)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                text = line.decode()[6:]  # 去掉 "data: " 前缀
                if text == "[DONE]":
                    break
                try:
                    data = json.loads(text)
                    content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        on_chunk(content)
                except (UnicodeDecodeError, json.JSONDecodeError, IndexError, AttributeError):
                    continue


class OpenAICompatible(BaseAIClient):
    """OpenAI兼容格式的AI客户端"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        初始化
        
        Args:
            base_url: API地址，如 "https://api.openai.com/v1"
            api_key: API密钥
        """
        super().__init__(api_key, base_url)
    
    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> str:
        """
        对话接口
        
        Args:
            model: 模型ID
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
            **kwargs: 其他参数
        
        Returns:
            AI回复文本
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        payload.update(kwargs)
        
        data = self._post("/chat/completions", payload)
        return data["choices"][0]["message"]["content"]
    
    def chat_stream(self, model: str, messages: List[Dict[str, str]], 
                   temperature: float = 0.7) -> Generator[str, None, None]:
        """
        流式对话
        
        Args:
            model: 模型ID
            messages: 消息列表
            temperature: 温度参数
        
        Yields:
            逐字输出
        """
        result = []
        
        def on_chunk(chunk: str):
            result.append(chunk)
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        self._post_stream("/chat/completions", payload, on_chunk)
        return "".join(result)


class DeepSeek(OpenAICompatible):
    """DeepSeek专用客户端"""
    
    BASE_URL = "https://api.deepseek.com/v1"
    
    def __init__(self, api_key: str):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥
        """
        super().__init__(self.BASE_URL, api_key)


class VolcengineARK(BaseAIClient):
    """火山引擎ARK专用客户端"""
    
    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    
    def __init__(self, api_key: str):
        """
        初始化火山引擎ARK客户端
        
        Args:
            api_key: ARK API密钥（不是AK/SK）
        """
        super().__init__(api_key, self.BASE_URL)
    
    def chat(
        self,
        model: str,  # 如 "doubao-pro-32k"
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """对话接口"""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        data = self._post("/chat/completions", payload)
        return data["choices"][0]["message"]["content"]


def quick_chat(message: str, api_key: str, base_url: str, 
               model: str = "gpt-3.5-turbo") -> str:
    """
    快速对话（单次调用）
    
    Args:
        message: 用户消息
        api_key: API密钥
        base_url: API地址
        model: 模型ID
    
    Returns:
        AI回复
    """
    client = OpenAICompatible(base_url, api_key)
    return client.chat(model, [{"role": "user", "content": message}])
