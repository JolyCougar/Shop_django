from django.core.exceptions import ObjectDoesNotExist
from .models import EmailVerification
from .tasks import send_verification_email_task
from django.urls import reverse
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
            print('im here service')
            send_verification_email_task.delay(verification_link, user.email, email_verification.token)
        except ObjectDoesNotExist:
            logger.error(f"Не найден профиль для пользователя: {user.id}")

        except Exception as e:
            logger.error(f"Ошибка отправки письма подтверждения E-mail: {str(e)}")
