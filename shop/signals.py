from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Product, ProductImage, Marketing
import os


@receiver(pre_save, sender=Product)
def delete_old_preview_on_update(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Product.objects.get(pk=instance.pk)
        if old_instance.preview and old_instance.preview != instance.preview:
            if os.path.isfile(old_instance.preview.path):
                os.remove(old_instance.preview.path)


@receiver(post_delete, sender=ProductImage)
def delete_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(pre_save, sender=ProductImage)
def delete_old_image_on_update(sender, instance, **kwargs):
    if instance.pk:
        old_instance = ProductImage.objects.get(pk=instance.pk)
        if old_instance.image and old_instance.image != instance.image:
            if os.path.isfile(old_instance.image.path):
                os.remove(old_instance.image.path)


@receiver(pre_save, sender=Marketing)
def delete_old_avatar(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_preview = Marketing.objects.get(pk=instance.pk).image
        except Marketing.DoesNotExist:
            old_preview = None

        if old_preview and old_preview != instance.image:
            if os.path.isfile(old_preview.path):
                os.remove(old_preview.path)
