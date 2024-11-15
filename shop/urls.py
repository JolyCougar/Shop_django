from django.urls import path
from .views import ProductListView, ProductDetailView, AddToCartView, CartView, OrdersListView, OrderDetailView

app_name = 'shop'

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("<int:pk>", ProductDetailView.as_view(), name="product-detail"),
    path('add-to-cart/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path('orders/', OrdersListView.as_view(), name='orders_user'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order_detail')

]
