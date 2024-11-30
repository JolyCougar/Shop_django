"""
URL configuration for shopSite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.flatpages import views as flatpage_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('account/', include('account.urls')),
    path('about-us/', flatpage_views.flatpage, {'url': '/about-us/'}, name='about'),
    path('contact/', flatpage_views.flatpage, {'url': '/contact/'}, name='contact'),
    path('delivery/', flatpage_views.flatpage, {'url': '/delivery/'}, name='delivery'),
    path('warranty/', flatpage_views.flatpage, {'url': '/warranty/'}, name='warranty'),
    path('trade_in/', flatpage_views.flatpage, {'url': '/trade_in/'}, name='trade_in'),
]

if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
