import pytest

pytestmark = pytest.mark.anyio


def test_email_message_creation() -> None:
    """Test that EmailMessage can be created with required fields."""
    from litestar_email import EmailMessage

    message = EmailMessage(
        subject="Test Subject",
        body="Test body",
        to=["recipient@example.com"],
    )
    assert message.subject == "Test Subject"
    assert message.body == "Test body"
    assert message.to == ["recipient@example.com"]
    assert message.from_email is None
    assert message.cc == []
    assert message.bcc == []


def test_email_message_with_all_fields() -> None:
    """Test that EmailMessage accepts all optional fields."""
    from litestar_email import EmailMessage

    message = EmailMessage(
        subject="Test Subject",
        body="Test body",
        from_email="sender@example.com",
        to=["to@example.com"],
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
        reply_to=["reply@example.com"],
        headers={"X-Custom": "value"},
    )
    assert message.from_email == "sender@example.com"
    assert message.cc == ["cc@example.com"]
    assert message.bcc == ["bcc@example.com"]
    assert message.reply_to == ["reply@example.com"]
    assert message.headers == {"X-Custom": "value"}


def test_email_message_attach() -> None:
    """Test that attachments can be added to a message."""
    from litestar_email import EmailMessage

    message = EmailMessage(subject="Test", body="Body", to=["test@example.com"])
    message.attach("file.pdf", b"content", "application/pdf")

    assert len(message.attachments) == 1
    assert message.attachments[0] == ("file.pdf", b"content", "application/pdf")


def test_email_message_attach_alternative() -> None:
    """Test that alternative content can be added to a message."""
    from litestar_email import EmailMessage

    message = EmailMessage(subject="Test", body="Plain text", to=["test@example.com"])
    message.attach_alternative("<h1>HTML</h1>", "text/html")

    assert len(message.alternatives) == 1
    assert message.alternatives[0] == ("<h1>HTML</h1>", "text/html")


def test_email_message_recipients() -> None:
    """Test that recipients() returns all recipients."""
    from litestar_email import EmailMessage

    message = EmailMessage(
        subject="Test",
        body="Body",
        to=["to1@example.com", "to2@example.com"],
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
    )

    recipients = message.recipients()
    assert len(recipients) == 4
    assert "to1@example.com" in recipients
    assert "to2@example.com" in recipients
    assert "cc@example.com" in recipients
    assert "bcc@example.com" in recipients


def test_email_multi_alternatives_auto_attach() -> None:
    """Test that EmailMultiAlternatives auto-attaches HTML body."""
    from litestar_email import EmailMultiAlternatives

    message = EmailMultiAlternatives(
        subject="Test",
        body="Plain text",
        html_body="<h1>HTML</h1>",
        to=["test@example.com"],
    )

    assert len(message.alternatives) == 1
    assert message.alternatives[0] == ("<h1>HTML</h1>", "text/html")


def test_email_multi_alternatives_no_html() -> None:
    """Test EmailMultiAlternatives without HTML body."""
    from litestar_email import EmailMultiAlternatives

    message = EmailMultiAlternatives(
        subject="Test",
        body="Plain text only",
        to=["test@example.com"],
    )

    assert len(message.alternatives) == 0
