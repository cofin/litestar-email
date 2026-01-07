"""Tests for HTTP transport layer."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from litestar_email.utils import dependencies

pytestmark = pytest.mark.anyio


# --- Factory Tests ---


def test_get_transport_default() -> None:
    """Test get_transport returns HttpxTransport by default."""
    from litestar_email.transports import get_transport
    from litestar_email.transports.httpx import HttpxTransport

    transport = get_transport()
    assert isinstance(transport, HttpxTransport)


def test_get_transport_httpx_explicit() -> None:
    """Test get_transport with explicit httpx."""
    from litestar_email.transports import get_transport
    from litestar_email.transports.httpx import HttpxTransport

    transport = get_transport("httpx")
    assert isinstance(transport, HttpxTransport)


def test_get_transport_aiohttp() -> None:
    """Test get_transport with aiohttp."""
    from litestar_email.transports import get_transport
    from litestar_email.transports.aiohttp import AiohttpTransport

    transport = get_transport("aiohttp")
    assert isinstance(transport, AiohttpTransport)


def test_get_transport_unknown_raises() -> None:
    """Test get_transport raises ValueError for unknown transport."""
    from litestar_email.transports import get_transport

    with pytest.raises(ValueError, match="Unknown transport"):
        get_transport("unknown")


def test_get_transport_custom_class() -> None:
    """Test get_transport instantiates custom transport class."""
    from litestar_email.transports import get_transport

    class CustomTransport:
        """Custom transport for testing."""

        def __init__(self) -> None:
            self.initialized = True

    transport = get_transport(CustomTransport)  # type: ignore[arg-type]
    assert isinstance(transport, CustomTransport)
    assert transport.initialized is True


# --- Httpx Transport Tests ---


def test_httpx_transport_requires_httpx(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test HttpxTransport raises MissingDependencyError if httpx not installed."""
    from litestar_email.exceptions import MissingDependencyError

    monkeypatch.setattr(dependencies, "_dependency_cache", {"httpx": False})

    from litestar_email.transports.httpx import HttpxTransport

    with pytest.raises(MissingDependencyError, match="httpx"):
        HttpxTransport()


async def test_httpx_transport_open_close() -> None:
    """Test HttpxTransport open/close lifecycle."""
    from litestar_email.transports.httpx import HttpxTransport

    transport = HttpxTransport()
    assert transport._client is None

    await transport.open(headers={"Authorization": "Bearer test"}, timeout=60.0)
    assert transport._client is not None

    # Second open should be no-op
    await transport.open()  # type: ignore[unreachable]
    assert transport._client is not None

    await transport.close()
    assert transport._client is None


async def test_httpx_transport_context_manager() -> None:
    """Test HttpxTransport works as async context manager."""
    from litestar_email.transports.httpx import HttpxTransport

    async with HttpxTransport() as transport:
        await transport.open()
        assert transport._client is not None

    # Client should be closed after exiting context
    assert transport._client is None


async def test_httpx_transport_post_not_initialized() -> None:
    """Test HttpxTransport.post raises RuntimeError if not initialized."""
    from litestar_email.transports.httpx import HttpxTransport

    transport = HttpxTransport()

    with pytest.raises(RuntimeError, match="Transport not initialized"):
        await transport.post("https://example.com", json={})


async def test_httpx_transport_post_json() -> None:
    """Test HttpxTransport.post with JSON payload."""
    from litestar_email.transports.httpx import HttpxTransport

    transport = HttpxTransport()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_response.headers = {"Content-Type": "application/json"}

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        await transport.open(headers={"Authorization": "Bearer test"})
        response = await transport.post(
            "https://api.example.com/emails",
            json={"to": "test@example.com", "subject": "Test"},
        )

        assert response.status_code == 200
        assert await response.text() == "OK"
        mock_client.post.assert_called_once()


async def test_httpx_transport_post_form_data() -> None:
    """Test HttpxTransport.post with form-data payload."""
    from litestar_email.transports.httpx import HttpxTransport

    transport = HttpxTransport()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_response.headers = {}

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        await transport.open(auth=("api", "key-xxx"), base_url="https://api.mailgun.net")
        response = await transport.post(
            "/v3/domain/messages",
            data={"from": "sender@example.com", "to": "recipient@example.com"},
            files=[("attachment", ("file.txt", b"content", "text/plain"))],
        )

        assert response.status_code == 200
        mock_client.post.assert_called_once()


async def test_httpx_transport_base_url() -> None:
    """Test HttpxTransport passes base_url to client."""
    from litestar_email.transports.httpx import HttpxTransport

    transport = HttpxTransport()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_response.headers = {}

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        await transport.open(base_url="https://api.example.com/")
        await transport.post("/v3/messages", json={})

        # Verify base_url was passed to client constructor
        call_kwargs = mock_client_class.call_args.kwargs
        assert call_kwargs.get("base_url") == "https://api.example.com/"

        # Verify the relative URL was passed to post
        post_call_args = mock_client.post.call_args
        assert post_call_args[0][0] == "/v3/messages"


async def test_httpx_response_get_header() -> None:
    """Test HttpxResponse.get_header method."""
    from litestar_email.transports.httpx import HttpxResponse

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Rate limited"
    mock_response.headers = {"Retry-After": "60", "Content-Type": "text/plain"}

    response = HttpxResponse(mock_response)
    assert response.get_header("Retry-After") == "60"
    assert response.get_header("Content-Type") == "text/plain"
    assert response.get_header("X-Missing") is None
    assert response.get_header("X-Missing", "default") == "default"


