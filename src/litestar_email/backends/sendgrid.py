"""SendGrid email backend using the SendGrid v3 HTTP API."""

import base64
from typing import TYPE_CHECKING, Any

from litestar_email.backends.base import BaseEmailBackend
from litestar_email.exceptions import (
    EmailBackendError,
    EmailDeliveryError,
    EmailRateLimitError,
)

if TYPE_CHECKING:
    import httpx

    from litestar_email.config import SendGridConfig
    from litestar_email.message import EmailMessage

# Import guard for optional dependency
try:
    import httpx as httpx_module
except ImportError:
    httpx_module = None  # type: ignore[assignment]

HAS_HTTPX = httpx_module is not None

__all__ = ("SendGridBackend",)

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


class SendGridBackend(BaseEmailBackend):
    """SendGrid email backend using the v3 HTTP API.

    This backend sends emails via SendGrid's HTTP API, which doesn't require
    SMTP ports and works on any hosting plan.

    The backend requires the ``httpx`` package to be installed.
    Install it with::

        pip install litestar-email[sendgrid]

    Example:
        Basic usage::

            config = EmailConfig(
                backend="sendgrid",
                from_email="noreply@example.com",
                backend_config=SendGridConfig(api_key="SG.xxx..."),
            )
            backend = get_backend("sendgrid", config=config)
            async with backend:
                await backend.send_messages([message])

    Get your API key at: https://app.sendgrid.com/settings/api_keys
    """

    __slots__ = ("_client", "_config")

    def __init__(
        self,
        config: "SendGridConfig | None" = None,
        fail_silently: bool = False,
        default_from_email: str | None = None,
        default_from_name: str | None = None,
    ) -> None:
        """Initialize SendGrid backend.

        Args:
            config: SendGrid configuration settings. If None, defaults are used.
            fail_silently: If True, suppress exceptions during send.
            default_from_email: Default sender email when message.from_email is missing.
            default_from_name: Default sender name when message.from_email has no name.

        Raises:
            EmailBackendError: If httpx is not installed.
        """
        if not HAS_HTTPX:
            msg = "httpx is required for SendGrid backend. Install with: pip install litestar-email[sendgrid]"
            raise EmailBackendError(msg)

        super().__init__(
            fail_silently=fail_silently,
            default_from_email=default_from_email,
            default_from_name=default_from_name,
        )

        # Use provided config or create default
        if config is None:
            from litestar_email.config import SendGridConfig

            config = SendGridConfig()

        self._config = config
        self._client: "httpx.AsyncClient | None" = None

    async def open(self) -> bool:
        """Open an HTTP client for sending emails.

        Returns:
            True if a new client was created, False if reusing existing.
        """
        if self._client is not None:
            return False

        assert httpx_module is not None  # noqa: S101 # Checked in __init__
        self._client = httpx_module.AsyncClient(
            headers={
                "Authorization": f"Bearer {self._config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=float(self._config.timeout),
        )
        return True

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception:
                if not self.fail_silently:
                    raise
            finally:
                self._client = None

    async def send_messages(self, messages: list["EmailMessage"]) -> int:
        """Send messages via SendGrid API.

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
                        msg = f"Failed to send email to {message.to} via SendGrid"
                        raise EmailDeliveryError(msg) from exc
            return num_sent
        finally:
            if new_connection:
                await self.close()

    async def _send_message(self, message: "EmailMessage") -> None:
        """Send a single message via SendGrid API.

        Args:
            message: The email message to send.

        Raises:
            RuntimeError: If client is not initialized.
            EmailRateLimitError: If rate limited by the API.
            EmailDeliveryError: If the API returns an error.
        """
        if self._client is None:
            msg = "SendGrid client not initialized"
            raise RuntimeError(msg)

        # Build personalizations (recipients)
        personalization: dict[str, Any] = {
            "to": [{"email": email} for email in message.to],
        }
        if message.cc:
            personalization["cc"] = [{"email": email} for email in message.cc]
        if message.bcc:
            personalization["bcc"] = [{"email": email} for email in message.bcc]

        # Build the request payload
        from_email, from_name, _ = self._resolve_from(message)
        from_payload: dict[str, str] = {"email": from_email}
        if from_name:
            from_payload["name"] = from_name
        payload: dict[str, Any] = {
            "personalizations": [personalization],
            "subject": message.subject,
            "from": from_payload,
        }

        # Build content array
        content: list[dict[str, str]] = []
        if message.body:
            content.append({"type": "text/plain", "value": message.body})

        # Add HTML alternative if present
        for alt_content, mimetype in message.alternatives:
            if mimetype == "text/html":
                content.append({"type": "text/html", "value": alt_content})
                break

        if content:
            payload["content"] = content

        # Add reply-to
        if message.reply_to:
            payload["reply_to"] = {"email": message.reply_to[0]}

        # Add custom headers
        if message.headers:
            payload["headers"] = message.headers

        # Add attachments with base64 encoding
        if message.attachments:
            payload["attachments"] = [
                {
                    "filename": filename,
                    "content": base64.b64encode(attach_content).decode("ascii"),
                    "type": mimetype,
                }
                for filename, attach_content, mimetype in message.attachments
            ]

        response = await self._client.post(SENDGRID_API_URL, json=payload)

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after else None
            msg = "SendGrid API rate limit exceeded"
            raise EmailRateLimitError(msg, retry_after=retry_seconds)

        # Handle other errors (SendGrid returns 202 on success)
        if response.status_code >= 400:
            error_detail = response.text
            msg = f"SendGrid API error: {response.status_code} - {error_detail}"
            raise EmailDeliveryError(msg)
