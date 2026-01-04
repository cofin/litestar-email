from abc import ABC, abstractmethod
from email.utils import formataddr, parseaddr
from typing import TYPE_CHECKING

from typing_extensions import Self

if TYPE_CHECKING:
    from litestar_email.message import EmailMessage

__all__ = ("BaseEmailBackend",)


class BaseEmailBackend(ABC):
    """Abstract base class for email backends.

    All email backends must inherit from this class and implement
    the ``send_messages`` method. Backends can optionally override
    ``open`` and ``close`` for connection pooling.

    The class supports async context manager protocol for resource management.

    Example:
        Basic usage with context manager::

            async with get_backend() as backend:
                await backend.send_messages([message])
    """

    __slots__ = ("_default_from_email", "_default_from_name", "fail_silently")

    def __init__(
        self,
        fail_silently: bool = False,
        default_from_email: str | None = None,
        default_from_name: str | None = None,
    ) -> None:
        """Initialize the email backend.

        Args:
            fail_silently: If True, exceptions during sending are suppressed.
            default_from_email: Default sender email when message.from_email is missing.
            default_from_name: Default sender name when message.from_email has no name.
        """
        self.fail_silently = fail_silently
        self._default_from_email = default_from_email
        self._default_from_name = default_from_name

    async def open(self) -> bool:
        """Open a connection to the email server.

        Override this method to implement connection pooling.
        Called automatically when entering the async context manager.

        Returns:
            True if connection was opened, False if already open or not needed.
        """
        return True

    async def close(self) -> None:
        """Close the connection to the email server.

        Override this method to clean up resources.
        Called automatically when exiting the async context manager.
        """

    async def __aenter__(self) -> Self:
        """Enter the async context manager.

        Returns:
            The backend instance.
        """
        await self.open()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit the async context manager.

        Args:
            exc_type: The exception type, if any.
            exc_val: The exception value, if any.
            exc_tb: The exception traceback, if any.
        """
        await self.close()

    def _resolve_from(self, message: "EmailMessage") -> tuple[str, str, str]:
        """Resolve the sender address for a message.

        Args:
            message: The email message.

        Returns:
            Tuple of (email, name, formatted) values.
        """
        raw_from = message.from_email or self._default_from_email or ""
        name, email = parseaddr(raw_from)
        if not name and self._default_from_name:
            name = self._default_from_name
        formatted = formataddr((name, email)) if email else ""
        return email, name, formatted

    @abstractmethod
    async def send_messages(self, messages: list["EmailMessage"]) -> int:
        """Send one or more email messages.

        This method must be implemented by all backends.

        Args:
            messages: A list of EmailMessage instances to send.

        Returns:
            The number of messages successfully sent.

        Raises:
            Exception: If fail_silently is False and sending fails.
        """
        ...
