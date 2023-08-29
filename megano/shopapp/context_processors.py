from .models import Category
from .utils.banners import get_random_active_product_banners


def categories_menu(request):
    active_categories = Category.objects.filter(active=True, products__active=True).order_by('sorting_index')
    return {'categories_menu': active_categories}


def random_product_banners(request):
    # Получаем случайные активные продукты для баннеров
    random_banners = get_random_active_product_banners()

    # Добавляем продукты в контекст
    context = {
        'random_banners': random_banners,
    }

    return context

