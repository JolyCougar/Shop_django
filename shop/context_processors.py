from django.core.cache import cache
from .models import Category


def categories_context(request):
    """
    Контекстный процессор для добавления всех категорий в контекст шаблонов.
    Кэширует категории на 1 час для оптимизации производительности.
    """
    categories = cache.get('categories')

    if categories is None:
        categories = Category.objects.all()
        cache.set('categories', categories, 3600)

    return {'categories': categories}
