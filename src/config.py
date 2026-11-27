"""Environment-backed configuration helpers with explicit type conversion."""
import os
from typing import Any, Mapping, Optional


def get_env(name: str, default: Optional[str] = None, *, required: bool = False) -> Optional[str]:
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        raise ValueError("Required environment variable is missing: %s" % name)
    return value


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("Invalid boolean value for %s: %r" % (name, value))


def env_int(name: str, default: int, *, minimum: Optional[int] = None, maximum: Optional[int] = None) -> int:
    value = os.getenv(name)
    try:
        result = default if value is None else int(value)
    except (TypeError, ValueError) as error:
        raise ValueError("Invalid integer value for %s: %r" % (name, value)) from error
    if minimum is not None and result < minimum:
        raise ValueError("%s must be >= %s" % (name, minimum))
    if maximum is not None and result > maximum:
        raise ValueError("%s must be <= %s" % (name, maximum))
    return result


class Settings:
    """Small mapping wrapper for application settings; values are not secret-redacted."""
    def __init__(self, values: Optional[Mapping[str, Any]] = None, prefix: str = ""):
        self.values = dict(values or {})
        self.prefix = prefix

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.values:
            return self.values[key]
        return os.getenv(self.prefix + key, default)

    def require(self, key: str) -> Any:
        value = self.get(key)
        if value is None or value == "":
            raise ValueError("Required setting is missing: %s" % (self.prefix + key))
        return value

    def as_dict(self) -> dict:
        return dict(self.values)
