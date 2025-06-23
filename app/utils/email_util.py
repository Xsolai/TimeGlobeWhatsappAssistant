import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core.config import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)


def send_email(recipient_email, subject, body, sender_name=None):
    """
    Sends an email to the recipient using the configured SMTP settings.

    Args:
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The email body content.
        sender_name (str, optional): The sender's display name. Defaults to configured name.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    try:
        # Use sender name from parameter or default from settings
        from_name = sender_name or settings.EMAIL_FROM_NAME
        from_address = f"{from_name} <{settings.EMAIL_FROM}>"
        
        # Prepare email message
        msg = MIMEMultipart()
        msg["From"] = from_address
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server
        logger.info(f"Connecting to SMTP server: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                logger.info("Enabling TLS encryption")
                server.starttls()  # Enable TLS encryption
            
            logger.info(f"Logging in with username: {settings.SMTP_USERNAME}")
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            server.sendmail(settings.EMAIL_FROM, recipient_email, msg.as_string())

        logger.info(f"Email sent successfully to {recipient_email}")
        return True

    except smtplib.SMTPAuthenticationError as auth_err:
        logger.error(f"SMTP Authentication failed: {auth_err}")
        logger.error(f"Check SMTP credentials for {settings.SMTP_USERNAME}")
        return False
    except smtplib.SMTPRecipientsRefused as recip_err:
        logger.error(f"SMTP Recipients refused: {recip_err}")
        return False
    except smtplib.SMTPServerDisconnected as disc_err:
        logger.error(f"SMTP Server disconnected: {disc_err}")
        return False
    except smtplib.SMTPException as smtp_err:
        logger.error(f"SMTP error occurred: {smtp_err}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def send_otp_email(recipient_email, otp, business_name=None):
    """
    Sends an OTP verification email.

    Args:
        recipient_email (str): The recipient's email address.
        otp (str): The OTP code.
        business_name (str, optional): The business name for personalization.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    subject = "Your OTP Verification Code - TimeGlobe"
    
    if business_name:
        greeting = f"Dear {business_name},"
    else:
        greeting = "Dear User,"
    
    body = f"""{greeting}

Your OTP verification code is: {otp}

This code is valid for 5 minutes only. Please do not share this code with anyone.

If you did not request this code, please ignore this email.

Best regards,
TimeGlobe Team

---
This is an automated email. Please do not reply to this message.
"""
    logger.info(f"Sending OTP email to {recipient_email} with OTP: {otp}")
    return send_email(recipient_email, subject, body)


def send_password_reset_email(recipient_email, reset_link, business_name=None):
    """
    Sends a password reset email.

    Args:
        recipient_email (str): The recipient's email address.
        reset_link (str): The password reset link.
        business_name (str, optional): The business name for personalization.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    subject = "Reset Your Password - TimeGlobe"
    
    if business_name:
        greeting = f"Dear {business_name},"
    else:
        greeting = "Dear User,"
    
    body = f"""{greeting}

You have requested to reset your password for your TimeGlobe account.

Click the link below to reset your password:
{reset_link}

This link is valid for a limited time. If you did not request this password reset, please ignore this email.

For security reasons, this link will expire after 24 hours.

Best regards,
TimeGlobe Team

---
This is an automated email. Please do not reply to this message.
"""
    
    return send_email(recipient_email, subject, body)
