"""Tests for EmailService."""

import pytest

pytestmark = pytest.mark.anyio


async def test_email_service_sends_messages_memory_backend() -> None:
    """Test EmailService sends messages via the configured backend."""
    from litestar_email import EmailConfig, EmailMessage, EmailService
    from litestar_email.backends import InMemoryBackend

    InMemoryBackend.clear()
    config = EmailConfig(backend="memory")
    service = EmailService(config)

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    count = await service.send_messages([message])

    assert count == 1
    assert len(InMemoryBackend.outbox) == 1


def test_config_get_service_uses_state_config() -> None:
    """Test EmailConfig.get_service returns service from cached config."""
    from litestar.datastructures import State

    from litestar_email import EmailConfig, EmailService

    config = EmailConfig()
    state = State({config.email_service_state_key: config})

    service = config.get_service(state)
    assert isinstance(service, EmailService)
    assert service.config is config


def test_config_get_service_uses_state_service() -> None:
    """Test EmailConfig.get_service returns cached state instance."""
    from litestar.datastructures import State

    from litestar_email import EmailConfig, EmailService

    config = EmailConfig()
    service = EmailService(config)
    state = State({config.email_service_state_key: service})

    assert config.get_service(state) is service


async def test_config_provide_service_as_context_manager() -> None:
    """Test provide_service works as an async context manager."""
    from litestar_email import EmailConfig, EmailMessage
    from litestar_email.backends import InMemoryBackend

    InMemoryBackend.clear()
    config = EmailConfig(backend="memory")

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    async with config.provide_service() as mailer:
        await mailer.send_message(message)

    assert len(InMemoryBackend.outbox) == 1


async def test_config_provide_service_as_iterator() -> None:
    """Test provide_service works as an async iterator (DI compatibility)."""
    from litestar_email import EmailConfig, EmailMessage
    from litestar_email.backends import InMemoryBackend

    InMemoryBackend.clear()
    config = EmailConfig(backend="memory")

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["test@example.com"],
    )

    async for mailer in config.provide_service():
        await mailer.send_message(message)

    assert len(InMemoryBackend.outbox) == 1


def test_async_service_provider_has_slots() -> None:
    """Test AsyncServiceProvider uses __slots__ for memory efficiency."""
    from litestar_email import AsyncServiceProvider

    assert hasattr(AsyncServiceProvider, "__slots__")
    assert "_config" in AsyncServiceProvider.__slots__
    assert "_service" in AsyncServiceProvider.__slots__
