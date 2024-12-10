from django.urls import path
from .views import (RegisterView, CustomLoginView, CustomLogoutView,
                    ProfileView, CustomPasswordChangeView, ChangeProfileInfoView,
                    ClearAvatarView, ManageUsersView, ProductCreateView,
                    ProductUpdateView, ListProductAdminView, ManufactureCreateAdminView,
                    CategoryCreateAdminView)

app_name = 'account'

urlpatterns = [
    path("register/", RegisterView.as_view(), name="registration"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path('profile/<int:pk>/', ProfileView.as_view(), name="profile"),
    path("profile/change_password", CustomPasswordChangeView.as_view(), name="change-password"),
    path("profile/update/", ChangeProfileInfoView.as_view(), name="update-profile"),
    path('clear-avatar/', ClearAvatarView.as_view(), name='clear_avatar'),
    path('profile/manage-users/', ManageUsersView.as_view(), name='manage_users'),
    path('profile/products/', ListProductAdminView.as_view(), name='product_list'),
    path('profile/product/create/', ProductCreateView.as_view(), name='product_create'),
    path('profile/product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('profile/category/create/', CategoryCreateAdminView.as_view(), name='category_create'),
    path('profile/manufacturer/create/', ManufactureCreateAdminView.as_view(), name='manufacturer_create'),
]
