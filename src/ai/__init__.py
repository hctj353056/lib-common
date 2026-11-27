# -*- coding: utf-8 -*-
"""OpenAI-compatible chat clients with Server-Sent Events streaming."""
import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Union
import requests

@dataclass
class Message:
    role: str
    content: Any
    name: Optional[str] = None
    def to_dict(self) -> Dict:
        result = {"role": self.role, "content": self.content}
        if self.name: result["name"] = self.name
        return result

def _normalize_messages(messages: Union[str, Message, Iterable[Union[Dict, Message]]]) -> List[Dict]:
    if isinstance(messages, str): return [{"role": "user", "content": messages}]
    if isinstance(messages, Message): return [messages.to_dict()]
    return [message.to_dict() if isinstance(message, Message) else dict(message) for message in messages]

class BaseAIClient:
    def __init__(self, api_key: str, base_url: str, timeout: int = 60):
        if not api_key: raise ValueError("api_key must not be empty")
        if not base_url: raise ValueError("base_url must not be empty")
        self.api_key = api_key; self.base_url = base_url.rstrip("/"); self.timeout = timeout
        self.headers = {"Content-Type": "application/json", "Authorization": "Bearer %s" % api_key}
        self.session = requests.Session()
    def _post(self, endpoint: str, payload: Dict) -> Dict:
        response = self.session.post(self.base_url + endpoint, json=payload, headers=self.headers, timeout=self.timeout)
        response.raise_for_status(); return response.json()
    def _iter_stream(self, endpoint: str, payload: Dict) -> Generator[str, None, None]:
        """Yield content deltas; ignore SSE comments, metadata and malformed frames."""
        with self.session.post(self.base_url + endpoint, json=payload, headers=self.headers, stream=True, timeout=self.timeout) as response:
            response.raise_for_status()
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line: continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if not line.startswith("data:"): continue
                frame = line[5:].strip()
                if frame == "[DONE]": break
                try: data = json.loads(frame)
                except json.JSONDecodeError: continue
                choices = data.get("choices") or []
                if not choices: continue
                content = (choices[0].get("delta") or {}).get("content")
                if isinstance(content, str) and content: yield content
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and isinstance(item.get("text"), str): yield item["text"]
    def _post_stream(self, endpoint: str, payload: Dict, on_chunk: Callable[[str], None]) -> None:
        for chunk in self._iter_stream(endpoint, payload): on_chunk(chunk)
    def close(self): self.session.close()
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.close()

class OpenAICompatible(BaseAIClient):
    def __init__(self, base_url: str, api_key: str, timeout: int = 60): super().__init__(api_key, base_url, timeout)
    def chat(self, model: str, messages, temperature: float = 0.7, max_tokens: Optional[int] = None, stream: bool = False, **kwargs) -> str:
        normalized = _normalize_messages(messages)
        if stream: return "".join(self.chat_stream(model, normalized, temperature, max_tokens=max_tokens, **kwargs))
        payload = {"model": model, "messages": normalized, "temperature": temperature}
        if max_tokens is not None: payload["max_tokens"] = max_tokens
        payload.update(kwargs); data = self._post("/chat/completions", payload)
        return data["choices"][0]["message"].get("content") or ""
    def chat_stream(self, model: str, messages, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> Generator[str, None, None]:
        payload = {"model": model, "messages": _normalize_messages(messages), "temperature": temperature, "stream": True}
        if max_tokens is not None: payload["max_tokens"] = max_tokens
        payload.update(kwargs); yield from self._iter_stream("/chat/completions", payload)

class DeepSeek(OpenAICompatible):
    BASE_URL = "https://api.deepseek.com/v1"
    def __init__(self, api_key: str, timeout: int = 60): super().__init__(self.BASE_URL, api_key, timeout)

class VolcengineARK(BaseAIClient):
    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    def __init__(self, api_key: str, timeout: int = 60): super().__init__(api_key, self.BASE_URL, timeout)
    def chat(self, model: str, messages, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> str:
        payload = {"model": model, "messages": _normalize_messages(messages), "temperature": temperature}
        if max_tokens is not None: payload["max_tokens"] = max_tokens
        payload.update(kwargs); data = self._post("/chat/completions", payload)
        return data["choices"][0]["message"].get("content") or ""

def quick_chat(message: str, api_key: str, base_url: str, model: str = "gpt-3.5-turbo") -> str:
    with OpenAICompatible(base_url, api_key) as client: return client.chat(model, message)
