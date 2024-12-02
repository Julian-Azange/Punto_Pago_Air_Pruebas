import os
import smtplib, ssl
from email.message import EmailMessage
from dotenv import load_dotenv

from dotenv import load_dotenv
 
load_dotenv()  # take environment variables from .env.
 
# import logging

class EmailHelper:
    def send_payment_email(payment_code):
        payment_code = payment_code

        email_sender = "pdptestpy@gmail.com"
        password = os.getenv("EMAIL_PASSWORD")
        email_receiver = os.getenv("EMAIL_RECIEVER")

        body = f"""\
            Hola, gracias por realizar una reserva con nosotros.
            Aquí está tu código de pago: {payment_code}
        """
        em = EmailMessage()
        em["From"] = email_sender
        em["To"] = email_receiver
        em["Subject"] = "Código de pago PDP"
        em.set_content(body)
        
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp_server:
            smtp_server.login(email_sender, password)
            smtp_server.sendmail(email_sender, email_receiver, em.as_string())

    def send_booking_paid_notification():
        email_sender = "pdptestpy@gmail.com"
        password = os.getenv("EMAIL_PASSWORD")
        email_receiver = os.getenv("EMAIL_RECIEVER")

        body = f"""\
            Hola, gracias por realizar el pago de tu reserva con nosotros.
            Sigue disfrutando de nuestros servicios en nuestra página.
        """
        em = EmailMessage()
        em["From"] = email_sender
        em["To"] = email_receiver
        em["Subject"] = "Notificación pago satisfactorio - PDP Airlines"
        em.set_content(body)
        
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp_server:
            smtp_server.login(email_sender, password)
            smtp_server.sendmail(email_sender, email_receiver, em.as_string())
