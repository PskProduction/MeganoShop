import json

from celery.result import AsyncResult
from django.shortcuts import get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.cache import cache
from django.views.generic import TemplateView

from .models import ProductReview
from django.db.models import Avg
from django.core.paginator import Paginator
from django.contrib import messages

from cart_and_orders.services.cart import CartService
from .forms import AddToCartForm, ProductReviewForm, FileImportForm
from .models import ProductSeller
from .services.discount import DiscountService
from .services.product_review import ProductReviewService
from .utils.details_cache import get_cached_product_by_slug
from .utils.top_products import get_cached_top_products
from .services.recently_viewed import RecentlyViewedService

from django.shortcuts import render, redirect

from django.views import View
from .models import Product, ProductFeature
from .services.compared_products import ComparedProductsService
from django.views.decorators.csrf import csrf_exempt


class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'index.jinja2'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_products'] = get_cached_top_products()
        return context


class ProductDetailView(View):
    """
    Представление для отображения детальной информации о продукте.
    """

    template_name = 'product_detail.jinja2'
    model = Product

    review_service = ProductReviewService()
    discount_service = DiscountService()
    recently_viewed_service = RecentlyViewedService()
    cart = CartService()

    def get(self, request: HttpRequest, product_slug: str) -> HttpResponse:
        """
        Обработчик GET-запроса для отображения детальной информации о продукте.

        :param request: Запрос пользователя.
        :param product_slug: Уникальный идентификатор товара в URL.
        :return: HTTP-ответ с детальной информацией о товаре.
        """

        product = get_cached_product_by_slug(product_slug)

        try:
            product_reviews = self.review_service.get_reviews_for_product(product)
        except ProductReview.DoesNotExist:
            product_reviews = []

        paginator = Paginator(product_reviews, 3)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        extra_images = product.extra_images.all()
        user = request.user
        tags = product.category.tags.all().union(product.tags.all())
        reviews_count = self.review_service.get_reviews_count(product=product)

        product_sellers = product.productseller_set.all()
        average_price = round(ProductSeller.objects.aggregate(avg_price=Avg('price'))['avg_price'], 2)
        # average_price_discount = self.discount_service.calculate_discount_price_product(product)

        if user.is_authenticated:
            self.recently_viewed_service.add_to_recently_viewed(user_id=user.id, product_slug=product_slug)

        features = product.features.all()

        context = {
            'extra_images': extra_images,
            'product': product,
            'product_sellers': product_sellers,
            'average_price': average_price,
            'tags': tags,
            'product_reviews': page_obj,
            'reviews_count': reviews_count,
            'features': features
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, product_slug: str) -> HttpResponse:
        """
        Обработчик POST-запросов для отображения детальной информации о продукте.

        :param request: Запрос пользователя.
        :param product_slug: Уникальный идентификатор товара в URL.
        :return: HTTP-ответ с детальной информацией о товаре.
        """

        product = get_cached_product_by_slug(product_slug)
        user = request.user

        if 'order_quantity' and 'seller_id' in request.POST:
            form = AddToCartForm(request.POST)
            if form.is_valid():
                order_quantity = form.cleaned_data['order_quantity']
                seller_id = request.POST.get('seller_id')
                try:
                    product_seller = ProductSeller.objects.get(id=seller_id)
                    seller_quantity = product_seller.quantity

                    if 0 < order_quantity <= seller_quantity:
                        messages.success(request, 'Товар успешно добавлен в корзину!')
                        # self.cart.add_to_cart()
                    else:
                        messages.error(request, 'Ошибка добавления товара, введите допустимое количество')
                except ProductSeller.DoesNotExist:
                    messages.error(request, 'Продавец не найден')
            else:
                messages.error(request, 'Ошибка добавления товара, введите число')

        elif 'review_text' in request.POST:
            review_form = ProductReviewForm(request.POST)
            if review_form.is_valid():
                review_text = review_form.cleaned_data['review_text']
                self.review_service.add_review_for_product(product=product, user_id=user.id, review_text=review_text)

        return redirect('shopapp:product_detail', product_slug=product_slug)


def catalog_list(request: HttpRequest):
    if not cache.get('top_tags'):  # популярные теги
        top_tags = Product.tags.most_common()[:5]
        cache.set('top_tags', top_tags, 300)
    top_tags = cache.get('top_tags')

    # Фильтрация
    if request.method == 'POST':
        tag = request.POST.get('tag')  # выбранный тег из популярных
        price = request.POST.get('price')
        price_from = price.split(';')[0]  # цена от
        price_to = price.split(';')[1]  # цена до
        title = request.POST.get('title')  # название товара
        available = request.POST.get('available')  # товар в наличии
        free_delivery = request.POST.get('free_delivery')  # бесплатная доставка
        category = request.POST.get('category')

        qs = ProductSeller.objects.select_related('product').filter(price__range=(price_from, price_to))

        if qs:
            if title:
                qs = qs.filter(product__name__icontains=title)  # фильтр по вхождению строки в название товара
            if available:
                qs = qs.filter(quantity__gt=0)  # фильтр по наличию товара
            if free_delivery:
                qs = qs.filter(free_delivery=True)  # фильтр по бесплатной доставке
            if tag:
                qs = qs.filter(product__tags__name=tag)  # фильтр по популярным тегам
            if category:
                qs = qs.filter(product__category__name=category)
            cache.set('qs', qs, 300)
        else:
            qs = []
            cache.set('qs', qs, 300)

    qs = cache.get('qs')

    if request.method == 'GET':
        # Сортировка
        if request.GET.get('sort') and qs:
            sort_param = request.GET.get('sort')
            # eval() преобразует строку в переменную
            if not sort_param.endswith('price'):
                if '-' in sort_param:
                    qs = sorted(qs, key=lambda a: eval('a.product.' + f'{sort_param[1:]}'), reverse=True)
                else:
                    qs = sorted(qs, key=lambda a: eval('a.product.' + f'{sort_param}'))
            else:
                if '-' in sort_param:
                    qs = sorted(qs, key=lambda a: eval('a.' + f'{sort_param[1:]}'), reverse=True)
                else:
                    qs = sorted(qs, key=lambda a: eval('a.' + f'{sort_param}'))
            #cache.set('qs', qs, 300)
        else:
            qs = ProductSeller.objects.select_related('product').all()
        cache.set('qs', qs, 300)

    # Пагинация
    if qs:
        # qs = cache.get('qs')
        paginator = Paginator(qs, 4)  # Show 4 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'dealers': page_obj,
            'top_tags': top_tags,
        }
    else:
        context = {
            'dealers': [],
            'top_tags': top_tags,
        }

    return render(request, 'catalog.jinja2', context=context)


