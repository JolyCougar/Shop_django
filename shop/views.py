import logging

from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Product, Order, Cart, CartItem, OrderItem, Marketing, Category
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View, TemplateView, CreateView

log = logging.getLogger(__name__)


class MainPage(ListView):
    model = Marketing
    template_name = "shop/main.html"
    context_object_name = "marketing"

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


class ProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    queryset = Product.objects.filter(archived=False)


class ProductByCategoryView(ListView):
    model = Product
    template_name = "shop/product_list.html"
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


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"


class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect("shop:cart_view")


class CartView(ListView):
    model = Cart
    template_name = "shop/cart.html"
    context_object_name = "cart_items"

    def get_queryset(self):
        # Получаем корзину текущего пользователя
        cart = Cart.objects.get(user=self.request.user)
        return cart.cartitem_set.all()  # Возвращаем все элементы корзины

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.get(user=self.request.user)
        total_price = sum(item.product.price * item.quantity for item in cart.cartitem_set.all())
        context["total_price"] = total_price
        return context


class CreateOrderView(CreateView):
    model = Order
    template_name = "shop/order_form.html"
    fields = ["delivery_address"]
    success_url = reverse_lazy("shopp:order_success")

    def form_valid(self, form):
        # Создаем заказ
        form.instance.user = self.request.user
        cart = Cart.objects.get(user=self.request.user)

        # Сохраняем заказ, чтобы получить его ID
        order = form.save(commit=False)  # Не сохраняем еще в БД
        order.total_price = 0  # Инициализируем общую цену
        order.save()  # Сохраняем заказ

        total_price = 0
        for cart_item in cart.cartitem_set.all():
            OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)
            total_price += cart_item.product.price * cart_item.quantity

        order.total_price = total_price  # Обновляем общую цену заказа
        order.save()  # Сохраняем заказ снова с обновленной ценой

        # Очистка корзины после создания заказа
        cart.cartitem_set.all().delete()

        return super().form_valid(form)


class OrderSuccessView(View):
    def get(self, request):
        return render(request, "shop/order_success.html")


class CartItemDeleteView(View):
    def post(self, request, *args, **kwargs):
        # Получаем корзину пользователя
        cart = get_object_or_404(Cart, user=request.user)
        # Получаем элемент корзины, который нужно удалить
        cart_item = get_object_or_404(CartItem, cart=cart, id=self.kwargs["pk"])

        # Удаляем элемент из корзины
        cart_item.delete()

        # Возвращаем JSON-ответ
        return JsonResponse({"success": True, "message": "Item removed from cart."})


class OrdersListView(ListView):
    model = Order
    template_name = "shop/orders_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(DetailView):
    model = Order
    template_name = "shop/order_detail.html"
