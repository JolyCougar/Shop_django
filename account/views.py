from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.shortcuts import redirect, render
from django.views.generic import CreateView, DetailView, UpdateView
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from shop.models import Product, Cart, CartItem, Marketing
from .forms import (CustomUserCreationForm, CustomPasswordChangeForm, ProfileUpdateForm,
                    ProductForm, CategoryForm, ManufacturerForm, MarketingForm)
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


class ListProductAdminView(ListView):
    model = Product
    template_name = 'account/product_list_admin.html'
    context_object_name = 'products'


class ProductCreateView(View):
    def get(self, request):
        form = ProductForm()
        return render(request, 'account/product_form.html', {'form': form})

    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар успешно добавлен.")
            return redirect('account:product_list')
        return render(request, 'account/product_form.html', {'form': form})


class ProductUpdateView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)
        return render(request, 'account/product_form.html', {'form': form})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар успешно обновлен.")
            return redirect('account:product_list')
        return render(request, 'account/product_form.html', {'form': form})


class ManufactureCreateAdminView(View):
    def get(self, request):
        form = ManufacturerForm()
        return render(request, 'account/manufacturer_form.html', {'form': form})

    def post(self, request):
        form = ManufacturerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Производитель успешно добавлен.")
            return redirect('account:product_list')
        return render(request, 'account/manufacturer_form.html', {'form': form})


class CategoryCreateAdminView(View):
    def get(self, request):
        form = CategoryForm()
        return render(request, 'account/category_form.html', {'form': form})

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория успешно добавлена.")
            return redirect('account:product_list')
        return render(request, 'account/category_form.html', {'form': form})


class MarketingListView(ListView):
    model = Marketing
    template_name = 'account/marketing_list.html'
    context_object_name = 'marketings'


class MarketingCreateView(CreateView):
    model = Marketing
    form_class = MarketingForm
    template_name = 'account/marketing_form.html'
    success_url = reverse_lazy('marketing_list')

    def form_valid(self, form):
        messages.success(self.request, "Маркетинговая кампания успешно создана.")
        return super().form_valid(form)


class MarketingUpdateView(UpdateView):
    model = Marketing
    form_class = MarketingForm
    template_name = 'account/marketing_form.html'
    success_url = reverse_lazy('marketing_list')

    def form_valid(self, form):
        messages.success(self.request, "Маркетинговая кампания успешно обновлена.")
        return super().form_valid(form)
