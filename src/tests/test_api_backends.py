"""Tests for API-based email backends (Resend and SendGrid)."""

import httpx
import pytest
import respx

pytestmark = pytest.mark.anyio


# ==============================================================================
# Resend Backend Tests
# ==============================================================================


def test_resend_backend_requires_httpx() -> None:
    """Test that ResendBackend raises if httpx is not installed."""
    from litestar_email.backends import resend as resend_module
    from litestar_email.exceptions import EmailBackendError

    original = resend_module.HAS_HTTPX
    resend_module.HAS_HTTPX = False

    try:
        with pytest.raises(EmailBackendError, match="httpx is required"):
            resend_module.ResendBackend()
    finally:
        resend_module.HAS_HTTPX = original


def test_resend_backend_default_config() -> None:
    """Test ResendBackend uses default config when none provided."""
    from litestar_email.backends.resend import ResendBackend

    backend = ResendBackend()
    assert backend._config.api_key == ""
    assert backend._config.timeout == 30


def test_resend_backend_custom_config() -> None:
    """Test ResendBackend accepts custom config."""
    from litestar_email.backends.resend import ResendBackend
    from litestar_email.config import ResendConfig

    config = ResendConfig(api_key="re_xxx", timeout=60)
    backend = ResendBackend(config=config)
    assert backend._config.api_key == "re_xxx"
    assert backend._config.timeout == 60


async def test_resend_backend_open_returns_false_when_connected() -> None:
    """Test that open() returns False if already connected."""
    from unittest.mock import MagicMock

    from litestar_email.backends.resend import ResendBackend
    from litestar_email.config import ResendConfig

    config = ResendConfig(api_key="re_xxx")
    backend = ResendBackend(config=config)
    backend._client = MagicMock()

    result = await backend.open()
    assert result is False


async def test_resend_backend_open_creates_client() -> None:
    """Test that open() creates a new HTTP client."""
    from litestar_email.backends.resend import ResendBackend
    from litestar_email.config import ResendConfig

    config = ResendConfig(api_key="re_xxx")
    backend = ResendBackend(config=config)

    result = await backend.open()
    assert result is True
    assert backend._client is not None

    await backend.close()


async def test_resend_backend_close_when_not_connected() -> None:
    """Test that close() does nothing when not connected."""
    from litestar_email.backends.resend import ResendBackend

    backend = ResendBackend()
    backend._client = None

    # Should not raise
    await backend.close()


async def test_resend_backend_send_empty_list() -> None:
    """Test sending empty list returns 0."""
    from litestar_email.backends.resend import ResendBackend

    backend = ResendBackend()
    count = await backend.send_messages([])
    assert count == 0


async def test_resend_backend_send_message_not_connected() -> None:
    """Test _send_message raises if not connected."""
    from litestar_email import EmailMessage
    from litestar_email.backends.resend import ResendBackend

    backend = ResendBackend()
    backend._client = None
    message = EmailMessage(subject="Test", body="Body", to=["test@example.com"])

    with pytest.raises(RuntimeError, match="Resend client not initialized"):
        await backend._send_message(message)


@respx.mock
async def test_resend_backend_send_success() -> None:
    """Test successful email sending via Resend API."""
    from litestar_email import EmailMessage
    from litestar_email.backends.resend import RESEND_API_URL, ResendBackend
    from litestar_email.config import ResendConfig

    respx.post(RESEND_API_URL).mock(return_value=httpx.Response(200, json={"id": "msg_123"}))

    config = ResendConfig(api_key="re_xxx")
    backend = ResendBackend(config=config)

    message = EmailMessage(
        subject="Test",
        body="Body",
        from_email="sender@example.com",
        to=["test@example.com"],
    )

    count = await backend.send_messages([message])
    assert count == 1


