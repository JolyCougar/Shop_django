from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
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
    template_name = 'account/change_info.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('account:profile', kwargs={'pk': self.request.user.pk})