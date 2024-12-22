from django.core.exceptions import ObjectDoesNotExist
from .models import EmailVerification
from django.template.loader import render_to_string
from .tasks import send_email_task
from django.urls import reverse
from django.contrib.sites.models import Site
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
