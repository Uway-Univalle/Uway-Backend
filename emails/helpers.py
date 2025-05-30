import os

from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_admin_credentials_email(username, plain_password, college_name, email_to):
    context = {
        "username" : username,
        "password": plain_password,
        "college_name": college_name
    }
    message = render_to_string("emails/verification_college_email.txt", context)

    send_mail(
        subject="Credenciales de Acceso a Uway - Administrador Institucional",
        message= message,
        from_email= os.environ.get("EMAIL_HOST_USER"),
        recipient_list=[email_to],
        fail_silently=False
    )

def send_verification_notification_to_user(full_name, email_to):
    context = {
        "full_name": full_name
    }
    message = render_to_string("emails/user_verification_email.txt", context)

    send_mail(
        subject="¡Has sido verificado!",
        message=message,
        from_email=os.environ.get("EMAIL_HOST_USER"),
        recipient_list=[email_to],
        fail_silently=False
    )