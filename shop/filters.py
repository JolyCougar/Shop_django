import django_filters
from .models import Product, Manufacturer


class ProductFilter(django_filters.FilterSet):
    # Фильтр по цене (диапазон)
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Цена от')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Цена до')

    # Фильтр по бренду
    manufacturer = django_filters.ModelChoiceFilter(
        queryset=Manufacturer.objects.all(),
        field_name='manufacturer',
        label='Бренд',
    )

    # Фильтр по категории
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains', label='Категория')

    # Фильтр по скидке
    discounted = django_filters.BooleanFilter(method='filter_discounted', label='Со скидкой')

    def filter_discounted(self, queryset, name, value):
        if value:  # Если фильтр включён
            return queryset.filter(discount__gt=0)
        return queryset

    class Meta:
        model = Product
        fields = ['price', 'manufacturer', 'category', 'discounted']
