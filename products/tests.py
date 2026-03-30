# products/tests.py
from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Category, Product
from decimal import Decimal


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Лаптопи',
            description='Ноутбуци и лаптопи'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Лаптопи')
        self.assertEqual(self.category.description, 'Ноутбуци и лаптопи')

    def test_category_str_method(self):
        self.assertEqual(str(self.category), 'Лаптопи')

    def test_category_product_count(self):
        Product.objects.create(
            name='HP Pavilion',
            price=Decimal('1200.00'),
            stock_quantity=10,
            category=self.category
        )
        Product.objects.create(
            name='Dell XPS',
            price=Decimal('1500.00'),
            stock_quantity=5,
            category=self.category
        )
        self.assertEqual(self.category.products.count(), 2)


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Лаптопи')
        self.product = Product.objects.create(
            name='HP Pavilion',
            description='Мощен лаптоп за ежедневна употреба',
            price=Decimal('1200.00'),
            stock_quantity=10,
            category=self.category,
            product_type=Product.LAPTOP
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'HP Pavilion')
        self.assertEqual(self.product.price, Decimal('1200.00'))
        self.assertEqual(self.product.stock_quantity, 10)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.product_type, Product.LAPTOP)

    def test_product_str_method(self):
        self.assertEqual(str(self.product), 'HP Pavilion')

    def test_product_is_available(self):
        self.assertTrue(self.product.is_available)
        self.product.stock_quantity = 0
        self.product.save()
        self.assertFalse(self.product.is_available)

    def test_product_price_validation(self):
        product = Product(
            name='Invalid',
            price=Decimal('-100.00'),
            stock_quantity=5,
            category=self.category
        )
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_average_rating_default(self):
        """Тест за начална стойност на среден рейтинг"""
        self.assertEqual(self.product.average_rating, Decimal('0.00'))
        self.assertEqual(self.product.total_reviews, 0)

    def test_product_update_average_rating(self):
        """Тест за обновяване на среден рейтинг (ще работи след добавяне на reviews)"""
        self.product.update_average_rating()
        self.assertEqual(self.product.average_rating, Decimal('0.00'))
        self.assertEqual(self.product.total_reviews, 0)


class CeleryTaskTest(TestCase):
    """Тестове за Celery задачи"""

    def test_celery_task_exists(self):
        """Проверка дали задачата test_celery съществува"""
        from .tasks import test_celery
        self.assertIsNotNone(test_celery)

    @patch('products.tasks.test_celery.delay')
    def test_celery_task_called(self, mock_delay):
        """Тест за извикване на Celery задача"""
        from .tasks import test_celery
        mock_delay.return_value = None
        test_celery.delay()
        mock_delay.assert_called_once()


class CeleryExecutionTest(TestCase):
    """Тест за реално изпълнение на Celery задача в eager mode"""

    def test_celery_task_executes_and_returns_expected_result(self):
        from .tasks import test_celery

        result = test_celery.delay()
        task_result = result.get()

        self.assertEqual(task_result["status"], "success")
        self.assertEqual(task_result["message"], "Celery is working correctly!")

