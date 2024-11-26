from django.urls import path
from .views import (ProductListView, ProductDetailView, AddToCartView,
                    CartView, OrdersListView, OrderDetailView, MainPage,
                    CreateOrderView, OrderSuccessView, CartItemDeleteView)

app_name = 'shop'

urlpatterns = [
    path("", MainPage.as_view(), name="main"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path('add-to-cart/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path('orders/', OrdersListView.as_view(), name='orders_user'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order_detail'),
    path('create_order/', CreateOrderView.as_view(), name='create_order'),
    path('order_success/', OrderSuccessView.as_view(), name='order_success'),
    path('cart/remove/<int:pk>/', CartItemDeleteView.as_view(), name='remove_from_cart'),

]
