Quickstart
==========

This guide will help you get started with litestar-email quickly.

Installation
------------

Install the base package:

.. code-block:: bash

    pip install litestar-email

For production use, install with your preferred backend:

.. code-block:: bash

    # SMTP backend (aiosmtplib)
    pip install litestar-email[smtp]

    # Resend API backend
    pip install litestar-email[resend]

    # SendGrid API backend
    pip install litestar-email[sendgrid]

    # All backends
    pip install litestar-email[all]

Basic Setup
-----------

Configure the email plugin with your Litestar application:

.. code-block:: python

    from litestar import Litestar
    from litestar_email import EmailConfig, EmailPlugin

    # Development configuration (console output)
    config = EmailConfig(
        backend="console",
        from_email="noreply@example.com",
        from_name="My App",
    )

    app = Litestar(plugins=[EmailPlugin(config=config)])

Sending Emails
--------------

Create and send email messages:

.. code-block:: python

    from litestar_email import EmailMessage

    # Create a message
    message = EmailMessage(
        subject="Welcome!",
        body="Thanks for signing up.",
        to=["user@example.com"],
    )

    # Send using the configured service
    async for mailer in config.provide_service():
        await mailer.send_message(message)

When ``message.from_email`` is omitted, the service uses ``config.from_email`` and
``config.from_name`` as defaults.

HTML Emails
-----------

Send emails with HTML content:

.. code-block:: python

    message = EmailMessage(
        subject="Welcome!",
        body="Thanks for signing up.",  # Plain text fallback
        to=["user@example.com"],
    )
    message.attach_alternative(
        "<h1>Welcome!</h1><p>Thanks for signing up.</p>",
        "text/html",
    )

Using Inside a Handler
----------------------

The plugin registers a ``mailer`` dependency for handlers by default:

.. code-block:: python

    from litestar import get
    from litestar_email import EmailMessage, EmailService

    @get("/welcome/{email:str}")
    async def send_welcome(email: str, mailer: EmailService) -> dict[str, str]:
        message = EmailMessage(
            subject="Welcome!",
            body="Thanks for signing up.",
            to=[email],
        )

        await mailer.send_message(message)
        return {"status": "sent"}

For use outside Litestar, call ``config.get_service()`` for a one-off service or
``config.provide_service()`` for batch sending.

Events and Listeners
--------------------

Litestar listeners do not support DI, so pass the service explicitly when emitting:

.. code-block:: python

    from litestar import Litestar, Request, get
    from litestar.events import listener
    from litestar_email import EmailConfig, EmailMessage, EmailPlugin, EmailService

    config = EmailConfig(
        backend="smtp",
        from_email="noreply@example.com",
        from_name="My App",
    )

    @listener("user.registered")
    async def on_user_registered(email: str, mailer: EmailService) -> None:
        message = EmailMessage(
            subject="Welcome!",
            body="Thanks for signing up.",
            to=[email],
        )
        await mailer.send_message(message)

    @get("/register/{email:str}")
    async def register(email: str, request: Request) -> dict[str, str]:
        request.app.emit(
            "user.registered",
            email,
            mailer=config.get_service(request.app.state),
        )
        return {"status": "queued"}

    app = Litestar(
        plugins=[EmailPlugin(config=config)],
        listeners=[on_user_registered],
    )

You can override the dependency and state keys via ``EmailConfig`` if needed:
``email_service_dependency_key="email_service"`` and ``email_service_state_key="email_service"``.
If you have the plugin instance available, use ``plugin.get_service(request.app.state)``.

Attachments
-----------

Add file attachments to emails:

.. code-block:: python

    message = EmailMessage(
        subject="Your Report",
        body="Please find your report attached.",
        to=["user@example.com"],
    )
    message.attach(
        filename="report.pdf",
        content=pdf_bytes,
        mimetype="application/pdf",
    )

Next Steps
----------

- :doc:`backends` - Configure production email backends
- :doc:`testing` - Test email functionality with Mailpit
