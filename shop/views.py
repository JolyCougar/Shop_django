import logging
import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django_filters.views import FilterView

from account.models import CustomUser
from account.services import EmailService
from .filters import ProductFilter
from review.forms import ReviewForm
from review.models import Review, Rating, RatingStar
from django.db.models import Avg
from django.db.models.signals import post_save
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.core.exceptions import ValidationError
from .forms import ProductForm, MarketingForm, ManufacturerForm, CategoryForm, ProductImageFormSet, OrderStatusForm, \
    EmailForm
from .models import Product, Order, Cart, CartItem, OrderItem, Marketing, Category, Manufacturer
from .services import PaymentOrder
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView
from django.views.decorators.cache import cache_page

log = logging.getLogger(__name__)

@cache_page(60 * 15)
class MainPage(ListView):
    model = Marketing
    template_name = "shop/main.html"
    context_object_name = "marketing"
    queryset = Marketing.objects.filter(archived=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["popular_products"] = Product.objects.all()[:5]
        return context

@cache_page(60 * 15)
class PromotionListView(ListView):
    model = Marketing
    template_name = "shop/promotion_list.html"
    context_object_name = "promotions"
    queryset = Marketing.objects.filter(archived=False)
    paginate_by = 6

@cache_page(60 * 15)
class PromotionDetailView(DetailView):
    model = Marketing
    template_name = "shop/promotion_detail.html"
    slug_field = "url"
    slug_url_kwarg = "slug"
    context_object_name = "promotion"


class ProductListView(FilterView):
    model = Product
    filterset_class = ProductFilter
    template_name = "shop/product_list.html"
    queryset = Product.objects.filter(archived=False)
    paginate_by = 10


class ProductByCategoryView(FilterView):
    model = Product
    template_name = "shop/product_list.html"
    filterset_class = ProductFilter
    context_object_name = "product_list"
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        category = get_object_or_404(Category, name=category_slug)
        return Product.objects.filter(category=category, archived=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get("category_slug")
        context["selected_category"] = get_object_or_404(Category, name=category_slug)
        return context


class ProductsNewView(FilterView):
    model = Product
    template_name = 'shop/product_list.html'
    filterset_class = ProductFilter
    context_object_name = "product_list"
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.filter(new=True, archived=False)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        avg_rating = Rating.objects.filter(product=self.object).aggregate(Avg('star__value'))['star__value__avg']
        avg_rating = avg_rating if avg_rating is not None else 0

        context['avg_rating'] = avg_rating
        context['reviews'] = Review.objects.filter(product=self.object, parent__isnull=True)
        context['review_form'] = ReviewForm()

        user = self.request.user
        if user.is_authenticated:
            context['user_review'] = Review.objects.filter(product=self.object, author=user).first()
        else:
            context['user_review'] = None

        context['ratings'] = RatingStar.objects.all()

        return context


class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if created:
                cart_item.quantity = 1
            else:
                cart_item.quantity += 1

            cart_item.save()
        else:
            cart = request.session.get('cart', {})
            if not isinstance(cart, dict):
                cart = {}

            if str(product_id) in cart:
                cart[str(product_id)] += 1
            else:
                cart[str(product_id)] = 1
            request.session['cart'] = cart

        return redirect("shop:cart_view")


class UpdateCartView(View):
    def post(self, request, item_id):
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))

            if quantity < 1:
                return JsonResponse({'success': False, 'message': 'Количество не может быть меньше 1.'})

            cart_item = CartItem.objects.get(product_id=item_id, cart__user=request.user)
            cart_item.quantity = quantity
            cart_item.save()

            return JsonResponse({'success': True, 'message': 'Количество обновлено.'})

        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Товар не найден в корзине.'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Некорректное значение количества.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'})


class CartItemDeleteView(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_item = get_object_or_404(CartItem, cart=cart, product__id=product_id)
            cart_item.delete()
        else:
            cart = request.session.get('cart', {})
            if not isinstance(cart, dict):
                cart = {}

            if str(product_id) in cart:
                del cart[str(product_id)]
                request.session['cart'] = cart

        return JsonResponse({"success": True, "message": "Item removed from cart."})


class CartView(ListView):
    template_name = "shop/cart.html"
    context_object_name = "cart_items"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            return cart.cartitem_set.select_related('product')
        else:
            cart = self.request.session.get('cart', {})
            cart_items = []
            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, id=product_id)
                cart_item = CartItem(
                    product=product,
                    quantity=quantity,
                    cart=None
                )
                cart_items.append(cart_item)
            return cart_items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart_items = self.get_queryset()

        total_price = 0
        for item in cart_items:
            item.total_price = item.product.discounted_price * item.quantity
            total_price += item.total_price

        context["cart_items"] = cart_items
        context["total_price"] = total_price

        return context