@respx.mock
async def test_resend_backend_send_with_all_fields() -> None:
    """Test sending email with all optional fields."""
    from litestar_email import EmailMessage
    from litestar_email.backends.resend import RESEND_API_URL, ResendBackend
    from litestar_email.config import ResendConfig

    route = respx.post(RESEND_API_URL).mock(return_value=httpx.Response(200, json={"id": "msg_123"}))

    config = ResendConfig(api_key="re_xxx")
    backend = ResendBackend(config=config)

    message = EmailMessage(
        subject="Test",
        body="Plain text",
        from_email="sender@example.com",
        to=["test@example.com"],
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
        reply_to=["reply@example.com"],
        headers={"X-Custom": "header"},
    )
    message.attach_alternative("<p>HTML</p>", "text/html")
    message.attach("file.txt", b"content", "text/plain")

    count = await backend.send_messages([message])
    assert count == 1

    # Verify request payload
    request = route.calls.last.request
    import json

    payload = json.loads(request.content)

    assert payload["from"] == "sender@example.com"
    assert payload["to"] == ["test@example.com"]
    assert payload["cc"] == ["cc@example.com"]
    assert payload["bcc"] == ["bcc@example.com"]
    assert payload["reply_to"] == "reply@example.com"
    assert payload["text"] == "Plain text"
    assert payload["html"] == "<p>HTML</p>"
    assert payload["headers"] == {"X-Custom": "header"}
    assert len(payload["attachments"]) == 1
    assert payload["attachments"][0]["filename"] == "file.txt"


@respx.mock
async def test_resend_backend_uses_default_from() -> None:
    """Test default from values are used when message lacks from_email."""
    from litestar_email import EmailConfig, EmailMessage, get_backend
    from litestar_email.backends.resend import RESEND_API_URL
    from litestar_email.config import ResendConfig

    route = respx.post(RESEND_API_URL).mock(return_value=httpx.Response(200, json={"id": "msg_123"}))

    config = EmailConfig(
        backend="resend",
        from_email="noreply@example.com",
        from_name="Litestar",
        backend_config=ResendConfig(api_key="re_xxx"),
    )
    backend = get_backend("resend", config=config)

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    await backend.send_messages([message])

    import json

    payload = json.loads(route.calls.last.request.content)
    assert payload["from"] == "Litestar <noreply@example.com>"


@respx.mock
async def test_resend_backend_rate_limit() -> None:
    """Test rate limit error handling."""
    from litestar_email import EmailMessage
    from litestar_email.backends.resend import RESEND_API_URL, ResendBackend
    from litestar_email.config import ResendConfig
    from litestar_email.exceptions import EmailRateLimitError

    respx.post(RESEND_API_URL).mock(return_value=httpx.Response(429, headers={"Retry-After": "60"}))

    config = ResendConfig(api_key="re_xxx")
    backend = ResendBackend(config=config, fail_silently=False)

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    with pytest.raises(EmailRateLimitError) as exc_info:
        await backend.send_messages([message])

    assert exc_info.value.retry_after == 60


@respx.mock
async def test_resend_backend_api_error() -> None:
    """Test API error handling."""
    from litestar_email import EmailMessage
    from litestar_email.backends.resend import RESEND_API_URL, ResendBackend
    from litestar_email.config import ResendConfig
    from litestar_email.exceptions import EmailDeliveryError

    respx.post(RESEND_API_URL).mock(return_value=httpx.Response(400, json={"message": "Invalid request"}))

    config = ResendConfig(api_key="re_xxx")
    backend = ResendBackend(config=config, fail_silently=False)

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    with pytest.raises(EmailDeliveryError, match="Failed to send email"):
        await backend.send_messages([message])


@respx.mock
async def test_resend_backend_multiple_reply_to() -> None:
    """Test multiple reply-to addresses are handled correctly."""
    from litestar_email import EmailMessage
    from litestar_email.backends.resend import RESEND_API_URL, ResendBackend
    from litestar_email.config import ResendConfig

    route = respx.post(RESEND_API_URL).mock(return_value=httpx.Response(200, json={"id": "msg_123"}))

    config = ResendConfig(api_key="re_xxx")
    backend = ResendBackend(config=config)

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
        reply_to=["reply1@example.com", "reply2@example.com"],
    )

    await backend.send_messages([message])

    import json

    payload = json.loads(route.calls.last.request.content)
    assert payload["reply_to"] == ["reply1@example.com", "reply2@example.com"]


# ==============================================================================
# SendGrid Backend Tests
# ==============================================================================


def test_sendgrid_backend_requires_httpx() -> None:
    """Test that SendGridBackend raises if httpx is not installed."""
    from litestar_email.backends import sendgrid as sendgrid_module
    from litestar_email.exceptions import EmailBackendError

    original = sendgrid_module.HAS_HTTPX
    sendgrid_module.HAS_HTTPX = False

    try:
        with pytest.raises(EmailBackendError, match="httpx is required"):
            sendgrid_module.SendGridBackend()
    finally:
        sendgrid_module.HAS_HTTPX = original


