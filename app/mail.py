from flask import render_template
from flask_mail import Message
from . import mail
from config import ConfigClass


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Сброс пароля',
               sender=ConfigClass.MAIL_DEFAULT_SENDER,
               recipients=[user.email],
               html_body=render_template('email/reset_password_text.html',
                                         user=user, token=token))


def send_email_confirm_email(user):
    token = user.get_confirm_email_token()
    send_email('Подтвердите адрес электронной почты',
               sender=ConfigClass.MAIL_DEFAULT_SENDER,
               recipients=[user.email],
               html_body=render_template('email/confirm_email_text.html',
                                         user=user, token=token))