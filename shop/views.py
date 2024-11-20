import logging
from decimal import Decimal
from itertools import product
from unicodedata import decimal

from .models import Product, Order, Cart, CartItem
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View

log = logging.getLogger(__name__)


class ProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    queryset = Product.objects.filter(archived=False)


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

        return redirect('shop:cart_view')


class CartView(ListView):
    model = Cart
    template_name = "shop/cart.html"
    context_object_name = "cart"

    def get_queryset(self):
        return get_object_or_404(Cart, user=self.request.user)


class OrdersListView(ListView):
    model = Order
    template_name = "shop/orders_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(DetailView):
    model = Order
    template_name = "shop/order_detail.html"
