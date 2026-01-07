"""Mailgun email backend using the Mailgun HTTP API."""

from typing import TYPE_CHECKING, Any

from litestar_email.backends.base import BaseEmailBackend
from litestar_email.exceptions import (
    EmailDeliveryError,
    EmailRateLimitError,
)
from litestar_email.utils.module_loader import ensure_httpx

if TYPE_CHECKING:
    from litestar_email.config import MailgunConfig
    from litestar_email.message import EmailMessage
    from litestar_email.transports.base import HTTPTransport

__all__ = ("MailgunBackend",)

MAILGUN_US_URL = "https://api.mailgun.net"
MAILGUN_EU_URL = "https://api.eu.mailgun.net"


class MailgunBackend(BaseEmailBackend):
    """Mailgun email backend using the HTTP API.

    This backend sends emails via Mailgun's HTTP API, supporting both
    US and EU regional endpoints for GDPR compliance.

    The backend uses httpx by default (bundled with Litestar), but can be
    configured to use aiohttp or a custom HTTP transport.

    Example:
        Basic usage::

            config = EmailConfig(
                backend="mailgun",
                from_email="noreply@example.com",
                backend_config=MailgunConfig(
                    api_key="key-xxx...",
                    domain="mg.example.com",
                ),
            )
            backend = get_backend("mailgun", config=config)
            async with backend:
                await backend.send_messages([message])

        Using EU region::

            backend_config=MailgunConfig(
                api_key="key-xxx...",
                domain="mg.example.com",
                region="eu",
            )

        Using aiohttp transport::

            backend_config=MailgunConfig(
                api_key="key-xxx...",
                domain="mg.example.com",
                http_transport="aiohttp",
            )

    Get your API key at: https://app.mailgun.com/settings/api_keys
    """

    __slots__ = ("_config", "_transport")

    def __init__(
        self,
        config: "MailgunConfig | None" = None,
        fail_silently: bool = False,
        default_from_email: str | None = None,
        default_from_name: str | None = None,
    ) -> None:
        """Initialize Mailgun backend.

        Args:
            config: Mailgun configuration settings. If None, defaults are used.
            fail_silently: If True, suppress exceptions during send.
            default_from_email: Default sender email when message.from_email is missing.
            default_from_name: Default sender name when message.from_email has no name.

        Note:
            May raise ``MissingDependencyError`` if the configured HTTP transport
            is not installed.
        """
        super().__init__(
            fail_silently=fail_silently,
            default_from_email=default_from_email,
            default_from_name=default_from_name,
        )

        # Use provided config or create default
        if config is None:
            from litestar_email.config import MailgunConfig

            config = MailgunConfig()

        # Check httpx availability if using default transport
        if config.http_transport == "httpx":
            ensure_httpx()

        self._config = config
        self._transport: "HTTPTransport | None" = None

    async def open(self) -> bool:
        """Open an HTTP transport for sending emails.

        Returns:
            True if a new transport was created, False if reusing existing.
        """
        if self._transport is not None:
            return False

        from litestar_email.transports import get_transport

        # Select base URL based on region
        base_url = MAILGUN_EU_URL if self._config.region == "eu" else MAILGUN_US_URL

        self._transport = get_transport(self._config.http_transport)
        await self._transport.open(
            auth=("api", self._config.api_key),
            base_url=base_url,
            timeout=float(self._config.timeout),
        )
        return True

    async def close(self) -> None:
        """Close the HTTP transport."""
        if self._transport is not None:
            try:
                await self._transport.close()
            except Exception:
                if not self.fail_silently:
                    raise
            finally:
                self._transport = None

    async def send_messages(self, messages: list["EmailMessage"]) -> int:
        """Send messages via Mailgun API.

        Args:
            messages: List of EmailMessage instances to send.

        Returns:
            Number of messages successfully sent.

        Raises:
            EmailDeliveryError: If sending fails and fail_silently is False.
            EmailRateLimitError: If rate limited by the API.
        """
        if not messages:
            return 0

        new_connection = await self.open()

        try:
            num_sent = 0
            for message in messages:
                try:
                    await self._send_message(message)
                    num_sent += 1
                except EmailRateLimitError:
                    # Re-raise rate limit errors for proper handling
                    raise
                except Exception as exc:
                    if not self.fail_silently:
                        msg = f"Failed to send email to {message.to} via Mailgun"
                        raise EmailDeliveryError(msg) from exc
            return num_sent
        finally:
            if new_connection:
                await self.close()

    async def _send_message(self, message: "EmailMessage") -> None:
        """Send a single message via Mailgun API.

        Args:
            message: The email message to send.

        Raises:
            RuntimeError: If transport is not initialized.
            EmailRateLimitError: If rate limited by the API.
            EmailDeliveryError: If the API returns an error.
        """
        if self._transport is None:
            msg = "Mailgun transport not initialized"
            raise RuntimeError(msg)

        # Build the request payload as form data
        _, _, from_formatted = self._resolve_from(message)
        data: dict[str, Any] = {
            "from": from_formatted,
            "to": ",".join(message.to),
            "subject": message.subject,
        }

        # Add text body
        if message.body:
            data["text"] = message.body

        # Add HTML alternative if present
        for content, mimetype in message.alternatives:
            if mimetype == "text/html":
                data["html"] = content
                break

        # Add optional fields
        if message.cc:
            data["cc"] = ",".join(message.cc)
        if message.bcc:
            data["bcc"] = ",".join(message.bcc)
        if message.reply_to:
            # Mailgun uses h:Reply-To header format
            data["h:Reply-To"] = message.reply_to[0]

        # Add custom headers with h: prefix
        if message.headers:
            for key, value in message.headers.items():
                data[f"h:{key}"] = value

        # Build files list for attachments
        files: list[tuple[str, tuple[str, bytes, str]]] | None = None
        if message.attachments:
            files = [
                ("attachment", (filename, content, mimetype)) for filename, content, mimetype in message.attachments
            ]

        response = await self._transport.post(
            f"/v3/{self._config.domain}/messages",
            data=data,
            files=files,
        )

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = response.get_header("Retry-After")
            retry_seconds = int(retry_after) if retry_after else None
            msg = "Mailgun API rate limit exceeded"
            raise EmailRateLimitError(msg, retry_after=retry_seconds)

        # Handle other errors (Mailgun returns 200 on success)
        if response.status_code >= 400:
            error_detail = await response.text()
            msg = f"Mailgun API error: {response.status_code} - {error_detail}"
            raise EmailDeliveryError(msg)
