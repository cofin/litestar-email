Testing Email Functionality
===========================

litestar-email provides tools for testing email functionality in your application.

InMemoryBackend
---------------

The ``InMemoryBackend`` stores all sent emails in a class-level list, perfect
for unit testing:

.. code-block:: python

    import pytest
    from litestar_email import EmailMessage
    from litestar_email.backends import InMemoryBackend

    @pytest.fixture(autouse=True)
    def clear_outbox():
        """Clear the email outbox before each test."""
        InMemoryBackend.clear()

    async def test_sends_welcome_email():
        # ... code that sends an email ...

        # Verify email was sent
        assert len(InMemoryBackend.outbox) == 1

        email = InMemoryBackend.outbox[0]
        assert email.subject == "Welcome!"
        assert "user@example.com" in email.to

ConsoleBackend
--------------

The ``ConsoleBackend`` prints emails to stdout (or a custom stream), useful
for development and debugging:

.. code-block:: python

    from io import StringIO
    from litestar_email.backends import ConsoleBackend

    # Capture output for testing
    stream = StringIO()
    backend = ConsoleBackend(stream=stream)

    await backend.send_messages([message])

    output = stream.getvalue()
    assert "Welcome!" in output

Mailpit Integration
-------------------

`Mailpit <https://github.com/axllent/mailpit>`_ is a fake SMTP server with
a web UI and REST API. It's ideal for integration testing.

Starting Mailpit
^^^^^^^^^^^^^^^^

Using the provided container manager:

.. code-block:: python

    from tools.mailpit import MailpitContainer

    container = MailpitContainer()
    container.start()

    # SMTP available at localhost:1025
    # Web UI available at http://localhost:8025

    container.stop()

Or using Docker/Podman directly:

.. code-block:: bash

    # Start Mailpit
    docker run -d --name mailpit -p 1025:1025 -p 8025:8025 axllent/mailpit

    # Stop Mailpit
    docker stop mailpit && docker rm mailpit

Using Make targets:

.. code-block:: bash

    make start-mail   # Start Mailpit container
    make stop-mail    # Stop and remove container
    make mail-logs    # View container logs

Pytest Fixtures
^^^^^^^^^^^^^^^

Example fixtures for integration tests:

.. code-block:: python

    import pytest
    from tools.mailpit import MailpitContainer
    from litestar_email.config import EmailConfig, SMTPConfig

    @pytest.fixture(scope="session")
    def mailpit():
        """Provide Mailpit container for SMTP tests."""
        container = MailpitContainer()
        if not container.is_available:
            pytest.skip("Docker/Podman not available")

        container.start()
        yield container
        container.stop()

    @pytest.fixture
    def smtp_config(mailpit):
        """Provide SMTP config for Mailpit."""
        return SMTPConfig(
            host=mailpit.smtp_host,
            port=mailpit.smtp_port,
        )

    @pytest.fixture
    def email_config(smtp_config):
        """Provide full email config."""
        return EmailConfig(
            backend="smtp",
            from_email="test@example.com",
            smtp=smtp_config,
        )

    @pytest.fixture
    def clear_mailpit(mailpit):
        """Clear all messages before each test."""
        mailpit.clear_messages()
        yield

Integration Test Example
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import pytest
    from litestar_email import EmailMessage, get_backend

    pytestmark = pytest.mark.anyio

    async def test_smtp_sends_email(email_config, mailpit, clear_mailpit):
        """Test that emails are actually delivered via SMTP."""
        message = EmailMessage(
            subject="Integration Test",
            body="This is a test email.",
            from_email="sender@example.com",
            to=["recipient@example.com"],
        )

        backend = get_backend("smtp", config=email_config)
        async with backend:
            count = await backend.send_messages([message])

        assert count == 1

        # Verify via Mailpit API
        messages = mailpit.get_messages()
        assert len(messages) == 1
        assert messages[0]["Subject"] == "Integration Test"

MailpitContainer API
^^^^^^^^^^^^^^^^^^^^

The ``MailpitContainer`` class provides:

+----------------------+-------------------------------------------+
| Method/Property      | Description                               |
+======================+===========================================+
| ``start()``          | Start the container                       |
+----------------------+-------------------------------------------+
| ``stop()``           | Stop and remove the container             |
+----------------------+-------------------------------------------+
| ``is_running()``     | Check if container is running             |
+----------------------+-------------------------------------------+
| ``is_available``     | Check if Docker/Podman is available       |
+----------------------+-------------------------------------------+
| ``smtp_host``        | SMTP hostname (localhost)                 |
+----------------------+-------------------------------------------+
| ``smtp_port``        | SMTP port (default: 1025)                 |
+----------------------+-------------------------------------------+
| ``web_url``          | Web UI URL (http://localhost:8025)        |
+----------------------+-------------------------------------------+
| ``clear_messages()`` | Delete all messages via API               |
+----------------------+-------------------------------------------+
| ``get_messages()``   | Retrieve all messages via API             |
+----------------------+-------------------------------------------+

Mocking API Backends
--------------------

For Resend and SendGrid backends, use ``respx`` to mock HTTP responses:

.. code-block:: python

    import httpx
    import pytest
    import respx
    from litestar_email import EmailMessage
    from litestar_email.backends.resend import RESEND_API_URL, ResendBackend
    from litestar_email.config import ResendConfig

    pytestmark = pytest.mark.anyio

    @respx.mock
    async def test_resend_sends_email():
        """Test Resend backend with mocked API."""
        # Mock successful response
        respx.post(RESEND_API_URL).mock(
            return_value=httpx.Response(200, json={"id": "msg_123"})
        )

        config = ResendConfig(api_key="re_test_key")
        backend = ResendBackend(config=config)

        message = EmailMessage(
            subject="Test",
            body="Body",
            from_email="sender@example.com",
            to=["recipient@example.com"],
        )

        count = await backend.send_messages([message])
        assert count == 1

    @respx.mock
    async def test_resend_rate_limit():
        """Test rate limit handling."""
        from litestar_email.exceptions import EmailRateLimitError

        respx.post(RESEND_API_URL).mock(
            return_value=httpx.Response(429, headers={"Retry-After": "60"})
        )

        config = ResendConfig(api_key="re_test_key")
        backend = ResendBackend(config=config)

        message = EmailMessage(
            subject="Test",
            body="Body",
            to=["test@example.com"],
        )

        with pytest.raises(EmailRateLimitError) as exc_info:
            await backend.send_messages([message])

        assert exc_info.value.retry_after == 60
