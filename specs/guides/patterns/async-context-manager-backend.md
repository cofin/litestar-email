# Pattern: Async Context Manager Backend

## When to Use

When implementing backends that manage connections (HTTP clients, SMTP connections, etc.), use the async context manager pattern for:

1. Proper resource cleanup
2. Connection pooling support
3. Consistent API across all backends

## Implementation

```python
from typing import TYPE_CHECKING

from typing_extensions import Self

from litestar_email.backends.base import BaseEmailBackend

if TYPE_CHECKING:
    from litestar_email.message import EmailMessage


class SomeBackend(BaseEmailBackend):
    __slots__ = ("_connection",)

    def __init__(self, fail_silently: bool = False) -> None:
        super().__init__(fail_silently=fail_silently)
        self._connection: SomeConnectionType | None = None

    async def open(self) -> bool:
        """Open a connection.

        Returns:
            True if a new connection was opened, False if reusing existing.
        """
        if self._connection is not None:
            return False  # Already connected

        self._connection = await create_connection()
        return True

    async def close(self) -> None:
        """Close the connection."""
        if self._connection is not None:
            try:
                await self._connection.close()
            except Exception:
                if not self.fail_silently:
                    raise
            finally:
                self._connection = None

    async def send_messages(self, messages: list["EmailMessage"]) -> int:
        """Send messages with automatic connection management."""
        if not messages:
            return 0

        new_connection = await self.open()

        try:
            num_sent = 0
            for message in messages:
                try:
                    await self._send_message(message)
                    num_sent += 1
                except Exception as exc:
                    if not self.fail_silently:
                        raise EmailDeliveryError(...) from exc
            return num_sent
        finally:
            if new_connection:
                await self.close()
```

## Key Points

1. **Return boolean from open()**: True if new connection, False if reusing
2. **Check existing connection**: Prevent double-open issues
3. **Finally block in close()**: Always reset `_connection = None`
4. **Track new_connection**: Only close if we opened the connection ourselves
5. **Respect fail_silently**: Suppress exceptions when configured

## Usage

```python
# Single send (connection opened/closed per call)
await backend.send_messages([message1])
await backend.send_messages([message2])

# Batched sends (connection reused)
async with backend:
    await backend.send_messages([message1])
    await backend.send_messages([message2])
    await backend.send_messages([message3])
```

## Example Files

- `src/litestar_email/backends/base.py` - Base implementation
- `src/litestar_email/backends/smtp.py` - SMTP connection pooling
- `src/litestar_email/backends/resend.py` - HTTP client reuse

## Notes

- The base class provides `__aenter__` and `__aexit__` implementations
- Backends only need to override `open()`, `close()`, and `send_messages()`
- Use `typing_extensions.Self` for proper return type hints on Python 3.10
