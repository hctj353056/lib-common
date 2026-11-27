# -*- coding: utf-8 -*-
"""SSH/SFTP helpers with explicit host-key trust and structured results."""
import os
import paramiko
from dataclasses import dataclass
from typing import Optional, Callable, Any


@dataclass
class ExecResult:
    stdout: str
    stderr: str
    code: int

    def __str__(self):
        return self.stdout

    @property
    def success(self) -> bool:
        return self.code == 0


class SSHClient:
    def __init__(self, host: str, port: int = 22, username: str = "root",
                 password: Optional[str] = None, key_path: Optional[str] = None,
                 timeout: int = 10, *, known_hosts: Optional[str] = None,
                 allow_unknown_hosts: bool = False, passphrase: Optional[str] = None):
        if not host:
            raise ValueError("host must not be empty")
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        self.host, self.port, self.username = host, port, username
        self.timeout = timeout
        self._password, self._key_path, self._passphrase = password, key_path, passphrase
        self._known_hosts = known_hosts
        self._allow_unknown_hosts = allow_unknown_hosts
        self._client: Optional[paramiko.SSHClient] = None

    def _load_private_key(self):
        errors = []
        key_types = [paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.RSAKey]
        if hasattr(paramiko, "DSSKey"):
            key_types.append(paramiko.DSSKey)
        for key_type in key_types:
            try:
                return key_type.from_private_key_file(self._key_path, password=self._passphrase)
            except (paramiko.SSHException, IOError, ValueError) as error:
                errors.append(error)
        raise paramiko.SSHException("Unable to load private key: %s" % self._key_path) from errors[-1]

    def _get_client(self) -> paramiko.SSHClient:
        transport = self._client.get_transport() if self._client is not None else None
        if self._client is not None and transport is not None and transport.is_active():
            return self._client
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        if self._known_hosts:
            client.load_host_keys(self._known_hosts)
        # Reject unknown keys by default; opting in to AutoAddPolicy is explicit.
        policy = paramiko.AutoAddPolicy() if self._allow_unknown_hosts else paramiko.RejectPolicy()
        client.set_missing_host_key_policy(policy)
        options = {"hostname": self.host, "port": self.port, "username": self.username,
                   "timeout": self.timeout, "banner_timeout": self.timeout,
                   "auth_timeout": self.timeout}
        if self._key_path:
            options["pkey"] = self._load_private_key()
        else:
            options["password"] = self._password
        try:
            client.connect(**options)
        except Exception:
            client.close()
            raise
        self._client = client
        return client

    def exec(self, command: str, timeout: Optional[int] = None) -> ExecResult:
        client = self._get_client()
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout or self.timeout)
        return ExecResult(stdout.read().decode("utf-8", errors="replace"),
                          stderr.read().decode("utf-8", errors="replace"),
                          stdout.channel.recv_exit_status())

    def exec_stream(self, command: str, callback: Callable[[str], Any],
                    timeout: Optional[int] = None) -> ExecResult:
        client = self._get_client()
        _, stdout, stderr = client.exec_command(command, timeout=timeout or self.timeout)
        captured = []
        for line in stdout:
            text = line.decode("utf-8", errors="replace") if isinstance(line, bytes) else line
            text = text.rstrip("\r\n")
            captured.append(text)
            callback(text)
        return ExecResult("\n".join(captured),
                          stderr.read().decode("utf-8", errors="replace"),
                          stdout.channel.recv_exit_status())

    def upload(self, local_path: str, remote_path: str):
        with self._get_client().open_sftp() as sftp:
            sftp.put(local_path, remote_path)

    def download(self, remote_path: str, local_path: str):
        with self._get_client().open_sftp() as sftp:
            sftp.get(remote_path, local_path)

    def close(self):
        if self._client is not None:
            try:
                self._client.close()
            finally:
                self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def quick_exec(host: str, key_path: str, command: str, username: str = "root") -> str:
    with SSHClient(host, key_path=key_path, username=username) as client:
        return client.exec(command).stdout


def ssh_connect_with_key(host: str, key_path: str, username: str = "root",
                         timeout: int = 10) -> SSHClient:
    return SSHClient(host, key_path=key_path, username=username, timeout=timeout)


def ssh_exec(ssh_client: SSHClient, command: str) -> ExecResult:
    return ssh_client.exec(command)