def test_sendgrid_backend_default_config() -> None:
    """Test SendGridBackend uses default config when none provided."""
    from litestar_email.backends.sendgrid import SendGridBackend

    backend = SendGridBackend()
    assert backend._config.api_key == ""
    assert backend._config.timeout == 30


def test_sendgrid_backend_custom_config() -> None:
    """Test SendGridBackend accepts custom config."""
    from litestar_email.backends.sendgrid import SendGridBackend
    from litestar_email.config import SendGridConfig

    config = SendGridConfig(api_key="SG.xxx", timeout=60)
    backend = SendGridBackend(config=config)
    assert backend._config.api_key == "SG.xxx"
    assert backend._config.timeout == 60


async def test_sendgrid_backend_open_returns_false_when_connected() -> None:
    """Test that open() returns False if already connected."""
    from unittest.mock import MagicMock

    from litestar_email.backends.sendgrid import SendGridBackend
    from litestar_email.config import SendGridConfig

    config = SendGridConfig(api_key="SG.xxx")
    backend = SendGridBackend(config=config)
    backend._client = MagicMock()

    result = await backend.open()
    assert result is False


async def test_sendgrid_backend_send_empty_list() -> None:
    """Test sending empty list returns 0."""
    from litestar_email.backends.sendgrid import SendGridBackend

    backend = SendGridBackend()
    count = await backend.send_messages([])
    assert count == 0


async def test_sendgrid_backend_send_message_not_connected() -> None:
    """Test _send_message raises if not connected."""
    from litestar_email import EmailMessage
    from litestar_email.backends.sendgrid import SendGridBackend

    backend = SendGridBackend()
    backend._client = None
    message = EmailMessage(subject="Test", body="Body", to=["test@example.com"])

    with pytest.raises(RuntimeError, match="SendGrid client not initialized"):
        await backend._send_message(message)


@respx.mock
async def test_sendgrid_backend_send_success() -> None:
    """Test successful email sending via SendGrid API."""
    from litestar_email import EmailMessage
    from litestar_email.backends.sendgrid import SENDGRID_API_URL, SendGridBackend
    from litestar_email.config import SendGridConfig

    respx.post(SENDGRID_API_URL).mock(return_value=httpx.Response(202))

    config = SendGridConfig(api_key="SG.xxx")
    backend = SendGridBackend(config=config)

    message = EmailMessage(
        subject="Test",
        body="Body",
        from_email="sender@example.com",
        to=["test@example.com"],
    )

    count = await backend.send_messages([message])
    assert count == 1


@respx.mock
async def test_sendgrid_backend_send_with_all_fields() -> None:
    """Test sending email with all optional fields."""
    from litestar_email import EmailMessage
    from litestar_email.backends.sendgrid import SENDGRID_API_URL, SendGridBackend
    from litestar_email.config import SendGridConfig

    route = respx.post(SENDGRID_API_URL).mock(return_value=httpx.Response(202))

    config = SendGridConfig(api_key="SG.xxx")
    backend = SendGridBackend(config=config)

    message = EmailMessage(
        subject="Test",
        body="Plain text",
        from_email="sender@example.com",
        to=["test@example.com", "test2@example.com"],
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
        reply_to=["reply@example.com"],
        headers={"X-Custom": "header"},
    )
    message.attach_alternative("<p>HTML</p>", "text/html")
    message.attach("file.txt", b"content", "text/plain")

    count = await backend.send_messages([message])
    assert count == 1

    # Verify request payload matches SendGrid v3 format
    import json

    payload = json.loads(route.calls.last.request.content)

    assert payload["from"]["email"] == "sender@example.com"
    assert payload["subject"] == "Test"
    assert payload["personalizations"][0]["to"] == [
        {"email": "test@example.com"},
        {"email": "test2@example.com"},
    ]
    assert payload["personalizations"][0]["cc"] == [{"email": "cc@example.com"}]
    assert payload["personalizations"][0]["bcc"] == [{"email": "bcc@example.com"}]
    assert payload["reply_to"]["email"] == "reply@example.com"
    assert payload["headers"] == {"X-Custom": "header"}

    # Check content
    assert {"type": "text/plain", "value": "Plain text"} in payload["content"]
    assert {"type": "text/html", "value": "<p>HTML</p>"} in payload["content"]

    # Check attachments
    assert len(payload["attachments"]) == 1
    assert payload["attachments"][0]["filename"] == "file.txt"
    assert payload["attachments"][0]["type"] == "text/plain"


