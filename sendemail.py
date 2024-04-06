import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, html_body):

    #when on git hub it will fail since I will not upload the file with them
    try:
        from set_env_variables import set_env_variables
        set_env_variables()
    except Exception as e:
        print(e)

    try:
        smtp_user = os.environ["SMTP_USER"]
        smtp_password = os.environ["SMTP_PASSWORD"]
        smtp_server = os.environ["SMTP_SERVER"]
        smtp_port = int(os.environ["SMTP_PORT"])
        sender_email = os.environ["SENDER_EMAIL"]
        to_email = os.environ["TO_EMAIL"]

        # Construct the email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(html_body, 'html'))

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Start TLS for security (optional)
            server.starttls()

            # Log in to the email account
            server.login(smtp_user, smtp_password)

            # Send the email
            server.sendmail(sender_email, to_email, message.as_string())

        print('Email sent successfully!')
    except Exception as e:
        print(e)
