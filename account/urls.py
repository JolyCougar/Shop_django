from django.urls import path
from .views import RegisterView, CustomLoginView, CustomLogoutView, ProfileView

app_name = 'account'

urlpatterns = [
    path("register/", RegisterView.as_view(), name="registration"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path('profile/<int:pk>/', ProfileView.as_view(), name="profile")
]
