from django.test import TestCase
from django.contrib.auth import get_user_model
from shopapp.models import Product, Category, ProductSeller, Seller
from histviewapp.models import HistoryViewed
from histviewapp.services.history import HistoryService


# Create your tests here.
class TestHistoryService(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email='testuser@skill.box', password='testpassword')
        category = Category.objects.create(name='testcategory')
        product1 = Product.objects.create(category=category, name='Product 1')
        product2 = Product.objects.create(category=category, name='Product 2')
        seller = Seller.objects.create(user=self.user, name='exampleuser', slug='exampleslug',
                                       delivery_method=True, payment_method='none')
        self.product_seller_1 = ProductSeller.objects.create(seller=seller, product=product1, price=310)
        self.product_seller_2 = ProductSeller.objects.create(seller=seller, product=product2, price=350)

    def test_add_product(self):
        self.assertFalse(HistoryService.is_product_watched(self.user, self.product_seller_1))
        HistoryService.add_product(self.user, self.product_seller_1)
        self.assertTrue(HistoryService.is_product_watched(self.user, self.product_seller_1))

    def test_remove_product(self):
        HistoryService.add_product(self.user, self.product_seller_1)
        HistoryService.remove_product(self.user, self.product_seller_1)
        self.assertFalse(HistoryService.is_product_watched(self.user, self.product_seller_1))

    def test_is_product_watched(self):
        HistoryViewed.objects.create(user=self.user, product=self.product_seller_1)
        self.assertTrue(HistoryService.is_product_watched(self.user, self.product_seller_1))
        self.assertFalse(HistoryService.is_product_watched(self.user, self.product_seller_2))

    def test_get_history(self):
        HistoryService.add_product(self.user, self.product_seller_1)
        HistoryService.add_product(self.user, self.product_seller_2)
        history = HistoryService.get_history(self.user)
        self.assertEqual(len(history), 2)

    def test_get_history_count(self):
        self.assertEqual(HistoryService.get_history_count(self.user), 0)
        HistoryService.add_product(self.user, self.product_seller_1)
        HistoryService.add_product(self.user, self.product_seller_2)
        self.assertEqual(HistoryService.get_history_count(self.user), 2)
