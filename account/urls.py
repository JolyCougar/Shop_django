from django.urls import path
from .views import (RegisterView, CustomLoginView, CustomLogoutView,
                    ProfileView, CustomPasswordChangeView, ChangeProfileInfoView,
                    ClearAvatarView)

app_name = 'account'

urlpatterns = [
    path("register/", RegisterView.as_view(), name="registration"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path('profile/<int:pk>/', ProfileView.as_view(), name="profile"),
    path("profile/change_password", CustomPasswordChangeView.as_view(), name="change-password"),
    path("profile/update/", ChangeProfileInfoView.as_view(), name="update-profile"),
    path('clear-avatar/', ClearAvatarView.as_view(), name='clear_avatar'),
]
