import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SENDER_EMAIL = "abdullahmustafa2435@gmail.com"
SENDER_PASSWORD = "iazi iycs jjjg epeg"


def send_email(recipient_email, subject, body):
    """
    Sends a registration OTP email to the recipient.

    Args:
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        otp (str): The OTP to include in the email body.

    Returns:
        None
    """
    try:
        # Prepare email message
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            server.quit()

        print("Registration email sent successfully!")

    except smtplib.SMTPException as smtp_err:
        print(f"SMTP error occurred: {smtp_err}")
    except Exception as e:
        print(f"Failed to send registration email: {e}")
