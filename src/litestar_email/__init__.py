from litestar_email.backends import (
    BaseEmailBackend,
    ConsoleBackend,
    InMemoryBackend,
    ResendBackend,
    SendGridBackend,
    SMTPBackend,
    get_backend,
    get_backend_class,
    list_backends,
    register_backend,
)
from litestar_email.config import (
    AsyncServiceProvider,
    EmailConfig,
    ResendConfig,
    SendGridConfig,
    SMTPConfig,
)
from litestar_email.exceptions import (
    EmailAuthenticationError,
    EmailBackendError,
    EmailConnectionError,
    EmailDeliveryError,
    EmailError,
    EmailRateLimitError,
)
from litestar_email.message import EmailMessage, EmailMultiAlternatives
from litestar_email.plugin import EmailPlugin
from litestar_email.service import EmailService

__all__ = (
    "AsyncServiceProvider",
    "BaseEmailBackend",
    "ConsoleBackend",
    "EmailAuthenticationError",
    "EmailBackendError",
    "EmailConfig",
    "EmailConnectionError",
    "EmailDeliveryError",
    "EmailError",
    "EmailMessage",
    "EmailMultiAlternatives",
    "EmailPlugin",
    "EmailRateLimitError",
    "EmailService",
    "InMemoryBackend",
    "ResendBackend",
    "ResendConfig",
    "SMTPBackend",
    "SMTPConfig",
    "SendGridBackend",
    "SendGridConfig",
    "get_backend",
    "get_backend_class",
    "list_backends",
    "register_backend",
)