class AddToComparison(View):
    """
    добавить товар в список сравниваемых товаров
    """

    def get(self, request, **kwargs):
        compare_list = ComparedProductsService(request)
        compare_list.add_to_compared_products(kwargs['product_id'])
        return redirect(request.META.get('HTTP_REFERER'))


class RemoveFromComparison(View):
    """
    удалить товар из списка сравниваемых товаров
    """

    def get(self, request, **kwargs):
        compare_list = ComparedProductsService(request)
        compare_list.remove_from_compared_products(kwargs['product_id'])
        return redirect('shopapp:compare_list')


class ComparisonOfProducts(View):
    """
    вывести список сравниваемых товаров
    """
    temlate_name = 'shopapp/comparison.jinja2'

    def get(self, request):
        compare_list = ComparedProductsService(request)
        compare_list = compare_list.get_compared_products()
        compared_products = [get_object_or_404(ProductSeller, id=product_id) for product_id in compare_list]
        only_differences = request.GET.get('only_differences')
        context = {}
        products = []
        features_values_list = []

        # Если товары в списке сранения не из одной категории, выводится философское сообщение на тему попытки
        # сравнить то, что сравнить нельзя и сравнивается только цена.
        if not all([product.product.category == compared_products[0].product.category for product in compared_products]):
            context['message'] = ('Все сравниваемые товары должны быть из одной категории, в противном случае '
                                  'сравнивается только цена.')
            for product in compared_products:
                price = product.price
                seller = product.seller
                products.append({'product': product.product, 'price': price, 'seller': seller, 'id': product.id})
            context['products'] = products
            return render(request, self.temlate_name,  context)

        for product in compared_products:
            features = product.product.features.all()
            [features_values_list.append(feature.value) for feature in features]
            price = product.price
            seller = product.seller
            products.append({'product': product.product, 'features': features, 'price': price, 'seller': seller, 'id': product.id})

        if only_differences:
            products.clear()
            context['only_differences'] = only_differences
            matching_features_list = set(list(filter(
                lambda x: features_values_list.count(x) == compare_list.__len__(), features_values_list
            )))
            for product in compared_products:
                features = product.product.features.exclude(value__in=matching_features_list)
                price = product.price
                seller = product.seller
                products.append({'product': product.product, 'features': features, 'price': price, 'seller': seller, 'id': product.id})

        context['products'] = products

        return render(request, self.temlate_name, context)


class ClearComparison(View):
    """
    Очистить список сравнения
    """

    def get(self, request):
        compare_list = ComparedProductsService(request)
        compare_list.clear()
        return redirect('shopapp:compare_list')


from .tasks import bar, import_json


def test_celery(request):
    # active_task =
    res = bar.delay()
    return HttpResponse(f'<h1>Test celery</h1>'
                        f'<h1>{res.id}</h1>')


def start_import_json(request):
    if request.method == 'GET':
        form = FileImportForm()
        context = {'form': form, 'header': 'Upload from JSON file'}
        return render(request, 'admin_settings/upload_file_form.html', context)
    form = FileImportForm(request.POST, request.FILES)
    if not form.is_valid():
        context = {'form': form, 'header': 'Upload from JSON file'}
        return render(request, 'admin_settings/upload_file_form.html', context, status=400)

    products_from_json = json.load(form.files['file'])
    email = request.POST.get('email')
    print(products_from_json)
    print(email)
    # task = import_json.delay()
    #
    #     for product in products_from_json:
    #         ProductSeller.objects.create(
    #             prduct=Product.objects.get(id=product['product']),
    #             seller=Seller.objects.get(id=product['seller']),
    #             price=product['price'],
    #             quantity=product['quantity'],
    #         )
    #
    # return JsonResponse({"task_id": task.id}, status=202)
    return redirect(request.META.get('HTTP_REFERER'))


# @csrf_exempt
def run_task(request):
    if request.POST:
        task_type = request.POST.get("type")
        print(task_type)
        task = import_json.delay(int(task_type))
        return JsonResponse({"task_id": task.id}, status=202)


# @csrf_exempt
def get_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JsonResponse(result, status=200)
