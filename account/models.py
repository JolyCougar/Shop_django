import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class AvatarPathGenerator:
    @staticmethod
    def user_avatar_directory_path(instance: "CustomUser", filename: str) -> str:
        return "user_{pk}/{filename}".format(
            pk=instance.pk,
            filename=filename,
        )


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    cookies_accepted = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=AvatarPathGenerator.user_avatar_directory_path, blank=True, null=True)


class EmailVerification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)