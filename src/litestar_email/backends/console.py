import sys
from typing import TYPE_CHECKING, TextIO

from litestar_email.backends.base import BaseEmailBackend

if TYPE_CHECKING:
    from litestar_email.message import EmailMessage

__all__ = ("ConsoleBackend",)


class ConsoleBackend(BaseEmailBackend):
    """Email backend that writes messages to a stream (default: stdout).

    Useful for local development and debugging. Prints email metadata
    and content to the console in a human-readable format.

    Example:
        Basic configuration::

            from litestar_email import EmailConfig

            config = EmailConfig(backend="console")
    """

    __slots__ = ("stream",)

    def __init__(
        self,
        fail_silently: bool = False,
        stream: TextIO | None = None,
        default_from_email: str | None = None,
        default_from_name: str | None = None,
    ) -> None:
        """Initialize the console backend.

        Args:
            fail_silently: If True, exceptions are suppressed.
            stream: Output stream. Defaults to sys.stdout.
            default_from_email: Default sender email when message.from_email is missing.
            default_from_name: Default sender name when message.from_email has no name.
        """
        super().__init__(
            fail_silently=fail_silently,
            default_from_email=default_from_email,
            default_from_name=default_from_name,
        )
        self.stream = stream or sys.stdout

    async def send_messages(self, messages: list["EmailMessage"]) -> int:
        """Write email messages to the stream.

        Args:
            messages: List of messages to output.

        Returns:
            The number of messages written.
        """
        count = 0
        for message in messages:
            self._write_message(message)
            count += 1
        return count

    def _write_message(self, message: "EmailMessage") -> None:
        """Write a single message to the stream.

        Args:
            message: The email message to write.
        """
        separator = "-" * 60
        self.stream.write(f"{separator}\n")
        self.stream.write(f"Subject: {message.subject}\n")
        _, _, from_formatted = self._resolve_from(message)
        self.stream.write(f"From: {from_formatted}\n")
        self.stream.write(f"To: {', '.join(message.to)}\n")

        if message.cc:
            self.stream.write(f"Cc: {', '.join(message.cc)}\n")

        if message.bcc:
            self.stream.write(f"Bcc: {', '.join(message.bcc)}\n")

        if message.reply_to:
            self.stream.write(f"Reply-To: {', '.join(message.reply_to)}\n")

        if message.headers:
            for key, value in message.headers.items():
                self.stream.write(f"{key}: {value}\n")

        self.stream.write(f"\n{message.body}\n")

        for content, mimetype in message.alternatives:
            self.stream.write(f"\n--- Alternative ({mimetype}) ---\n")
            self.stream.write(f"{content}\n")

        if message.attachments:
            self.stream.write("\nAttachments:\n")
            for filename, _, mimetype in message.attachments:
                self.stream.write(f"  - {filename} ({mimetype})\n")

        self.stream.write(f"{separator}\n\n")
        self.stream.flush()
