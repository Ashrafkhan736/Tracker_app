from email import encoders
from email.mime.base import MIMEBase
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Read from congif

SMTP_SERVER_HOST = "localhost"
SMTP_SERVER_PORT = 1025
SENDER_ADDRESS = "email@gmail.com"
SENDER_PASSWORD = ""


def send_email(to, sub, message, content_type="html", attachment=None):
    msg = MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = to
    msg['Subject'] = sub
    if content_type == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))
    if attachment:
        with open(attachment, "rb") as file:
            # Add file as application / octect-stream
            part = MIMEBase("application", "octect-stream")
            part.set_payload(file.read())
        # Email attachment are send as base64 encoded
        encoders.encode_base64(part)
        part.add_header("Content-Disposition",
                        f"attachment; filename= {attachment}")
        msg.attach(part)
    s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    return True


def main():
    new_users = [
        {"name": "Raj", "email": "raj@example.com"},
        {"name": "Ashraf", "email": "ashraf@example.com"}
    ]
    for user in new_users:
        send_email(user["email"], sub="Hello", message="Welcom to mailhog",
                   content_type="html", attachment="./requirements.txt")


if __name__ == "__main__":
    main()
