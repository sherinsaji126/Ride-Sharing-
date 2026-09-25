import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv("Credentials.env")

def send_otp_email(receiver_email: str, otp: str):

    sender_email = os.getenv("SENDER_EMAIL") 
    app_password = os.getenv("APP_PASSWORD")

    subject = "Password Reset OTP"

    body = f"""Hello,
    
    Your password reset OTP is: {otp}
    
    This OTP will expire in 5 minutes.
    
    If you did not request a password reset, please ignore this email.
    
    Note : This mail has been sent to you for learning purpose only

    Regards,
    Sherin Saji 
    
    """

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:

        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(message)