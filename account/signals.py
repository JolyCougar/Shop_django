from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from shop.models import Marketing
from django.db.models.signals import post_save
from .services import EmailService
from .models import UserSubscription, CustomUser
from shop.models import Cart, CartItem, Product, Order
from django.contrib.auth.models import Group


@receiver(user_logged_in)
def transfer_cart_to_user(sender, request, user, **kwargs):
    # Получаем товары из сессии
    cart_ids = request.session.get('cart', [])

    if cart_ids:
        # Получаем или создаем корзину для пользователя
        cart, created = Cart.objects.get_or_create(user=user)

        for product_id in cart_ids:
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if not created:
                cart_item.quantity += 1  # Увеличиваем количество, если товар уже есть в корзине
                cart_item.save()

        # Очищаем сессию после переноса товаров
        del request.session['cart']


@receiver(post_save, sender=Marketing)
def notify_users_about_promotion(sender, instance, created, **kwargs):
    request = kwargs.get('request')
    if created and request:
        subscribers = UserSubscription.objects.filter(is_subscribed=True).select_related('user')
        # EmailService.send_new_promotion(subscribers, instance, request)


@receiver(post_save, sender=Order)
def notify_users_about_promotion(sender, instance, created, **kwargs):
    request = kwargs.get('request')
    if created and request:
        moderator_group = Group.objects.get(name='Модераторы')
        users = CustomUser.objects.filter(is_superuser=True) | CustomUser.objects.filter(groups=moderator_group)
        user_list = list(users)
        # EmailService.send_info_new_order(user_list, instance)


@receiver(post_save, sender=Order)
def notify_users_about_change_status(sender, instance, created, **kwargs):
    order_pk = kwargs.get('order_pk')
    order_status = kwargs.get('order_status')
    username_send = kwargs.get('username_send')
    user_email_send = kwargs.get('user_email_send')
    if not created:
        EmailService.notify_change_order_status(order_pk, order_status, username_send, user_email_send)