class CreateOrderView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = "shop/checkout_order.html"
    fields = ["full_name", "city", "delivery_address", "payment_method", "delivery_method"]
    success_url = reverse_lazy("shop:order_success")

    def form_valid(self, form):
        form.instance.user = self.request.user
        cart = get_object_or_404(Cart, user=self.request.user)

        with transaction.atomic():
            order = form.save(commit=False)
            order.save()
            order.total_price = 0

            total_price = 0

            for cart_item in cart.cartitem_set.all():
                product = cart_item.product
                try:
                    if product.stock < cart_item.quantity:
                        log.info(f"Не хватает товара '{product.name}' на складе! "
                                 f"Доступно: {product.stock} шт. Необходимо: {cart_item.quantity}")
                        raise ValidationError(
                            f"Не хватает товара '{product.name}' на складе! Доступно: {product.stock} шт.")
                except ValidationError:
                    return render(self.request, "shop/error_messages.html",
                                  {"message_error": "Такого количества товара нет на складе, "
                                                    "просим извинения за доставленные неудобства."
                                                    f"Уменьшите кол-во товара {product.name} до {product.stock}"})

                product.stock -= cart_item.quantity
                if product.stock == 0:
                    product.archived = True
                product.save()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity
                )

                total_price += product.price * cart_item.quantity

            order.total_price = total_price
            order.save()
            self.request.session['order_id'] = order.id

            cart.cartitem_set.all().delete()
            return_link = self.request.build_absolute_uri(
                reverse('shop:order_success'))

            post_save.send(sender=Order, instance=self.object, created=True, request=self.request)
            log.info("Сделан новый заказ.")
            if order.payment_method == "Онлайн":
                payment_url = PaymentOrder.get_payment_url(order, return_link)
                if payment_url != "":
                    return HttpResponseRedirect(payment_url)
                else:
                    return render(self.request, "shop/error_messages.html",
                                  {"message_error": "Произошла ошибка при создании счета на оплату,"
                                                    "заказ создан,но не оплачен, попробуйте оплатить снова,"
                                                    "В разделе ваших заказов, если возникли проблемы или"
                                                    "эта ошибка все равно происходит, напишите нам"})
            return HttpResponseRedirect(reverse('shop:order_success'))


class OrderSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        order_id = request.session.get('order_id')
        order = Order.objects.prefetch_related('items__product').get(id=order_id)
        if order.payment_id:
            if PaymentOrder.check_paid_order(order.payment_id):
                order.paid = True
                order.save()
                log.info(f"Заказ #{order_id} оплачен!")
        context = {'order': order}
        return render(request, "shop/order_success.html", context)


class OrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shop/orders_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        filter_slug = self.kwargs.get("slug")
        if filter_slug == "all":
            return Order.objects.filter(canceled=False)
        elif filter_slug == "complete":
            return Order.objects.filter(complete=True, canceled=False)
        elif filter_slug == "canceled":
            return Order.objects.filter(canceled=True)
        else:
            return Order.objects.filter(complete=False, canceled=False)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "shop/order_detail.html"


class ProductSearchView(ListView):
    model = Product
    template_name = 'shop/product_search.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        return Product.objects.filter(name__icontains=query) if query else Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('search', '')
        return context


class ListProductAdminView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = Product
    template_name = 'shop/profile_admin/product_list_admin.html'
    context_object_name = 'products'
    paginate_by = 10

    def test_func(self):
        if self.request.user.groups.filter(name="Модераторы") or self.request.user.is_superuser:
            return True
        return False


class ProductCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/profile_admin/product_form.html'
    success_url = reverse_lazy('account:product_list')

    def test_func(self):
        if self.request.user.groups.filter(name="Модераторы") or self.request.user.is_superuser:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProductImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = ProductImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Товар успешно добавлен.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ProductUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/profile_admin/product_form.html'
    success_url = reverse_lazy('account:product_list')

    def test_func(self):
        if self.request.user.groups.filter(name="Модераторы") or self.request.user.is_superuser:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProductImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['formset'] = ProductImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Товар успешно обновлен.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ManufactureCreateAdminView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = 'shop/profile_admin/manufacturer_form.html'
    success_url = reverse_lazy('account:product_list')

    def test_func(self):
        if self.request.user.groups.filter(name="Модераторы") or self.request.user.is_superuser:
            return True
        return False

    def form_valid(self, form):
        messages.success(self.request, "Производитель успешно добавлен.")
        return super().form_valid(form)


class CategoryCreateAdminView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'shop/profile_admin/category_form.html'
    success_url = reverse_lazy('account:product_list')

    def test_func(self):
        if self.request.user.groups.filter(name="Модераторы") or self.request.user.is_superuser:
            return True
        return False

    def form_valid(self, form):
        messages.success(self.request, "Категория успешно добавлена.")
        return super().form_valid(form)


