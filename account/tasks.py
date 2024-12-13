from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from celery import shared_task
import logging


logger = logging.getLogger(__name__)


@shared_task
def send_verification_email_task(verification_link, user_email, token):
    try:
        # Генерируем HTML-содержимое письма
        html_message = render_to_string('account/email/messages_to_verification.html', {
            'verification_link': verification_link,
            'token': token
        })

        # Создаем текстовую версию письма (для почтовых клиентов, которые не поддерживают HTML)
        text_message = strip_tags(html_message)

        send_mail(
            'toDo app: Добро пожаловать!',
            text_message,
            'EMAIL_HOST_USER',
            [user_email],
            fail_silently=False,
            html_message=html_message,  # Добавляем HTML-содержимое
        )
        logger.info(f'Письмо с подтверждением было отправлено на {user_email}')
    except Exception as e:
        logger.error(f'Неудачная попытка отправить письмо пользователю на E-mail: {user_email}: {str(e)}')
