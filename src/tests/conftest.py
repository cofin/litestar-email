from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from litestar import Litestar

    from litestar_email import EmailConfig, EmailPlugin

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Return the async backend to use for tests."""
    return "asyncio"


@pytest.fixture
def email_config() -> "EmailConfig":
    """Return a default email configuration for testing."""
    from litestar_email import EmailConfig

    return EmailConfig(
        backend="memory",
        from_email="test@example.com",
        from_name="Test Sender",
    )


@pytest.fixture
def email_plugin(email_config: "EmailConfig") -> "EmailPlugin":
    """Return an email plugin instance for testing."""
    from litestar_email import EmailPlugin

    return EmailPlugin(config=email_config)


@pytest.fixture
def app(email_plugin: "EmailPlugin") -> "Litestar":
    """Return a Litestar application with the email plugin."""
    from litestar import Litestar

    return Litestar(plugins=[email_plugin])
