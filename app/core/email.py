import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def _load_template(name: str, **kwargs) -> str:
    """Load an HTML template file and substitute {{variable}} placeholders."""
    path = TEMPLATE_DIR / name
    html = path.read_text(encoding="utf-8")
    for key, value in kwargs.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))
    return html


async def send_email(to: str, subject: str, html_body: str) -> bool:
    """Send an email via Google SMTP. Returns True on success."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise RuntimeError("SMTP credentials are not configured.")

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(msg["From"], to, msg.as_string())

    return True


async def send_verification_code(to: str, code: str) -> bool:
    """Send a 6-digit verification code email."""
    html = _load_template(
        "verify_email.html",
        code=code,
        expire_minutes=settings.EMAIL_VERIFY_CODE_EXPIRE_MINUTES,
        app_name=settings.SMTP_FROM_NAME,
    )
    return await send_email(to, "Your verification code", html)


async def send_password_reset_code(to: str, code: str) -> bool:
    """Send a 6-digit password reset code email."""
    html = _load_template(
        "reset_password.html",
        code=code,
        expire_minutes=settings.EMAIL_VERIFY_CODE_EXPIRE_MINUTES,
        app_name=settings.SMTP_FROM_NAME,
    )
    return await send_email(to, "Your password reset code", html)
