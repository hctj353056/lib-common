# -*- coding: utf-8 -*-
"""HTTP client with reusable sessions and a lightweight response wrapper."""
import json as json_module, os, tempfile
from dataclasses import dataclass
from typing import Any, Dict, Optional
import requests

@dataclass
class HttpResponse:
    status_code: int
    text: str
    headers: Dict
    content: Optional[bytes] = None
    url: str = ""
    reason: str = ""
    encoding: Optional[str] = "utf-8"
    def __post_init__(self):
        if self.content is None: self.content = self.text.encode(self.encoding or "utf-8")
    def json(self) -> Any: return json_module.loads(self.text)
    @property
    def ok(self) -> bool: return 200 <= self.status_code < 300
    def raise_for_status(self) -> None:
        if self.status_code >= 400: raise requests.HTTPError("HTTP %s %s for %s" % (self.status_code, self.reason, self.url))

class HttpClient:
    def __init__(self, timeout: int = 30, headers: Optional[Dict] = None, session=None):
        if timeout <= 0: raise ValueError("timeout must be > 0")
        self.timeout = timeout; self.default_headers = dict(headers or {}); self.session = session or requests.Session()
    def request(self, method: str, url: str, **kwargs) -> HttpResponse:
        headers = {**self.default_headers, **kwargs.pop("headers", {})}
        response = self.session.request(method=method.upper(), url=url, headers=headers, timeout=kwargs.pop("timeout", self.timeout), **kwargs)
        return HttpResponse(response.status_code, response.text, dict(response.headers), response.content, response.url, response.reason, response.encoding or "utf-8")
    def _request(self, method: str, url: str, **kwargs) -> HttpResponse: return self.request(method, url, **kwargs)
    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> HttpResponse: return self.request("GET", url, params=params, **kwargs)
    def post(self, url: str, data: Any = None, json: Any = None, **kwargs) -> HttpResponse: return self.request("POST", url, data=data, json=json, **kwargs)
    def put(self, url: str, data: Any = None, json: Any = None, **kwargs) -> HttpResponse: return self.request("PUT", url, data=data, json=json, **kwargs)
    def patch(self, url: str, data: Any = None, json: Any = None, **kwargs) -> HttpResponse: return self.request("PATCH", url, data=data, json=json, **kwargs)
    def delete(self, url: str, **kwargs) -> HttpResponse: return self.request("DELETE", url, **kwargs)
    def head(self, url: str, **kwargs) -> HttpResponse: return self.request("HEAD", url, **kwargs)
    def download(self, url: str, path: str, chunk_size: int = 8192, **kwargs) -> str:
        """Download to a temporary file, then atomically replace the destination."""
        if chunk_size <= 0: raise ValueError("chunk_size must be > 0")
        headers = {**self.default_headers, **kwargs.pop("headers", {})}
        response = self.session.get(url, headers=headers, stream=True, timeout=kwargs.pop("timeout", self.timeout), **kwargs)
        response.raise_for_status(); destination = os.path.abspath(path); directory = os.path.dirname(destination)
        fd, temporary = tempfile.mkstemp(prefix=".download-", dir=directory)
        try:
            with os.fdopen(fd, "wb") as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk: file.write(chunk)
            os.replace(temporary, destination)
        except Exception:
            try: os.unlink(temporary)
            except OSError: pass
            raise
        finally: response.close()
        return path
    def close(self): self.session.close()
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.close()

def fetch(url: str, method: str = "GET", **kwargs) -> HttpResponse:
    with HttpClient() as client: return client.request(method, url, **kwargs)
