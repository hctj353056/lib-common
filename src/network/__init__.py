# -*- coding: utf-8 -*-
"""
lib-common.network: 网络请求工具

支持：
- HTTP/HTTPS请求
- 文件下载
- API调用封装

示例:
    from lib_common.network import HttpClient
    
    client = HttpClient()
    response = client.get("https://api.example.com/data")
    print(response.json())
"""

import requests
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class HttpResponse:
    """HTTP响应封装"""
    status_code: int
    text: str
    headers: Dict
    
    def json(self) -> Any:
        return requests.models.Response.json(self)
    
    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300


class HttpClient:
    """HTTP客户端封装"""
    
    def __init__(self, timeout: int = 30, headers: Optional[Dict] = None):
        """
        初始化
        
        Args:
            timeout: 超时时间(秒)
            headers: 默认请求头
        """
        self.timeout = timeout
        self.default_headers = headers or {}
    
    def _request(self, method: str, url: str, **kwargs) -> HttpResponse:
        """发送请求"""
        headers = {**self.default_headers, **kwargs.pop("headers", {})}
        
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            timeout=kwargs.pop("timeout", self.timeout),
            **kwargs
        )
        
        return HttpResponse(
            status_code=response.status_code,
            text=response.text,
            headers=dict(response.headers)
        )
    
    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> HttpResponse:
        """GET请求"""
        return self._request("GET", url, params=params, **kwargs)
    
    def post(self, url: str, data: Any = None, json: Any = None, **kwargs) -> HttpResponse:
        """POST请求"""
        return self._request("POST", url, data=data, json=json, **kwargs)
    
    def put(self, url: str, data: Any = None, json: Any = None, **kwargs) -> HttpResponse:
        """PUT请求"""
        return self._request("PUT", url, data=data, json=json, **kwargs)
    
    def delete(self, url: str, **kwargs) -> HttpResponse:
        """DELETE请求"""
        return self._request("DELETE", url, **kwargs)
    
    def download(self, url: str, path: str, chunk_size: int = 8192):
        """
        下载文件
        
        Args:
            url: 文件URL
            path: 保存路径
            chunk_size: 分块大小
        """
        response = requests.get(url, stream=True, timeout=self.timeout)
        response.raise_for_status()
        
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)


def fetch(url: str, method: str = "GET", **kwargs) -> HttpResponse:
    """
    快速HTTP请求（单次）
    
    Args:
        url: 请求URL
        method: 请求方法
        **kwargs: 其他参数
    
    Returns:
        HttpResponse
    """
    client = HttpClient()
    return client._request(method, url, **kwargs)
