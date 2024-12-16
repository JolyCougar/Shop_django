from decouple import config
from django.core.mail import send_mail
from django.utils.html import strip_tags
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email_task(html_message, user_email, subject):
    try:
        text_message = strip_tags(html_message)

        send_mail(
            subject,
            text_message,
            config('EMAIL_HOST_USER'),
            [user_email],
            fail_silently=False,
            html_message=html_message,
        )
        logger.info(f'Письмо было отправлено на {user_email}')
    except Exception as e:
        logger.error(f'Неудачная попытка отправить письмо пользователю на E-mail: {user_email}: {str(e)}')
