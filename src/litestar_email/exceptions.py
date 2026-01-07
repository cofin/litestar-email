"""Email exception hierarchy.

This module defines custom exceptions for the litestar-email plugin,
providing specific exception types for different failure modes.
"""

__all__ = (
    "EmailAuthenticationError",
    "EmailBackendError",
    "EmailConnectionError",
    "EmailDeliveryError",
    "EmailError",
    "EmailRateLimitError",
    "MissingDependencyError",
)


class EmailError(Exception):
    """Base exception for all email-related errors.

    This is the root exception class for the litestar-email plugin.
    All other email exceptions inherit from this class, allowing
    users to catch all email-related errors with a single handler.

    Example:
        Catch all email errors::

            try:
                await backend.send_messages([message])
            except EmailError as e:
                logger.error(f"Email failed: {e}")
    """


class EmailBackendError(EmailError):
    """Error in email backend configuration or initialization.

    Raised when there is a problem with the email backend setup,
    such as missing dependencies, invalid configuration, or
    backend initialization failures.

    Example:
        Handle backend configuration errors::

            try:
                backend = get_backend("smtp", config=config)
            except EmailBackendError as e:
                logger.error(f"Backend setup failed: {e}")
    """


class EmailDeliveryError(EmailError):
    """Error during email delivery.

    Base class for errors that occur while attempting to send
    email messages. This includes connection, authentication,
    and rate limit errors.

    Example:
        Handle delivery failures::

            try:
                await backend.send_messages([message])
            except EmailDeliveryError as e:
                logger.error(f"Delivery failed: {e}")
    """


class EmailConnectionError(EmailDeliveryError):
    """Error connecting to email server or API.

    Raised when the email backend cannot establish a connection
    to the SMTP server or API endpoint. This could be due to
    network issues, invalid hostnames, or server unavailability.

    Example:
        Handle connection failures with retry::

            try:
                await backend.send_messages([message])
            except EmailConnectionError as e:
                logger.warning(f"Connection failed, retrying: {e}")
                await asyncio.sleep(5)
                # retry logic...
    """


class EmailAuthenticationError(EmailDeliveryError):
    """Error authenticating with email server or API.

    Raised when authentication fails with the SMTP server
    (invalid username/password) or API service (invalid API key).

    Example:
        Handle authentication failures::

            try:
                await backend.send_messages([message])
            except EmailAuthenticationError as e:
                logger.error(f"Authentication failed: {e}")
                # Do not retry - credentials need to be fixed
    """


class EmailRateLimitError(EmailDeliveryError):
    """Rate limit exceeded for email API.

    Raised when the email API service returns a rate limit error
    (typically HTTP 429). This is common with API-based backends
    like Resend and SendGrid.

    Example:
        Handle rate limits with exponential backoff::

            try:
                await backend.send_messages([message])
            except EmailRateLimitError as e:
                wait_time = e.retry_after or 60
                logger.warning(f"Rate limited, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
                # retry logic...
    """

    retry_after: int | None

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        """Initialize rate limit error.

        Args:
            message: Error description.
            retry_after: Seconds to wait before retrying (optional).
        """
        super().__init__(message)
        self.retry_after = retry_after


class MissingDependencyError(EmailError, ImportError):
    """Raised when a required optional dependency is not installed.

    This exception inherits from both EmailError (for catch-all email
    error handling) and ImportError (for semantic correctness when
    a dependency import fails).

    Example:
        Handle missing dependency errors::

            try:
                from litestar_email.backends.smtp import SMTPBackend
                backend = SMTPBackend(config=config)
            except MissingDependencyError as e:
                logger.error(f"Missing dependency: {e}")
                # Install the dependency or use a different backend
    """

    def __init__(self, package: str, install_package: str | None = None) -> None:
        """Initialize missing dependency error.

        Args:
            package: The name of the missing package.
            install_package: The optional dependency extra name to install.
                If not provided, defaults to the package name.
        """
        install_name = install_package or package
        super().__init__(
            f"Package {package!r} is not installed but required. You can install it by running "
            f"'pip install litestar-email[{install_name}]' to install litestar-email with the required extra "
            f"or 'pip install {install_name}' to install the package separately"
        )
