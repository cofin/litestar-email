# Litestar Framework Skill

Quick reference for Litestar plugin development patterns used in litestar-email.

## Context7 Lookup

```python
# Resolve Litestar library ID
mcp__context7__resolve-library-id(
    query="Litestar plugin system",
    libraryName="litestar"
)

# Query specific topics
mcp__context7__query-docs(
    libraryId="/litestar-org/litestar",
    query="How to create a plugin with InitPluginProtocol"
)
```

## Plugin Pattern

### Basic Plugin Structure

```python
from typing import TYPE_CHECKING

from litestar.plugins import InitPluginProtocol

if TYPE_CHECKING:
    from litestar.config.app import AppConfig

    from litestar_email.config import EmailConfig

__all__ = ("EmailPlugin",)


class EmailPlugin(InitPluginProtocol):
    """Email plugin for Litestar applications.

    Attributes:
        config: Email configuration.
    """

    __slots__ = ("config",)

    def __init__(self, config: "EmailConfig") -> None:
        """Initialize the plugin.

        Args:
            config: Email configuration instance.
        """
        self.config = config

    def on_app_init(self, app_config: "AppConfig") -> "AppConfig":
        """Initialize plugin during app startup.

        Args:
            app_config: The application configuration.

        Returns:
            Modified application configuration.
        """
        # Plugin initialization logic
        return app_config
```

### Plugin Registration

```python
from litestar import Litestar
from litestar_email import EmailPlugin, EmailConfig

app = Litestar(
    plugins=[
        EmailPlugin(config=EmailConfig(
            backend="console",
            from_email="noreply@example.com",
        ))
    ]
)
```

## Backend Pattern

### Abstract Base Backend

```python
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from litestar_email.message import EmailMessage

__all__ = ("BaseEmailBackend",)


class BaseEmailBackend(ABC):
    """Abstract base class for email backends."""

    __slots__ = ("fail_silently",)

    def __init__(self, fail_silently: bool = False) -> None:
        self.fail_silently = fail_silently

    async def open(self) -> bool:
        """Open connection. Override for connection pooling."""
        return True

    async def close(self) -> None:
        """Close connection. Override to clean up."""
        pass

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    @abstractmethod
    async def send_messages(self, messages: list["EmailMessage"]) -> int:
        """Send messages. Must be implemented."""
        ...
```

### Concrete Backend Implementation

```python
from typing import TYPE_CHECKING

from litestar_email.backends.base import BaseEmailBackend

if TYPE_CHECKING:
    from litestar_email.message import EmailMessage

__all__ = ("ConsoleBackend",)


class ConsoleBackend(BaseEmailBackend):
    """Backend that prints emails to console."""

    __slots__ = ()

    async def send_messages(self, messages: list["EmailMessage"]) -> int:
        sent_count = 0
        for message in messages:
            print(f"Subject: {message.subject}")
            print(f"To: {', '.join(message.to)}")
            print(f"Body: {message.body}")
            print("-" * 40)
            sent_count += 1
        return sent_count
```

### Backend Registry

```python
from litestar_email.backends.base import BaseEmailBackend
from litestar_email.backends.console import ConsoleBackend
from litestar_email.backends.memory import InMemoryBackend

_BACKEND_REGISTRY: dict[str, type[BaseEmailBackend]] = {}


def register_backend(name: str, backend_class: type[BaseEmailBackend]) -> None:
    """Register a backend by name."""
    _BACKEND_REGISTRY[name] = backend_class


def get_backend_class(name: str) -> type[BaseEmailBackend]:
    """Get backend class by name."""
    return _BACKEND_REGISTRY[name]


def get_backend(name: str, **kwargs) -> BaseEmailBackend:
    """Get backend instance by name."""
    return get_backend_class(name)(**kwargs)


# Register built-in backends
register_backend("console", ConsoleBackend)
register_backend("memory", InMemoryBackend)
```

## Configuration Pattern

```python
from dataclasses import dataclass

__all__ = ("EmailConfig",)


@dataclass(slots=True)
class EmailConfig:
    """Configuration for the EmailPlugin.

    Attributes:
        backend: Backend name or import path.
        from_email: Default sender email.
        from_name: Default sender name.
        fail_silently: Suppress exceptions if True.
    """

    backend: str = "console"
    from_email: str = "noreply@localhost"
    from_name: str = ""
    fail_silently: bool = False
```

## Testing Pattern

```python
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar_email import EmailConfig, EmailPlugin

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def email_config() -> "EmailConfig":
    from litestar_email import EmailConfig
    return EmailConfig(backend="memory")


@pytest.fixture
def app(email_config: "EmailConfig") -> "Litestar":
    from litestar import Litestar
    from litestar_email import EmailPlugin
    return Litestar(plugins=[EmailPlugin(config=email_config)])


async def test_backend_sends_message(email_config: "EmailConfig") -> None:
    from litestar_email import EmailMessage, get_backend
    from litestar_email.backends import InMemoryBackend

    InMemoryBackend.clear()

    backend = get_backend(email_config.backend)
    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    async with backend:
        sent = await backend.send_messages([message])

    assert sent == 1
    assert len(InMemoryBackend.outbox) == 1
```

## Project Files Reference

| File | Purpose |
|------|---------|
| `src/litestar_email/__init__.py` | Public exports |
| `src/litestar_email/config.py` | EmailConfig dataclass |
| `src/litestar_email/plugin.py` | EmailPlugin class |
| `src/litestar_email/message.py` | EmailMessage classes |
| `src/litestar_email/backends/base.py` | BaseEmailBackend ABC |
| `src/litestar_email/backends/__init__.py` | Backend registry |
| `src/tests/conftest.py` | Test fixtures |
