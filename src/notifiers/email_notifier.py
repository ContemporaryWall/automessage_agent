import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import settings
import structlog

logger = structlog.get_logger()

def send_email_briefing(subject: str, html_body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = ", ".join(settings.EMAIL_RECIPIENTS)

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, settings.EMAIL_RECIPIENTS, msg.as_string())
        logger.info("Email briefing sent", recipients=settings.EMAIL_RECIPIENTS)
    except Exception as e:
        logger.error("Failed to send email", error=str(e))
        raise