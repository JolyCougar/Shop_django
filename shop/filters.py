import django_filters
from .models import Product, Category, Manufacturer


class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="discounted_price", lookup_expr='gte', label="Цена от")
    price_max = django_filters.NumberFilter(field_name="discounted_price", lookup_expr='lte', label="Цена до")
    manufacturer = django_filters.ModelChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label="Производитель"
    )

    discounted = django_filters.BooleanFilter(
        field_name="discounted",
        label="Только со скидкой",
    )

    class Meta:
        model = Product
        fields = ['price_min', 'price_max', 'manufacturer', 'category', 'discounted']
