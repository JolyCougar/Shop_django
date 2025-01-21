from django.core.exceptions import ObjectDoesNotExist
from .models import EmailVerification
from django.template.loader import render_to_string
from .tasks import send_email_task
from django.urls import reverse
from decouple import config
import random
import string
import logging

logger = logging.getLogger('__name__')


class EmailService:

    @staticmethod
    def send_verification_email(request, user):
        try:
            # Создаем или получаем токен верификации
            email_verification, created = EmailVerification.objects.get_or_create(user=user)
            # Генерируем ссылку для подтверждения
            verification_link = request.build_absolute_uri(
                reverse('account:verify_email', args=[email_verification.token])
            )
            # Отправляем электронное письмо асинхронно
            subject = 'MyShop: Добро пожаловать!'
            html_message = render_to_string('account/email/messages_to_verification.html', {
                'verification_link': verification_link,
            })
            send_email_task.delay(html_message, user.email, subject)
        except ObjectDoesNotExist:
            logger.error(f"Не найден профиль для пользователя: {user.id}")

        except Exception as e:
            logger.error(f"Ошибка отправки письма подтверждения E-mail: {str(e)}")

    @staticmethod
    def send_new_password(user, password):
        subject = 'MyShop: Ваш новый пароль'
        html_message = render_to_string('account/email/messages_to_new_password.html', {
            'new_password': password,
        })
        send_email_task.delay(html_message, user.email, subject)

    @staticmethod
    def send_new_promotion(subscribers, instance, request):
        users_list = subscribers

        promotion_link = request.build_absolute_uri(
            reverse('shop:promotion_detail', args=[instance.url])
        )

        for subscription in users_list:
            user = subscription.user
            subject = f'MyShop: У нас новая акция {instance.name}!'
            html_message = render_to_string('account/email/new_promotion.html', {
                'user_name': subscription.user.username,
                'promotion_name': instance.name,
                'link': promotion_link

            })

            send_email_task.delay(html_message, user.email, subject)

    @staticmethod
    def send_info_new_order(users, instance):
        users_list = users

        for subscription in users_list:
            user = subscription.user
            subject = f'MyShop: У нас новый заказ {instance.pk}!'
            html_message = render_to_string('account/email/messages_new_order.html', {
                'user_name': subscription.user.username,
                'order_number': instance.pk,
            })
            send_email_task.delay(html_message, user.email, subject)

    @staticmethod
    def send_email_from_admin(edit_subject, message, user):
        subject = f'MyShop: {edit_subject}!'
        html_message = render_to_string('account/email/message_from_administrators.html', {
            'user_name': user.username,
            'message': message,
            'email_for_message': config('EMAIL_HOST_USER'),
        })
        send_email_task.delay(html_message, user.email, subject)

    @staticmethod
    def notify_change_order_status(order_pk, order_status, username_send, user_email_send):
        subject = f'MyShop: Статус вашего заказа поменялся!'
        html_message = render_to_string('account/email/messages_info_status_order.html', {
            'user_name': username_send,
            'order_status': order_status,
            'order_number': order_pk
        })
        send_email_task.delay(html_message, user_email_send, subject)


class PasswordGenerator:
    """
    Генератор паролей
     """

    @staticmethod
    def generate_random_password(length=8):
        """
        Генерация случайного пароля заданной длины.
        """
        if length < 1:
            raise ValueError("Длина пароля должна быть больше 0")

        password = [random.choice(string.digits)]
        characters = string.ascii_letters + string.digits + string.punctuation
        password += random.choices(characters, k=length - 1)
        random.shuffle(password)

        return ''.join(password)
