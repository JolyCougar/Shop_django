from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.views.generic import CreateView, DetailView, UpdateView
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from shop.models import Product, Cart, CartItem
from .forms import CustomUserCreationForm, CustomPasswordChangeForm, ProfileUpdateForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView
from .models import CustomUser, EmailVerification, UserSubscription
from .services import EmailService, PasswordGenerator
from django.views.decorators.cache import cache_page
import logging

log = logging.getLogger(__name__)


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('shop:product-list')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        messages.success(self.request, 'Ваш аккаунт был успешно создан!')

        try:
            EmailService.send_verification_email(self.request, user)
            message_success = 'Регистрация прошла успешна! Проверьте вашу почту для подтверждения. '
            messages.success(self.request, message_success)
        except Exception as e:
            log.error(f"Произошла ошибка отправки письма с подтверждением {str(e)}")
            message_warning = ('Регистрация успешна, но не удалось отправить письмо с подтверждением. '
                               'Пожалуйста попробуйте отправить письмо через несколько минут')
            messages.warning(self.request, message_warning)

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


class ManageUsersView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'account/manage_users.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = CustomUser.objects.all()
        context['groups'] = Group.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            messages.error(request, "Пользователь не найден.")
            return redirect('account:manage_users')

        if action == 'block':
            user.is_active = False
            user.save()
            messages.success(request, f"Пользователь {user.username} был заблокирован.")
        elif action == 'unblock':
            user.is_active = True
            user.save()
            messages.success(request, f"Пользователь {user.username} был разблокирован.")
        elif action == 'add_to_group':
            group_id = request.POST.get('group_id')
            try:
                group = Group.objects.get(id=group_id)
                user.groups.add(group)
                messages.success(request, f"Пользователь {user.username} добавлен в группу {group.name}.")
            except Group.DoesNotExist:
                messages.error(request, "Группа не найдена.")
        elif action == 'remove_from_group':
            group_id = request.POST.get('group_id')
            try:
                group = Group.objects.get(id=group_id)
                user.groups.remove(group)
                messages.success(request, f"Пользователь {user.username} удалён из группы {group.name}.")
            except Group.DoesNotExist:
                messages.error(request, "Группа не найдена.")

        return redirect('account:manage_users')


class VerifyEmailView(View):
    def get(self, request, token):
        try:
            verification = EmailVerification.objects.get(token=token)
            user = verification.user
            user.email_verified = True
            user.is_active = True
            user.save()
            verification.delete()
            login(request, user)
            log.info(f'Пользователь {user.username} подтвердил свой E-mail.')
            return redirect('shop:main')
        except EmailVerification.DoesNotExist:
            log.warning(f'Ошибка подтверждения E-mail: неверный токен.')
            return render(request, 'account/email/verification_failed.html')


class PasswordRecoveryView(View):
    def get(self, request):
        return render(request, 'account/password_recovery.html')

    def post(self, request):
        username_or_email = request.POST.get('username_or_email')

        try:
            user = (CustomUser.objects.filter(username=username_or_email).first() or
                    CustomUser.objects.filter(email=username_or_email).first()
                    )

            if user:
                new_password = PasswordGenerator.generate_random_password(length=8)
                user.set_password(new_password)
                user.save()

                EmailService.send_new_password(user, new_password)
                log.info(f"Пользователь {user.username} сменил пароль")
            else:
                log.info(f"Пользователь {user.username} не найден.")

        except Exception as e:
            log.info(f"Произошла ошибка: {str(e)}")

        return redirect("account:login")


class ManageSubscriptionView(LoginRequiredMixin, View):
    template_name = 'account/subscription.html'

    def get(self, request):
        # Получение информации о подписке текущего пользователя
        subscription, created = UserSubscription.objects.get_or_create(user=request.user)
        return render(request, self.template_name, {'subscription': subscription})

    def post(self, request):
        # Переключение состояния подписки
        subscription, created = UserSubscription.objects.get_or_create(user=request.user)
        subscription.is_subscribed = not subscription.is_subscribed
        subscription.save()
        return redirect('account:manage_subscription')


class ResendEmailConfirmationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.email_verified:
            EmailService.send_verification_email(request, user)
            messages.success(request, "Письмо с подтверждением отправлено повторно.")
        return redirect('account:profile')
