"""HTTP transport layer for API-based email backends.

This package provides pluggable HTTP transport implementations for email backends
that communicate via HTTP APIs (Resend, SendGrid, Mailgun).

The default transport is httpx, which is bundled with Litestar. Users can opt
into aiohttp for applications that already use it, or provide custom transport
implementations.

Example:
    Using the default httpx transport::

        from litestar_email.transports import get_transport

        transport = get_transport()  # Returns HttpxTransport
        await transport.open(headers={"Authorization": "Bearer xxx"})
        response = await transport.post(url, json=payload)
        await transport.close()

    Using aiohttp transport::

        transport = get_transport("aiohttp")

    Using a custom transport::

        class MyTransport:
            async def open(self, headers, timeout, auth, base_url): ...
            async def close(self): ...
            async def post(self, url, *, json, data, files): ...
            async def __aenter__(self): ...
            async def __aexit__(self, ...): ...

        transport = get_transport(MyTransport)
"""

from typing import TYPE_CHECKING

from litestar_email.transports.base import HTTPResponse, HTTPTransport

if TYPE_CHECKING:
    from litestar_email.transports.aiohttp import AiohttpResponse, AiohttpTransport
    from litestar_email.transports.httpx import HttpxResponse, HttpxTransport

__all__ = (
    "AiohttpResponse",
    "AiohttpTransport",
    "HTTPResponse",
    "HTTPTransport",
    "HttpxResponse",
    "HttpxTransport",
    "get_transport",
)


def get_transport(transport: str | type["HTTPTransport"] = "httpx") -> "HTTPTransport":
    """Get an HTTP transport instance by name or from a custom class.

    This factory function provides a convenient way to obtain transport instances.
    It supports built-in transports by name and custom transport classes.

    Args:
        transport: Either a string name ("httpx" or "aiohttp") or a custom
            transport class that implements the HTTPTransport protocol.
            Defaults to "httpx".

    Returns:
        An instance of the requested transport.

    Raises:
        ValueError: If an unknown transport name is provided.

    Example:
        Get the default httpx transport::

            transport = get_transport()

        Get the aiohttp transport::

            transport = get_transport("aiohttp")

        Use a custom transport class::

            transport = get_transport(MyCustomTransport)
    """
    if isinstance(transport, str):
        if transport == "httpx":
            from litestar_email.transports.httpx import HttpxTransport

            return HttpxTransport()

        if transport == "aiohttp":
            from litestar_email.transports.aiohttp import AiohttpTransport

            return AiohttpTransport()

        msg = f"Unknown transport: {transport!r}. Available transports: 'httpx', 'aiohttp'"
        raise ValueError(msg)

    # Custom transport class - instantiate it
    return transport()


def __getattr__(name: str) -> object:
    """Lazy import for transport implementations.

    This enables importing transport classes from the package without
    loading their dependencies until actually used.

    Args:
        name: The attribute name to look up.

    Returns:
        The requested transport class.

    Raises:
        AttributeError: If the attribute is not found.
    """
    if name == "HttpxTransport":
        from litestar_email.transports.httpx import HttpxTransport

        return HttpxTransport

    if name == "HttpxResponse":
        from litestar_email.transports.httpx import HttpxResponse

        return HttpxResponse

    if name == "AiohttpTransport":
        from litestar_email.transports.aiohttp import AiohttpTransport

        return AiohttpTransport

    if name == "AiohttpResponse":
        from litestar_email.transports.aiohttp import AiohttpResponse

        return AiohttpResponse

    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
