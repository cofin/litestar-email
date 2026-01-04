Email Backends
==============

litestar-email provides multiple email backends for different use cases.
Most applications should use :class:`~litestar_email.service.EmailService` via
DI or ``EmailConfig.provide_service()`` and treat direct backend access as an
advanced/testing concern.

Available Backends
------------------

+--------------+------------------+--------------------------------+
| Backend      | Dependency       | Use Case                       |
+==============+==================+================================+
| ``console``  | None             | Development (prints to stdout) |
+--------------+------------------+--------------------------------+
| ``memory``   | None             | Testing (stores in memory)     |
+--------------+------------------+--------------------------------+
| ``smtp``     | ``aiosmtplib``   | Production SMTP servers        |
+--------------+------------------+--------------------------------+
| ``resend``   | ``httpx``        | Resend API (modern hosting)    |
+--------------+------------------+--------------------------------+
| ``sendgrid`` | ``httpx``        | SendGrid API (enterprise)      |
+--------------+------------------+--------------------------------+

SMTP Backend
------------

The SMTP backend uses `aiosmtplib <https://aiosmtplib.readthedocs.io/>`_ for
async email delivery. It supports STARTTLS, implicit SSL, and authentication.

SMTP Installation
^^^^^^^^^^^^^^^^^

.. code-block:: bash

    pip install litestar-email[smtp]

SMTP Configuration
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from litestar_email import EmailConfig, SMTPConfig

    # Basic SMTP (no encryption, no auth)
    config = EmailConfig(
        backend="smtp",
        from_email="noreply@example.com",
        backend_config=SMTPConfig(
            host="localhost",
            port=25,
        ),
    )

    # SMTP with STARTTLS (port 587)
    config = EmailConfig(
        backend="smtp",
        from_email="noreply@example.com",
        backend_config=SMTPConfig(
            host="smtp.example.com",
            port=587,
            username="user@example.com",
            password="your-password",
            use_tls=True,  # STARTTLS
        ),
    )

    # SMTP with implicit SSL (port 465)
    config = EmailConfig(
        backend="smtp",
        from_email="noreply@example.com",
        backend_config=SMTPConfig(
            host="smtp.example.com",
            port=465,
            username="user@example.com",
            password="your-password",
            use_ssl=True,  # Implicit SSL
        ),
    )

SMTPConfig Options
^^^^^^^^^^^^^^^^^^

+--------------+----------+---------+-----------------------------------+
| Option       | Type     | Default | Description                       |
+==============+==========+=========+===================================+
| ``host``     | str      | localhost | SMTP server hostname            |
+--------------+----------+---------+-----------------------------------+
| ``port``     | int      | 25      | SMTP server port                  |
+--------------+----------+---------+-----------------------------------+
| ``username`` | str|None | None    | Authentication username           |
+--------------+----------+---------+-----------------------------------+
| ``password`` | str|None | None    | Authentication password           |
+--------------+----------+---------+-----------------------------------+
| ``use_tls``  | bool     | False   | Enable STARTTLS after connecting  |
+--------------+----------+---------+-----------------------------------+
| ``use_ssl``  | bool     | False   | Use implicit SSL/TLS (port 465)   |
+--------------+----------+---------+-----------------------------------+
| ``timeout``  | int      | 30      | Connection timeout in seconds     |
+--------------+----------+---------+-----------------------------------+

Resend Backend
--------------

The Resend backend sends emails via `Resend's HTTP API <https://resend.com/>`_.
This is ideal for modern hosting platforms that block SMTP ports.

Resend Installation
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    pip install litestar-email[resend]

Resend Configuration
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from litestar_email import EmailConfig, ResendConfig

    config = EmailConfig(
        backend="resend",
        from_email="noreply@yourdomain.com",
        backend_config=ResendConfig(
            api_key="re_xxxxxxxxxxxxxxxxxxxxxxxxxx",
        ),
    )

Get your API key at: https://resend.com/api-keys

ResendConfig Options
^^^^^^^^^^^^^^^^^^^^

+-------------+------+---------+-----------------------------+
| Option      | Type | Default | Description                 |
+=============+======+=========+=============================+
| ``api_key`` | str  | ""      | Resend API key (re_xxx)     |
+-------------+------+---------+-----------------------------+
| ``timeout`` | int  | 30      | HTTP request timeout        |
+-------------+------+---------+-----------------------------+

SendGrid Backend
----------------

The SendGrid backend sends emails via `SendGrid's v3 API <https://sendgrid.com/>`_.
This is suitable for enterprise email delivery at scale.

SendGrid Installation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    pip install litestar-email[sendgrid]

