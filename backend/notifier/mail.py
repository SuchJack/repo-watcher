"""
邮件通知（用户自配置 SMTP）。
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def send(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    smtp_use_tls: bool,
    from_addr: str,
    to_addrs: list[str],
    subject: str,
    body: str,
):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        if smtp_use_tls and smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
            if smtp_use_tls:
                server.starttls()

        server.login(smtp_user, smtp_password)
        server.sendmail(from_addr, to_addrs, msg.as_string())
        server.quit()
        logger.info("邮件已发送: %s -> %s", subject, to_addrs)
    except Exception as e:
        logger.error("邮件发送失败: %s", e)
