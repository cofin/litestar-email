from typing import TYPE_CHECKING, ClassVar

from litestar_email.backends.base import BaseEmailBackend

if TYPE_CHECKING:
    from litestar_email.message import EmailMessage

__all__ = ("InMemoryBackend",)


class InMemoryBackend(BaseEmailBackend):
    """Email backend that stores messages in memory.

    Useful for unit and integration testing. All messages are stored
    in a class-level list that persists across instances.

    Example:
        Testing with the in-memory backend::

            from litestar_email.backends import InMemoryBackend

            # In tests
            InMemoryBackend.clear()  # Reset before test
            # ... code that sends email ...
            assert len(InMemoryBackend.outbox) == 1
            assert InMemoryBackend.outbox[0].subject == "Welcome"
    """

    __slots__ = ()

    outbox: ClassVar[list["EmailMessage"]] = []
    """Class-level storage for sent messages. Shared across all instances."""

    async def send_messages(self, messages: list["EmailMessage"]) -> int:
        """Store messages in the class-level outbox.

        Args:
            messages: List of messages to store.

        Returns:
            The number of messages stored.
        """
        self.outbox.extend(messages)
        return len(messages)

    @classmethod
    def clear(cls) -> None:
        """Clear all stored messages.

        Call this in test setup/teardown to reset state between tests.
        """
        cls.outbox.clear()
