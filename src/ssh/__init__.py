# -*- coding: utf-8 -*-
"""
lib-common.ssh: SSH连接模块

支持：
- 私钥连接
- 密码连接
- 命令执行
- 文件上传下载
- SFTP支持

示例:
    from lib_common.ssh import SSHClient
    
    client = SSHClient("192.168.1.1", key_path="./key.pem")
    result = client.exec("ls -la")
    print(result.stdout)
    client.close()
"""

import paramiko
import os
from typing import Optional, Union
from dataclasses import dataclass


@dataclass
class ExecResult:
    """命令执行结果"""
    stdout: str
    stderr: str
    code: int
    
    def __str__(self):
        return self.stdout
    
    @property
    def success(self) -> bool:
        return self.code == 0


class SSHClient:
    """SSH客户端封装"""
    
    def __init__(
        self,
        host: str,
        port: int = 22,
        username: str = "root",
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        timeout: int = 10
    ):
        """
        初始化SSH客户端
        
        Args:
            host: 服务器地址
            port: 端口，默认22
            username: 用户名，默认root
            password: 密码（与key_path二选一）
            key_path: 私钥路径（与password二选一）
            timeout: 超时时间(秒)
        """
        self.host = host
        self.port = port
        self.username = username
        self.timeout = timeout
        self._client: Optional[paramiko.SSHClient] = None
        self._password = password
        self._key_path = key_path
    
    def _get_client(self) -> paramiko.SSHClient:
        """获取或创建SSH连接"""
        if self._client is None or not self._client.get_transport().is_active():
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self._key_path:
                # 私钥连接
                os.chmod(self._key_path, 0o600)
                pkey = paramiko.RSAKey.from_private_key_file(self._key_path)
                self._client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=pkey,
                    timeout=self.timeout
                )
            else:
                # 密码连接
                self._client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self._password,
                    timeout=self.timeout
                )
        
        return self._client
    
    def exec(self, command: str, timeout: Optional[int] = None) -> ExecResult:
        """
        执行远程命令
        
        Args:
            command: 要执行的命令
            timeout: 命令超时时间
        
        Returns:
            ExecResult对象
        """
        client = self._get_client()
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        
        return ExecResult(
            stdout=stdout.read().decode(),
            stderr=stderr.read().decode(),
            code=stdout.channel.recv_exit_status()
        )
    
    def exec_stream(self, command: str, callback):
        """
        流式执行命令（实时输出）
        
        Args:
            command: 命令
            callback: 回调函数，接收每行输出
        """
        client = self._get_client()
        stdin, stdout, stderr = client.exec_command(command)
        
        for line in stdout:
            callback(line.decode().rstrip())
        
        return ExecResult(
            stdout="",
            stderr=stderr.read().decode(),
            code=stdout.channel.recv_exit_status()
        )
    
    def upload(self, local_path: str, remote_path: str):
        """上传文件"""
        client = self._get_client()
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    
    def download(self, remote_path: str, local_path: str):
        """下载文件"""
        client = self._get_client()
        sftp = client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
    
    def close(self):
        """关闭连接"""
        if self._client:
            self._client.close()
            self._client = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __del__(self):
        self.close()


def quick_exec(
    host: str, 
    key_path: str, 
    command: str,
    username: str = "root"
) -> str:
    """
    快速执行单条命令
    
    Args:
        host: 服务器地址
        key_path: 私钥路径
        command: 命令
        username: 用户名
    
    Returns:
        命令输出字符串
    """
    with SSHClient(host, key_path=key_path, username=username) as client:
        result = client.exec(command)
        return result.stdout


# 兼容旧代码
def ssh_connect_with_key(host: str, key_path: str, username: str = "root", 
                         timeout: int = 10) -> SSHClient:
    """兼容旧API"""
    return SSHClient(host, key_path=key_path, username=username, timeout=timeout)


def ssh_exec(ssh_client: SSHClient, command: str) -> ExecResult:
    """兼容旧API"""
    return ssh_client.exec(command)