@respx.mock
async def test_sendgrid_backend_uses_default_from() -> None:
    """Test default from values are used when message lacks from_email."""
    from litestar_email import EmailConfig, EmailMessage, get_backend
    from litestar_email.backends.sendgrid import SENDGRID_API_URL
    from litestar_email.config import SendGridConfig

    route = respx.post(SENDGRID_API_URL).mock(return_value=httpx.Response(202))

    config = EmailConfig(
        backend="sendgrid",
        from_email="noreply@example.com",
        from_name="Litestar",
        backend_config=SendGridConfig(api_key="SG.xxx"),
    )
    backend = get_backend("sendgrid", config=config)

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    await backend.send_messages([message])

    import json

    payload = json.loads(route.calls.last.request.content)
    assert payload["from"]["email"] == "noreply@example.com"
    assert payload["from"]["name"] == "Litestar"


@respx.mock
async def test_sendgrid_backend_rate_limit() -> None:
    """Test rate limit error handling."""
    from litestar_email import EmailMessage
    from litestar_email.backends.sendgrid import SENDGRID_API_URL, SendGridBackend
    from litestar_email.config import SendGridConfig
    from litestar_email.exceptions import EmailRateLimitError

    respx.post(SENDGRID_API_URL).mock(return_value=httpx.Response(429, headers={"Retry-After": "30"}))

    config = SendGridConfig(api_key="SG.xxx")
    backend = SendGridBackend(config=config, fail_silently=False)

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    with pytest.raises(EmailRateLimitError) as exc_info:
        await backend.send_messages([message])

    assert exc_info.value.retry_after == 30


@respx.mock
async def test_sendgrid_backend_api_error() -> None:
    """Test API error handling."""
    from litestar_email import EmailMessage
    from litestar_email.backends.sendgrid import SENDGRID_API_URL, SendGridBackend
    from litestar_email.config import SendGridConfig
    from litestar_email.exceptions import EmailDeliveryError

    respx.post(SENDGRID_API_URL).mock(return_value=httpx.Response(400, json={"errors": [{"message": "Invalid"}]}))

    config = SendGridConfig(api_key="SG.xxx")
    backend = SendGridBackend(config=config, fail_silently=False)

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    with pytest.raises(EmailDeliveryError, match="Failed to send email"):
        await backend.send_messages([message])


@respx.mock
async def test_sendgrid_backend_fail_silently() -> None:
    """Test fail_silently suppresses errors."""
    from litestar_email import EmailMessage
    from litestar_email.backends.sendgrid import SENDGRID_API_URL, SendGridBackend
    from litestar_email.config import SendGridConfig

    respx.post(SENDGRID_API_URL).mock(return_value=httpx.Response(500))

    config = SendGridConfig(api_key="SG.xxx")
    backend = SendGridBackend(config=config, fail_silently=True)

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    # Should not raise
    count = await backend.send_messages([message])
    assert count == 0


# ==============================================================================
# Common Backend Tests
# ==============================================================================


async def test_backends_registered() -> None:
    """Test that new backends are registered in the registry."""
    from litestar_email import list_backends

    backends = list_backends()
    assert "smtp" in backends
    assert "resend" in backends
    assert "sendgrid" in backends


def test_get_backend_smtp() -> None:
    """Test getting SMTP backend via factory."""
    from litestar_email import get_backend
    from litestar_email.backends.smtp import SMTPBackend

    backend = get_backend("smtp")
    assert isinstance(backend, SMTPBackend)


def test_get_backend_resend() -> None:
    """Test getting Resend backend via factory."""
    from litestar_email import get_backend
    from litestar_email.backends.resend import ResendBackend

    backend = get_backend("resend")
    assert isinstance(backend, ResendBackend)


def test_get_backend_sendgrid() -> None:
    """Test getting SendGrid backend via factory."""
    from litestar_email import get_backend
    from litestar_email.backends.sendgrid import SendGridBackend

    backend = get_backend("sendgrid")
    assert isinstance(backend, SendGridBackend)


def test_get_backend_with_config() -> None:
    """Test that config is passed to backend via factory."""
    from litestar_email import get_backend
    from litestar_email.config import EmailConfig, SMTPConfig

    config = EmailConfig(
        backend="smtp",
        backend_config=SMTPConfig(host="mail.example.com", port=587),
    )
    backend = get_backend("smtp", config=config)

    assert backend._config.host == "mail.example.com"
    assert backend._config.port == 587
