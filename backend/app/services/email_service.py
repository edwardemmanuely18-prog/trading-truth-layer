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
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">

        <h1 style="color:#111827;margin-bottom:20px;">
            Verify Your Email Address
        </h1>

        <p>Hello {name},</p>

        <p>
            Welcome to Trading Truth Layer.
            Before continuing, please verify ownership of your email address.
        </p>

        <div style="text-align:center;margin:40px 0;">

            <a
                href="{verification_url}"
                style="
                    background:#111827;
                    color:#ffffff;
                    padding:18px 40px;
                    text-decoration:none;
                    border-radius:12px;
                    font-size:18px;
                    font-weight:700;
                    display:inline-block;
                "
            >
                VERIFY EMAIL
            </a>

        </div>

        <p>
            If you did not create this account, you may safely ignore this email.
        </p>

        <p>
            If the button above does not work, copy and paste this link:
        </p>

        <p>
            {verification_url}
        </p>

        <hr style="margin:30px 0;">

        <p style="color:#6b7280;">
            Trading Truth Layer
        </p>

    </div>
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
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">

        <h1 style="color:#111827;margin-bottom:20px;">
            Reset Your Password
        </h1>

        <p>Hello {name},</p>

        <p>
            A request was made to reset the password for your
            Trading Truth Layer account.
        </p>

        <div style="text-align:center;margin:40px 0;">

            <a
                href="{reset_url}"
                style="
                    background:#dc2626;
                    color:#ffffff;
                    padding:18px 40px;
                    text-decoration:none;
                    border-radius:12px;
                    font-size:18px;
                    font-weight:700;
                    display:inline-block;
                "
            >
                RESET PASSWORD
            </a>

        </div>

        <p>
            If you did not request a password reset,
            you may safely ignore this email.
        </p>

        <p>
            If the button above does not work, copy and paste this link:
        </p>

        <p>
            {reset_url}
        </p>

        <hr style="margin:30px 0;">

        <p style="color:#6b7280;">
            Trading Truth Layer
        </p>

    </div>
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
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">

        <h1 style="color:#111827;">
            Welcome to Trading Truth Layer
        </h1>

        <p>Hello {name},</p>

        <p>
            Your account has been successfully verified and activated.
        </p>

        <p>
            Trading Truth Layer provides governed claim creation,
            canonical trade ledgers,
            evidence generation,
            verification workflows,
            dispute handling,
            and public proof surfaces.
        </p>

        <p>
            Need assistance?
        </p>

        <p>
            {SUPPORT_EMAIL}
        </p>

        <hr style="margin:30px 0;">

        <p style="color:#6b7280;">
            Trading Truth Layer
        </p>

    </div>
    """

    send_email(
        email,
        "Welcome to Trading Truth Layer",
        html,
    )