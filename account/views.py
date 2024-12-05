from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from shop.models import Product, Cart, CartItem
from .forms import CustomUserCreationForm, CustomPasswordChangeForm, ProfileUpdateForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView
from .models import CustomUser
import logging

log = logging.getLogger(__name__)


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('shop:product-list')

    def form_valid(self, form):
        messages.success(self.request, 'Ваш аккаунт был успешно создан!')
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'account/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()

        cart_data = self.request.session.get('cart', {})
        if cart_data:
            cart, created = Cart.objects.get_or_create(user=user)

            for product_id, quantity in cart_data.items():
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    continue

                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

                if created:
                    cart_item.quantity = quantity
                else:
                    cart_item.quantity += quantity
                cart_item.save()

            if 'cart' in self.request.session:
                del self.request.session['cart']

        return response


class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        log.info(f'User {request.user.username} вышел из системы.')
        response = super().get(request, *args, **kwargs)
        return response


class ProfileView(DetailView):
    model = CustomUser
    template_name = "account/profile.html"
    context_object_name = "user"


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "account/password_change.html"
    form_class = CustomPasswordChangeForm


class ChangeProfileInfoView(UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'account/update_profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('account:profile', kwargs={'pk': self.request.user.pk})


class ClearAvatarView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.avatar:
            user.avatar.delete()
        user.avatar = None
        user.save()
        return JsonResponse({'success': True})
