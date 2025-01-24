from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import Product
import os


@receiver(pre_save, sender=Product)
def delete_old_image_on_update(sender, instance, **kwargs):
    if instance.pk:
        old_image = Product.objects.get(pk=instance.pk).images
        if old_image and old_image != instance.image:
            if os.path.isfile(old_image.path):
                os.remove(old_image.path)


@receiver(pre_delete, sender=Product)
def delete_image_on_delete(sender, instance, **kwargs):
    if instance.images:
        if os.path.isfile(instance.images.path):
            os.remove(instance.images.path)
