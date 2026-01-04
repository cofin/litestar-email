from functools import lru_cache
from importlib import import_module
from inspect import signature
from typing import TYPE_CHECKING, Any

from litestar_email.backends.base import BaseEmailBackend

if TYPE_CHECKING:
    from litestar_email.config import EmailConfig

__all__ = (
    "BaseEmailBackend",
    "ConsoleBackend",
    "InMemoryBackend",
    "ResendBackend",
    "SMTPBackend",
    "SendGridBackend",
    "get_backend",
    "get_backend_class",
    "list_backends",
    "register_backend",
)

# Global registry of backend short names to classes
_backend_registry: dict[str, type[BaseEmailBackend]] = {}


def register_backend(name: str) -> "type[BaseEmailBackend]":
    """Decorator to register a backend class with a short name.

    Args:
        name: The short name for the backend (e.g., "console", "smtp").

    Returns:
        A decorator that registers the backend class.

    Example:
        Registering a custom backend::

            @register_backend("mybackend")
            class MyBackend(BaseEmailBackend):
                async def send_messages(self, messages):
                    ...
    """

    def decorator(cls: type[BaseEmailBackend]) -> type[BaseEmailBackend]:
        _backend_registry[name] = cls
        return cls

    return decorator  # type: ignore[return-value]


@lru_cache(maxsize=1)
def _register_builtins() -> None:
    """Register built-in backends. Called lazily to avoid import cycles."""
    from litestar_email.backends.console import ConsoleBackend
    from litestar_email.backends.memory import InMemoryBackend

    _backend_registry.setdefault("console", ConsoleBackend)
    _backend_registry.setdefault("memory", InMemoryBackend)

    # Register optional backends if dependencies are available
    try:
        from litestar_email.backends.smtp import SMTPBackend

        _backend_registry.setdefault("smtp", SMTPBackend)
    except ImportError:
        pass  # aiosmtplib not installed

    try:
        from litestar_email.backends.resend import ResendBackend

        _backend_registry.setdefault("resend", ResendBackend)
    except ImportError:
        pass  # httpx not installed

    try:
        from litestar_email.backends.sendgrid import SendGridBackend

        _backend_registry.setdefault("sendgrid", SendGridBackend)
    except ImportError:
        pass  # httpx not installed


def get_backend_class(backend_path: str) -> type[BaseEmailBackend]:
    """Get a backend class by short name or full import path.

    Args:
        backend_path: Either a registered short name (e.g., "console", "memory")
            or a full Python import path (e.g., "myapp.backends.CustomBackend").

    Returns:
        The backend class.

    Raises:
        ValueError: If the backend cannot be found.

    Example:
        Getting a backend class::

            # By short name
            cls = get_backend_class("console")

            # By full path
            cls = get_backend_class("litestar_email.backends.console.ConsoleBackend")
    """
    _register_builtins()

    # Check registry first
    if backend_path in _backend_registry:
        return _backend_registry[backend_path]

    # Try to import as a full path
    if "." not in backend_path:
        msg = f"Unknown backend: {backend_path!r}. Available: {list(_backend_registry.keys())}"
        raise ValueError(msg)

    module_path, class_name = backend_path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, class_name)  # type: ignore[no-any-return]


def get_backend(
    backend: str = "console",
    fail_silently: bool | None = None,
    config: "EmailConfig | None" = None,
) -> BaseEmailBackend:
    """Get an instantiated backend by name or path.

    Args:
        backend: The backend short name or full import path.
        fail_silently: Whether the backend should suppress exceptions. If None,
            uses config.fail_silently when config is provided.
        config: Optional EmailConfig to extract backend-specific settings from.
            The ``backend_config`` field from config will be passed to the
            backend constructor.

    Returns:
        An instantiated backend.

    Example:
        Basic usage::

            backend = get_backend("console")
            async with backend:
                await backend.send_messages([message])

        With configuration::

            config = EmailConfig(
                backend="smtp",
                fail_silently=True,
                backend_config=SMTPConfig(host="localhost", port=1025),
            )
            backend = get_backend("smtp", config=config)
    """
    backend_class = get_backend_class(backend)

    default_from_email: str | None = None
    default_from_name: str | None = None
    resolved_fail_silently = fail_silently if fail_silently is not None else False
    backend_config: Any = None
    if config is not None:
        backend_config = config.backend_config
        default_from_email = config.from_email
        default_from_name = config.from_name
        if fail_silently is None:
            resolved_fail_silently = config.fail_silently

    backend_kwargs: dict[str, Any] = {
        "fail_silently": resolved_fail_silently,
        "default_from_email": default_from_email,
        "default_from_name": default_from_name,
    }

    # Pass config to backend if it was found
    if backend_config is not None:
        backend_kwargs["config"] = backend_config

    init_signature = signature(backend_class.__init__)
    accepts_kwargs = any(param.kind == param.VAR_KEYWORD for param in init_signature.parameters.values())
    if not accepts_kwargs:
        backend_kwargs = {key: value for key, value in backend_kwargs.items() if key in init_signature.parameters}

    return backend_class(**backend_kwargs)


def list_backends() -> list[str]:
    """Return a list of registered backend short names.

    Returns:
        A list of backend names that can be used with get_backend().
    """
    _register_builtins()
    return list(_backend_registry.keys())


# Re-export backend classes for convenience
from litestar_email.backends.console import ConsoleBackend
from litestar_email.backends.memory import InMemoryBackend

# Conditionally export optional backends
try:
    from litestar_email.backends.smtp import SMTPBackend  # pyright: ignore[reportAssignmentType]
except ImportError:

    class SMTPBackend:  # type: ignore[no-redef]
        """Placeholder for SMTP backend when aiosmtplib is not installed."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            msg = "aiosmtplib is required for SMTP backend. Install with: pip install litestar-email[smtp]"
            raise ImportError(msg)


try:
    from litestar_email.backends.resend import ResendBackend  # pyright: ignore[reportAssignmentType]
except ImportError:

    class ResendBackend:  # type: ignore[no-redef]
        """Placeholder for Resend backend when httpx is not installed."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            msg = "httpx is required for Resend backend. Install with: pip install litestar-email[resend]"
            raise ImportError(msg)


try:
    from litestar_email.backends.sendgrid import SendGridBackend  # pyright: ignore[reportAssignmentType]
except ImportError:

    class SendGridBackend:  # type: ignore[no-redef]
        """Placeholder for SendGrid backend when httpx is not installed."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            msg = "httpx is required for SendGrid backend. Install with: pip install litestar-email[sendgrid]"
            raise ImportError(msg)