# --- Aiohttp Transport Tests ---


def test_aiohttp_transport_requires_aiohttp(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test AiohttpTransport raises MissingDependencyError if aiohttp not installed."""
    from litestar_email.exceptions import MissingDependencyError

    monkeypatch.setattr(dependencies, "_dependency_cache", {"aiohttp": False})

    from litestar_email.transports.aiohttp import AiohttpTransport

    with pytest.raises(MissingDependencyError, match="aiohttp"):
        AiohttpTransport()


async def test_aiohttp_transport_open_close() -> None:
    """Test AiohttpTransport open/close lifecycle."""
    from litestar_email.transports.aiohttp import AiohttpTransport

    transport = AiohttpTransport()
    assert transport._session is None

    await transport.open(headers={"Authorization": "Bearer test"}, timeout=60.0)
    assert transport._session is not None

    # Second open should be no-op
    await transport.open()  # type: ignore[unreachable]
    assert transport._session is not None

    await transport.close()
    assert transport._session is None


async def test_aiohttp_transport_context_manager() -> None:
    """Test AiohttpTransport works as async context manager."""
    from litestar_email.transports.aiohttp import AiohttpTransport

    async with AiohttpTransport() as transport:
        await transport.open()
        assert transport._session is not None

    # Session should be closed after exiting context
    assert transport._session is None


async def test_aiohttp_transport_post_not_initialized() -> None:
    """Test AiohttpTransport.post raises RuntimeError if not initialized."""
    from litestar_email.transports.aiohttp import AiohttpTransport

    transport = AiohttpTransport()

    with pytest.raises(RuntimeError, match="Transport not initialized"):
        await transport.post("https://example.com", json={})


async def test_aiohttp_transport_post_json() -> None:
    """Test AiohttpTransport.post with JSON payload."""

    from litestar_email.transports.aiohttp import AiohttpTransport

    transport = AiohttpTransport()

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.text = AsyncMock(return_value="OK")

    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = MagicMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_session.close = AsyncMock()
        mock_session_class.return_value = mock_session

        await transport.open(headers={"Authorization": "Bearer test"})
        response = await transport.post(
            "https://api.example.com/emails",
            json={"to": "test@example.com"},
        )

        assert response.status_code == 200
        body = await response.text()
        assert body == "OK"


async def test_aiohttp_response_lazy_reading() -> None:
    """Test AiohttpResponse reads body lazily and caches result."""
    from litestar_email.transports.aiohttp import AiohttpResponse

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/plain"}
    mock_response.text = AsyncMock(return_value="Body content")

    response = AiohttpResponse(mock_response)

    # First call should read from response
    body1 = await response.text()
    assert body1 == "Body content"
    mock_response.text.assert_called_once()

    # Second call should return cached value
    body2 = await response.text()
    assert body2 == "Body content"
    # Still only one call to response.text()
    mock_response.text.assert_called_once()


async def test_aiohttp_response_get_header() -> None:
    """Test AiohttpResponse.get_header method."""
    from litestar_email.transports.aiohttp import AiohttpResponse

    mock_response = MagicMock()
    mock_response.status = 429
    mock_response.headers = {"Retry-After": "60", "Content-Type": "text/plain"}
    mock_response.text = AsyncMock(return_value="Rate limited")

    response = AiohttpResponse(mock_response)
    assert response.get_header("Retry-After") == "60"
    assert response.get_header("Content-Type") == "text/plain"
    assert response.get_header("X-Missing") is None
    assert response.get_header("X-Missing", "default") == "default"


async def test_aiohttp_transport_with_auth() -> None:
    """Test AiohttpTransport with HTTP Basic Auth."""
    from litestar_email.transports.aiohttp import AiohttpTransport

    transport = AiohttpTransport()

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {}
    mock_response.text = AsyncMock(return_value="OK")

    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = MagicMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_session.close = AsyncMock()
        mock_session_class.return_value = mock_session

        await transport.open(
            auth=("api", "key-xxx"),
            base_url="https://api.mailgun.net",
        )

        # Auth should be stored for use in requests
        assert transport._auth is not None
        assert transport._base_url == "https://api.mailgun.net"

        await transport.close()
        assert transport._auth is None
        assert transport._base_url is None  # type: ignore[unreachable]


# --- Lazy Import Tests ---


def test_lazy_import_httpx_transport() -> None:
    """Test HttpxTransport can be imported from transports package."""
    from litestar_email.transports import HttpxTransport

    assert HttpxTransport is not None


def test_lazy_import_httpx_response() -> None:
    """Test HttpxResponse can be imported from transports package."""
    from litestar_email.transports import HttpxResponse

    assert HttpxResponse is not None


def test_lazy_import_aiohttp_transport() -> None:
    """Test AiohttpTransport can be imported from transports package."""
    from litestar_email.transports import AiohttpTransport

    assert AiohttpTransport is not None


def test_lazy_import_aiohttp_response() -> None:
    """Test AiohttpResponse can be imported from transports package."""
    from litestar_email.transports import AiohttpResponse

    assert AiohttpResponse is not None


def test_lazy_import_unknown_raises() -> None:
    """Test accessing unknown attribute raises AttributeError."""
    import litestar_email.transports as transports_module

    with pytest.raises(AttributeError, match="has no attribute"):
        _ = transports_module.UnknownClass