SendGrid Configuration
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from litestar_email import EmailConfig, SendGridConfig

    config = EmailConfig(
        backend="sendgrid",
        from_email="noreply@yourdomain.com",
        backend_config=SendGridConfig(
            api_key="SG.xxxxxxxxxxxxxxxxxxxxxxxxxx",
        ),
    )

Get your API key at: https://app.sendgrid.com/settings/api_keys

SendGridConfig Options
^^^^^^^^^^^^^^^^^^^^^^

+-------------+------+---------+-----------------------------+
| Option      | Type | Default | Description                 |
+=============+======+=========+=============================+
| ``api_key`` | str  | ""      | SendGrid API key (SG.xxx)   |
+-------------+------+---------+-----------------------------+
| ``timeout`` | int  | 30      | HTTP request timeout        |
+-------------+------+---------+-----------------------------+

Error Handling
--------------

All backends raise consistent exceptions for error handling:

.. code-block:: python

    from litestar_email.exceptions import (
        EmailBackendError,      # Configuration/initialization errors
        EmailConnectionError,   # Connection failures
        EmailAuthenticationError,  # Auth failures
        EmailDeliveryError,     # Sending failures
        EmailRateLimitError,    # API rate limiting
    )

    try:
        await backend.send_messages([message])
    except EmailRateLimitError as e:
        # Wait and retry
        await asyncio.sleep(e.retry_after or 60)
    except EmailDeliveryError as e:
        # Log and handle delivery failure
        logger.error(f"Email delivery failed: {e}")
    except EmailConnectionError as e:
        # Handle connection issues
        logger.error(f"Cannot connect to email server: {e}")

Fail Silently
^^^^^^^^^^^^^

All backends support a ``fail_silently`` option that suppresses exceptions:

.. code-block:: python

    config = EmailConfig(
        backend="smtp",
        fail_silently=True,  # Suppress sending errors
        backend_config=SMTPConfig(host="localhost", port=1025),
    )

    backend = get_backend("smtp", config=config)  # uses config.fail_silently

Connection Pooling
------------------

All backends support the async context manager protocol for connection pooling:

.. code-block:: python

    backend = get_backend("smtp", config=config)

    # Connection is opened and closed per call
    await backend.send_messages([message1])
    await backend.send_messages([message2])

    # Better: Reuse connection for multiple sends
    async with backend:
        await backend.send_messages([message1])
        await backend.send_messages([message2])
        await backend.send_messages([message3])

Custom Backends
---------------

You can implement your own backend by subclassing ``BaseEmailBackend`` and registering it:

.. code-block:: python

    from litestar_email.backends import BaseEmailBackend, register_backend
    from litestar_email.exceptions import EmailDeliveryError

    @register_backend("mybackend")
    class MyBackend(BaseEmailBackend):
        __slots__ = ("_client",)

        async def open(self) -> bool:
            if self._client is not None:
                return False
            self._client = await create_client()
            return True

        async def close(self) -> None:
            if self._client is not None:
                await self._client.aclose()
                self._client = None

        async def send_messages(self, messages: list["EmailMessage"]) -> int:
            if not messages:
                return 0
            new_connection = await self.open()
            try:
                sent = 0
                for message in messages:
                    try:
                        await self._send_message(message)
                        sent += 1
                    except Exception as exc:
                        if not self.fail_silently:
                            raise EmailDeliveryError("Failed to send email") from exc
                return sent
            finally:
                if new_connection:
                    await self.close()

Use ``config.get_backend("mybackend")`` once it is registered, or use the import path
``"your_module.MyBackend"`` directly without registration.

Optional Dependencies
^^^^^^^^^^^^^^^^^^^^^

If your backend uses an optional dependency, follow the import-guard pattern:

.. code-block:: python

    try:
        import httpx as httpx_module
    except ImportError:
        httpx_module = None  # type: ignore[assignment]

    HAS_HTTPX = httpx_module is not None

    class MyBackend(BaseEmailBackend):
        def __init__(self, ...) -> None:
            if not HAS_HTTPX:
                raise EmailBackendError(
                    "httpx is required. Install with: pip install litestar-email[mybackend]"
                )

Contributing a Backend (PR)
---------------------------

When submitting a backend to this repo, include:

- Implementation under ``src/litestar_email/backends/`` with ``__slots__`` and Google-style docstrings.
- Optional dependency guards (see above) and new extras in ``pyproject.toml``.
- Registration in ``src/litestar_email/backends/__init__.py`` if it is a built-in backend.
- Tests covering success + failure paths (mock external APIs where needed).
- Documentation updates (this page + README examples if applicable).

Quality checks:

- ``make test`` and ``make lint`` must pass
- 90%+ coverage on new modules
- No ``from __future__ import annotations`` and no ``Optional[T]`` (use ``T | None``)
