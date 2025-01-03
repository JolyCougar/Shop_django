from django.urls import path
from .views import (RegisterView, CustomLoginView, CustomLogoutView,
                    ProfileView, CustomPasswordChangeView, ChangeProfileInfoView,
                    ClearAvatarView, ManageUsersView, VerifyEmailView,
                    PasswordRecoveryView, ManageSubscriptionView, ResendEmailConfirmationView)

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
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('password-recovery/', PasswordRecoveryView.as_view(), name='password_recovery'),
    path('subscription/', ManageSubscriptionView.as_view(), name='manage_subscription'),
    path('resend-email-confirmation/', ResendEmailConfirmationView.as_view(), name='resend_email_confirmation'),

]
