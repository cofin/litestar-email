from typing import TYPE_CHECKING

from litestar.plugins import InitPluginProtocol

if TYPE_CHECKING:
    from litestar.config.app import AppConfig
    from litestar.datastructures import State

    from litestar_email.backends.base import BaseEmailBackend
    from litestar_email.config import EmailConfig
    from litestar_email.service import EmailService

__all__ = ("EmailPlugin",)


class EmailPlugin(InitPluginProtocol):
    """Litestar plugin for email functionality.

    This plugin provides email sending capabilities for Litestar applications.
    It supports multiple backend providers (SMTP, SendGrid, Resend, etc.) through
    a pluggable backend system.

    Example:
        Basic plugin configuration::

            from litestar import Litestar
            from litestar_email import EmailConfig, EmailPlugin

            email_config = EmailConfig(
                backend="smtp",
                from_email="noreply@example.com",
            )
            app = Litestar(plugins=[EmailPlugin(config=email_config)])

        Dependency injection example::

            from litestar import get
            from litestar_email import EmailMessage, EmailService

            @get("/welcome/{email:str}")
            async def send_welcome(email: str, mailer: EmailService) -> dict[str, str]:
                await mailer.send_message(
                    EmailMessage(subject="Welcome!", body="Thanks for signing up.", to=[email]),
                )
                return {"status": "sent"}
    """

    __slots__ = ("_config",)

    def __init__(self, config: "EmailConfig | None" = None) -> None:
        """Initialize the email plugin.

        Args:
            config: Optional email configuration. If not provided, defaults will be used.
        """
        from litestar_email.config import EmailConfig

        self._config = config or EmailConfig()

    @property
    def config(self) -> "EmailConfig":
        """Return the plugin configuration.

        Returns:
            The email configuration instance.
        """
        return self._config

    def get_service(self, state: "State | None" = None) -> "EmailService":
        """Return an EmailService for this plugin.

        Args:
            state: Optional application state to fetch a cached service instance or config.

        Returns:
            An EmailService instance.
        """
        return self._config.get_service(state)

    def get_backend(
        self,
        backend: str | None = None,
        fail_silently: bool | None = None,
    ) -> "BaseEmailBackend":
        """Return a backend instance configured for this plugin.

        Args:
            backend: Optional backend name or import path. Defaults to config backend.
            fail_silently: Optional override for fail_silently behavior.

        Returns:
            A configured backend instance.
        """
        return self._config.get_backend(backend=backend, fail_silently=fail_silently)

    def on_app_init(self, app_config: "AppConfig") -> "AppConfig":
        """Handle application initialization.

        This method is called during Litestar application initialization.
        Registers the EmailService dependency, signature namespace entries, and
        app state helpers for use in handlers and event listeners.

        Args:
            app_config: The Litestar application configuration.

        Returns:
            The application configuration (unmodified).
        """
        app_config.dependencies.update(self._config.dependencies)
        app_config.signature_namespace.update(self._config.signature_namespace)
        app_config.state.update({self._config.email_service_state_key: self._config})
        return app_config
