from django.urls import path
from .views import (ProductListView, ProductDetailView, AddToCartView,
                    CartView, OrdersListView, OrderDetailView, MainPage,
                    CreateOrderView, OrderSuccessView, CartItemDeleteView,
                    PromotionDetailView, ProductByCategoryView, PromotionListView,
                    ProductsNewView, ProductSearchView, ProductCreateView,
                    ProductUpdateView, ListProductAdminView, ManufactureCreateAdminView,
                    CategoryCreateAdminView, MarketingCreateView, MarketingListView,
                    MarketingUpdateView)

app_name = 'shop'

urlpatterns = [
    path("", MainPage.as_view(), name="main"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/new/", ProductsNewView.as_view(), name="products_new"),
    path('category/<slug:category_slug>/', ProductByCategoryView.as_view(), name='category_filter'),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path('add-to-cart/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path('orders/<slug:slug>/', OrdersListView.as_view(), name='orders_user'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order_detail'),
    path('create_order/', CreateOrderView.as_view(), name='create_order'),
    path('order_success/', OrderSuccessView.as_view(), name='order_success'),
    path('cart/remove/<int:pk>/', CartItemDeleteView.as_view(), name='remove_from_cart'),
    path('promotion/', PromotionListView.as_view(), name='promotion_list'),
    path('promotion/<slug:slug>/', PromotionDetailView.as_view(), name='promotion_detail'),
    path('search/', ProductSearchView.as_view(), name='product_search'),
    path('profile/products/', ListProductAdminView.as_view(), name='product_list_admin'),
    path('profile/product/create/', ProductCreateView.as_view(), name='product_create_admin'),
    path('profile/product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update_admin'),
    path('profile/category/create/', CategoryCreateAdminView.as_view(), name='category_create_admin'),
    path('profile/manufacturer/create/', ManufactureCreateAdminView.as_view(), name='manufacturer_create_admin'),
    path('marketings/', MarketingListView.as_view(), name='marketing_list_admin'),
    path('marketing/create/', MarketingCreateView.as_view(), name='marketing_create_admin'),
    path('marketing/<int:pk>/edit/', MarketingUpdateView.as_view(), name='marketing_update_admin'),

]
