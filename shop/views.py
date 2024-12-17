import logging
from django.contrib import messages
from django_filters.views import FilterView
from .filters import ProductFilter
from review.forms import ReviewForm
from review.models import Review
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction
from django.core.exceptions import ValidationError
from .forms import ProductForm, MarketingForm, ManufacturerForm, CategoryForm, ProductImageFormSet
from .models import Product, Order, Cart, CartItem, OrderItem, Marketing, Category, Manufacturer
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView

log = logging.getLogger(__name__)


class MainPage(ListView):
    model = Marketing
    template_name = "shop/main.html"
    context_object_name = "marketing"
    queryset = Marketing.objects.filter(archived=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["popular_products"] = Product.objects.all()[:5]
        return context


class PromotionListView(ListView):
    model = Marketing
    template_name = "shop/promotion_list.html"
    context_object_name = "promotions"
    queryset = Marketing.objects.filter(archived=False)


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


class ProductByCategoryView(FilterView):
    model = Product
    template_name = "shop/product_list.html"
    filterset_class = ProductFilter
    context_object_name = "product_list"

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

    def get_queryset(self):
        return Product.objects.filter(new=True, archived=False)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Получаем все отзывы для этого товара, сортируем по дате (от новых к старым)
        reviews = Review.objects.filter(product=product).order_by('-created_at')
        context['reviews'] = reviews
        context['form'] = ReviewForm()  # Форма для добавления отзыва

        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = ReviewForm(request.POST)

        if form.is_valid():
            # Проверка на дублирующий отзыв
            if Review.objects.filter(author=request.user, product=product).exists():
                return redirect('shop:product-detail', pk=product.pk)

            # Создаем и сохраняем новый отзыв
            review = form.save(commit=False)
            review.product = product
            review.author = request.user  # Присваиваем автором текущего пользователя
            review.save()

            return redirect('shop:product-detail', pk=product.pk)  # Перенаправляем обратно на страницу товара

        # Если форма не валидна, показываем ошибки и возвращаем на ту же страницу
        return redirect('shop:product-detail', pk=product.pk)


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
            item.total_price = item.product.price * item.quantity
            total_price += item.total_price

        context["cart_items"] = cart_items
        context["total_price"] = total_price

        return context


class CreateOrderView(CreateView):
    model = Order
    template_name = "shop/checkout_order.html"
    fields = ["full_name", "city", "delivery_address", "payment_method", "delivery_method"]
    success_url = reverse_lazy("shop:order_success")

    def form_valid(self, form):
        form.instance.user = self.request.user
        cart = get_object_or_404(Cart, user=self.request.user)

        with transaction.atomic():
            order = form.save(commit=False)
            order.total_price = 0
            order.save()

            total_price = 0

            for cart_item in cart.cartitem_set.all():
                product = cart_item.product

                if product.stock < cart_item.quantity:
                    raise ValidationError(
                        f"Не хватает товара '{product.name}' на складе! Доступно: {product.stock} шт.")

                product.stock -= cart_item.quantity
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

        return super().form_valid(form)


class OrderSuccessView(View):
    def get(self, request):
        order_id = request.session.get('order_id')
        order = Order.objects.prefetch_related('items__product').get(id=order_id)
        context = {'order': order}
        return render(request, "shop/order_success.html", context)


class OrdersListView(ListView):
    model = Order
    template_name = "shop/orders_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        filter_slug = self.kwargs.get("slug")
        if filter_slug == "all":
            return Order.objects.all()
        elif filter_slug == "complete":
            return Order.objects.filter(complete=True)
        else:
            return Order.objects.filter(complete=False)


class OrderDetailView(DetailView):
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


class ListProductAdminView(ListView):
    model = Product
    template_name = 'shop/profile_admin/product_list_admin.html'
    context_object_name = 'products'


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/profile_admin/product_form.html'
    success_url = reverse_lazy('account:product_list')

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


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/profile_admin/product_form.html'
    success_url = reverse_lazy('account:product_list')

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


class ManufactureCreateAdminView(CreateView):
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = 'shop/profile_admin/manufacturer_form.html'
    success_url = reverse_lazy('account:product_list')

    def form_valid(self, form):
        messages.success(self.request, "Производитель успешно добавлен.")
        return super().form_valid(form)


class CategoryCreateAdminView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'shop/profile_admin/category_form.html'
    success_url = reverse_lazy('account:product_list')

    def form_valid(self, form):
        messages.success(self.request, "Категория успешно добавлена.")
        return super().form_valid(form)


class MarketingListView(ListView):
    model = Marketing
    template_name = 'shop/profile_admin/marketing_list.html'
    context_object_name = 'marketings'


class MarketingCreateView(CreateView):
    model = Marketing
    form_class = MarketingForm
    template_name = 'shop/profile_admin/marketing_form.html'
    success_url = reverse_lazy('marketing_list')

    def form_valid(self, form):
        messages.success(self.request, "Маркетинговая кампания успешно создана.")
        return super().form_valid(form)


class MarketingUpdateView(UpdateView):
    model = Marketing
    form_class = MarketingForm
    template_name = 'shop/profile_admin/marketing_form.html'
    success_url = reverse_lazy('marketing_list')

    def form_valid(self, form):
        messages.success(self.request, "Маркетинговая кампания успешно обновлена.")
        return super().form_valid(form)
