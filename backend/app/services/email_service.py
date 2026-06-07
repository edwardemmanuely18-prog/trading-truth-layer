import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

EMAIL_FROM = os.getenv(
    "EMAIL_FROM",
    "noreply@tradingtruthlayer.com",
)

SUPPORT_EMAIL = os.getenv(
    "SUPPORT_EMAIL",
    "support@tradingtruthlayer.com",
)


def send_email(
    to_email: str,
    subject: str,
    html: str,
):
    try:
        resend.Emails.send(
            {
                "from": EMAIL_FROM,
                "to": [to_email],
                "subject": subject,
                "html": html,
            }
        )

    except Exception as exc:
        print(
            f"EMAIL ERROR: {exc}",
            flush=True,
        )


def send_verification_email(
    email: str,
    name: str,
    verification_url: str,
):
    html = f"""
    <h2>Verify your Trading Truth Layer account</h2>

    <p>Hello {name},</p>

    <p>
    Please verify ownership of your email address before
    using Trading Truth Layer.
    </p>

    <p>
        <a href="{verification_url}">
            Verify Email
        </a>
    </p>

    <p>
    If you did not create this account, you may ignore
    this message.
    </p>

    <p>
    Trading Truth Layer
    </p>
    """

    send_email(
        email,
        "Verify your Trading Truth Layer account",
        html,
    )


def send_password_reset_email(
    email: str,
    name: str,
    reset_url: str,
):
    html = f"""
    <h2>Password Reset Request</h2>

    <p>Hello {name},</p>

    <p>
    A password reset request was submitted for your
    Trading Truth Layer account.
    </p>

    <p>
        <a href="{reset_url}">
            Reset Password
        </a>
    </p>

    <p>
    If you did not request a password reset, you can
    safely ignore this email.
    </p>

    <p>
    Trading Truth Layer
    </p>
    """

    send_email(
        email,
        "Reset your Trading Truth Layer password",
        html,
    )


def send_welcome_email(
    email: str,
    name: str,
):
    html = f"""
    <h2>Welcome to Trading Truth Layer</h2>

    <p>Hello {name},</p>

    <p>
    Your account has been successfully created.
    </p>

    <p>
    Trading Truth Layer provides governed claim creation,
    canonical trade ledgers, evidence generation,
    verification workflows, and public proof surfaces.
    </p>

    <p>
    Need help?
    Contact {SUPPORT_EMAIL}
    </p>

    <p>
    Trading Truth Layer
    </p>
    """

    send_email(
        email,
        "Welcome to Trading Truth Layer",
        html,
    )