class MarketingAdminListView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = Marketing
    template_name = 'shop/profile_admin/marketing_list.html'
    context_object_name = 'marketings'
    paginate_by = 10

    def test_func(self):
        if self.request.user.groups.filter(name="Модераторы") or self.request.user.is_superuser:
            return True
        return False


class MarketingAdminCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Marketing
    form_class = MarketingForm
    template_name = 'shop/profile_admin/marketing_form.html'
    success_url = reverse_lazy('shop:marketing_list_admin')

    def test_func(self):
        if self.request.user.groups.filter(name="Модераторы") or self.request.user.is_superuser:
            return True
        return False

    def form_valid(self, form):
        response = super().form_valid(form)
        post_save.send(sender=Marketing, instance=self.object, created=True, request=self.request)
        messages.success(self.request, "Маркетинговая кампания успешно создана.")
        return response


class MarketingAdminUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Marketing
    form_class = MarketingForm
    template_name = 'shop/profile_admin/marketing_form.html'
    success_url = reverse_lazy('shop:marketing_list_admin')

    def test_func(self):
        if self.request.user.groups.filter(name="Модераторы") or self.request.user.is_superuser:
            return True
        return False

    def form_valid(self, form):
        messages.success(self.request, "Маркетинговая кампания успешно обновлена.")
        return super().form_valid(form)


class OrdersAdminListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shop/profile_admin/orders_list_admin.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(complete=False).all()


class OrdersUpdateAdminListView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderStatusForm
    template_name = "shop/profile_admin/order_update_status.html"
    success_url = reverse_lazy('shop:orders_list_admin')

    def test_func(self):
        if self.request.user.groups.filter(name="Модераторы") or self.request.user.is_superuser:
            return True
        return False

    def form_valid(self, form):
        order = self.get_object()
        order.status = form.cleaned_data.get('status', order.status)
        order.complete = form.cleaned_data.get('complete', order.complete)
        order.save()
        post_save.send(sender=Order, instance=self.object, created=False,
                       request=self.request, order_pk=order.pk, order_status=order.status,
                       username_send=order.user.username, user_email_send=order.user.email)
        return super().form_valid(form)


class SendMailUserFromAdmin(UserPassesTestMixin, LoginRequiredMixin, View):

    def test_func(self):
        if self.request.user.groups.filter(name="Модераторы") or self.request.user.is_superuser:
            return True
        return False

    def get(self, request):
        form = EmailForm()
        users = CustomUser.objects.all()
        return render(request, 'shop/profile_admin/send_message_to_user.html', {'form': form, 'users': users})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            user = CustomUser.objects.get(email=recipient)
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            EmailService.send_email_from_admin(subject, message, user)
            messages.success(request, "Письмо успешно отправленно!")
            return redirect('shop:send_email_admin')


class RepaymentOrder(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        return_link = self.request.build_absolute_uri(
            reverse('shop:repay_order_success', args=[pk]))
        pay_link = PaymentOrder.get_payment_url(order, return_link)
        if pay_link:
            return HttpResponseRedirect(pay_link)
        else:
            return render(self.request, "shop/error_messages.html",
                          {"message_error": "Произошла ошибка при создании счета на оплату,"
                                            "заказ создан,но не оплачен, попробуйте оплатить снова,"
                                            "В разделе ваших заказов, если возникли проблемы или"
                                            "эта ошибка все равно происходит, напишите нам"}
                          )


class PaySuccessView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        if order.payment_id:
            if PaymentOrder.check_paid_order(order.payment_id):
                order.paid = True
                order.save()
                log.info(f"Заказ #{pk} оплачен!")
                context = {'order': order}
                return render(request, "shop/payment_success.html", context)
            else:
                return render(request, "shop/error_messages.html",
                              {"message_error": "Произошла ошибка при создании счета на оплату,"
                                                "заказ создан,но не оплачен, попробуйте оплатить снова,"
                                                "В разделе ваших заказов, если возникли проблемы или"
                                                "эта ошибка все равно происходит, напишите нам"}
                              )

class CanceledOrder(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        if order.status == "В обработке" and order.paid == False:
            order.canceled = True
            order.save()
            messages.info(request,f"Заказ # {pk} успешно отменен.")
            return HttpResponseRedirect(reverse('shop:orders_user', args=["active"]))
        else:
            return render(request, "shop/error_messages.html",
                          {"message_error": "Ошибка! Вы не можете отменить заказ если "
                                            "он не находится в статусе: В обработке и оплачен "
                                            "Для отмены заказа свяжитесь с администрацией!"}
                          )

