from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from litestar.datastructures import State

    from litestar_email.backends.base import BaseEmailBackend
    from litestar_email.service import EmailService

__all__ = (
    "EmailConfig",
    "ResendConfig",
    "SMTPConfig",
    "SendGridConfig",
)


@dataclass(slots=True)
class SMTPConfig:
    """Configuration for SMTP email backend.

    This configuration class defines the settings for connecting to an SMTP
    server for sending email.

    Example:
        Configure for a local Mailpit instance::

            config = SMTPConfig(host="localhost", port=1025)

        Configure for a production server with TLS::

            config = SMTPConfig(
                host="smtp.example.com",
                port=587,
                username="user@example.com",
                password="secret",
                use_tls=True,
            )
    """

    host: str = "localhost"
    port: int = 25
    username: str | None = None
    password: str | None = None
    use_tls: bool = False
    use_ssl: bool = False
    timeout: int = 30


@dataclass(slots=True)
class ResendConfig:
    """Configuration for Resend API email backend.

    This configuration class defines the settings for the Resend API
    email service (https://resend.com).

    Example:
        Configure with an API key::

            config = ResendConfig(api_key="re_123abc...")
    """

    api_key: str = ""
    timeout: int = 30


@dataclass(slots=True)
class SendGridConfig:
    """Configuration for SendGrid API email backend.

    This configuration class defines the settings for the SendGrid API
    email service (https://sendgrid.com).

    Example:
        Configure with an API key::

            config = SendGridConfig(api_key="SG.xxx...")
    """

    api_key: str = ""
    timeout: int = 30


@dataclass(slots=True)
class EmailConfig:
    """Configuration for the EmailPlugin.

    This configuration class defines the settings for sending email
    within a Litestar application.

    Example:
        Basic configuration with console backend::

            config = EmailConfig(
                backend="console",
                from_email="noreply@example.com",
                from_name="My App",
            )

        Configuration with SMTP backend::

            config = EmailConfig(
                backend="smtp",
                from_email="noreply@example.com",
                backend_config=SMTPConfig(
                    host="smtp.example.com",
                    port=587,
                    use_tls=True,
                ),
            )

        Configuration with Resend API backend::

            config = EmailConfig(
                backend="resend",
                from_email="noreply@example.com",
                backend_config=ResendConfig(api_key="re_123abc..."),
            )
    """

    backend: str = "console"
    from_email: str = "noreply@localhost"
    from_name: str = ""
    fail_silently: bool = False
    email_service_dependency_key: str = "mailer"
    email_service_state_key: str = "mailer"
    backend_config: SMTPConfig | ResendConfig | SendGridConfig | None = None

    @property
    def signature_namespace(self) -> dict[str, Any]:
        """Return the plugin's signature namespace.

        Returns:
            A string keyed dict of names to be added to the namespace for signature forward reference resolution.
        """
        from litestar_email.backends.base import BaseEmailBackend
        from litestar_email.message import EmailMessage, EmailMultiAlternatives
        from litestar_email.service import EmailService

        return {
            "BaseEmailBackend": BaseEmailBackend,
            "EmailConfig": EmailConfig,
            "EmailMessage": EmailMessage,
            "EmailMultiAlternatives": EmailMultiAlternatives,
            "EmailService": EmailService,
            "ResendConfig": ResendConfig,
            "SMTPConfig": SMTPConfig,
            "SendGridConfig": SendGridConfig,
        }

    @property
    def dependencies(self) -> dict[str, Any]:
        """Return dependency providers for the plugin.

        Returns:
            A mapping of dependency keys to providers for Litestar's DI system.
        """
        from litestar.di import Provide

        return {self.email_service_dependency_key: Provide(self.provide_service)}

    def get_service(self, state: "State | None" = None) -> "EmailService":
        """Return an EmailService for this configuration.

        Args:
            state: Optional application state to fetch a cached service instance or config.

        Returns:
            An EmailService instance.
        """
        from litestar_email.service import EmailService

        if state is not None and self.email_service_state_key in state:
            cached = state[self.email_service_state_key]
            if isinstance(cached, EmailService):
                return cached
            if isinstance(cached, EmailConfig):
                return EmailService(cached)

        return EmailService(self)

    def get_backend(
        self,
        backend: str | None = None,
        fail_silently: bool | None = None,
    ) -> "BaseEmailBackend":
        """Return a backend instance configured for this EmailConfig.

        Args:
            backend: Optional backend name or import path. Defaults to config backend.
            fail_silently: Optional override for fail_silently behavior.

        Returns:
            A configured backend instance.
        """
        from litestar_email.backends import get_backend

        return get_backend(backend or self.backend, fail_silently=fail_silently, config=self)

    async def provide_service(self) -> AsyncGenerator["EmailService", None]:
        """Provide an EmailService instance.

        Yields:
            An EmailService instance that reuses connections within the request.
        """
        from litestar_email.service import EmailService

        service = EmailService(self)
        async with service:
            yield service
