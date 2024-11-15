import logging
from .models import Product, Order
from django.views.generic import ListView, DetailView

log = logging.getLogger(__name__)


class ProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    queryset = Product.objects.filter(archived=False)


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"

