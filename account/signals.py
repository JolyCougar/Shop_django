from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from shop.models import Cart, CartItem, Product


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
