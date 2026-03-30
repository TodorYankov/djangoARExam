# orders/tests.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
import json
from products.models import Product, Category
from orders.models import Order, OrderItem
from orders.forms import OrderForm, OrderStatusForm

User = get_user_model()


# ========== ТЕСТОВЕ ЗА МОДЕЛИ ==========
class OrderModelTests(TestCase):
    """Тестове за модел Order"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.order = Order.objects.create(
            user=self.user,
            status='pending'
        )

    def test_order_creation(self):
        """Тест за създаване на поръчка"""
        self.assertEqual(self.order.user.username, 'testuser')
        self.assertEqual(self.order.status, 'pending')

    def test_order_str_method(self):
        """Тест за __str__ метода"""
        order_str = str(self.order)
        self.assertTrue('Order' in order_str or str(self.order.id) in order_str)
        self.assertTrue(len(order_str) > 0)

    def test_order_status_choices(self):
        """Тест за валидност на статусите"""
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        self.assertIn(self.order.status, valid_statuses)


class OrderItemModelTests(TestCase):
    """Тестове за модел OrderItem"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description',
            price=100.00,
            category=self.category,
            product_type=Product.LAPTOP,
            stock_quantity=10,
            is_available=True
        )
        self.order = Order.objects.create(
            user=self.user
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price_at_time=100.00
        )

    def test_order_item_creation(self):
        """Тест за създаване на артикул в поръчка"""
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price_at_time, 100.00)

    def test_order_item_total(self):
        """Тест за изчисляване на общата цена"""
        expected_total = self.order_item.quantity * self.order_item.price_at_time
        self.assertEqual(expected_total, 200.00)


# ========== ТЕСТОВЕ ЗА ФОРМИ ==========
class OrderFormTests(TestCase):
    """Тестове за форма OrderForm"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_form_exists(self):
        """Тест че формата може да се инстанцира"""
        form = OrderForm()
        self.assertIsNotNone(form)


class OrderStatusFormTests(TestCase):
    """Тестове за форма OrderStatusForm"""

    def test_valid_status_form(self):
        """Тест за валидна форма за статус"""
        form_data = {'status': 'delivered'}
        form = OrderStatusForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_status_form(self):
        """Тест за невалидна форма за статус"""
        form_data = {'status': 'invalid_status'}
        form = OrderStatusForm(data=form_data)
        self.assertFalse(form.is_valid())


# ========== ТЕСТОВЕ ЗА КОЛИЧКАТА (CART) ==========
class CartViewsTests(TestCase):
    """Тестове за изгледите на количката"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

        self.category = Category.objects.create(
            name='Test Category'
        )

        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description for cart',
            price=100.00,
            category=self.category,
            product_type=Product.LAPTOP,
            stock_quantity=10,
            is_available=True
        )

        self.product.refresh_from_db()

    def test_cart_view_url_exists(self):
        """Тест: URL /orders/cart/ съществува"""
        response = self.client.get('/orders/cart/')
        self.assertEqual(response.status_code, 200)

    def test_cart_view_uses_correct_template(self):
        """Тест: Използва се правилният шаблон"""
        response = self.client.get(reverse('orders:cart'))
        self.assertTemplateUsed(response, 'orders/cart.html')

    def test_empty_cart_message(self):
        """Тест: Съобщение при празна количка"""
        response = self.client.get(reverse('orders:cart'))
        self.assertContains(response, 'Вашата количка е празна')

    def test_add_to_cart(self):
        """Тест: Добавяне на продукт в количката"""
        response = self.client.post(
            reverse('orders:add_to_cart', args=[self.product.id]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        cart = session.get('cart', [])
        self.assertEqual(len(cart), 1)
        self.assertEqual(cart[0]['product_id'], self.product.id)
        self.assertEqual(cart[0]['quantity'], 1)

    def test_add_to_cart_multiple_times(self):
        """Тест: Добавяне на същия продукт няколко пъти"""
        self.client.post(reverse('orders:add_to_cart', args=[self.product.id]))
        self.client.post(reverse('orders:add_to_cart', args=[self.product.id]))

        session = self.client.session
        cart = session.get('cart', [])
        self.assertEqual(len(cart), 1)
        self.assertEqual(cart[0]['quantity'], 2)

    def test_cart_with_items_display(self):
        """Тест: Показване на продукти в количката"""
        self.client.post(reverse('orders:add_to_cart', args=[self.product.id]))

        response = self.client.get(reverse('orders:cart'))

        self.assertContains(response, 'Test Product')
        self.assertContains(response, '100,00 €')


# ========== ТЕСТОВЕ ЗА API ENDPOINTS ==========
class CartAPITests(TestCase):
    """Тестове за API endpoints на количката"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

        self.category = Category.objects.create(
            name='Test Category'
        )

        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description for API',
            price=100.00,
            category=self.category,
            product_type=Product.LAPTOP,
            stock_quantity=10,
            is_available=True
        )

        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_cart_api_get_empty_cart(self):
        """Тест: GET /api/cart/ - празна количка"""
        response = self.client.get(reverse('orders:cart_api'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['cart_count'], 0)
        self.assertEqual(data['total'], 0)

    def test_cart_api_get_with_items(self):
        """Тест: GET /api/cart/ - количка с продукти"""
        session = self.client.session
        session['cart'] = [{
            'product_id': self.product.id,
            'name': self.product.name,
            'price': float(self.product.price),
            'quantity': 2,
            'image': None
        }]
        session.save()

        response = self.client.get(reverse('orders:cart_api'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['cart_count'], 2)
        self.assertEqual(data['total'], 200.00)

    def test_cart_api_add_product(self):
        """Тест: POST /api/cart/ - добавяне на продукт"""
        response = self.client.post(
            reverse('orders:cart_api'),
            data=json.dumps({
                'action': 'add',
                'product_id': self.product.id,
                'quantity': 1
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 1)
        self.assertEqual(data['total'], 100.00)


# ========== DRF ТЕСТОВЕ ==========
class CartDRFTests(APITestCase):
    """Тестове за DRF API с APITestCase"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='apitestuser',
            password='testpass123',
            email='api@example.com'
        )
        self.client.login(username='apitestuser', password='testpass123')

        self.category = Category.objects.create(name='API Category')
        self.product = Product.objects.create(
            name='API Product',
            description='API product description',
            price=100.00,
            category=self.category,
            product_type=Product.LAPTOP,
            stock_quantity=10,
            is_available=True
        )

    def test_cart_api_add_product_with_drf_client(self):
        response = self.client.post(
            reverse('orders:cart_api'),
            {
                'action': 'add',
                'product_id': self.product.id,
                'quantity': 1
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()  # защото view връща JsonResponse, не DRF Response
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 1)


# ========== ТЕСТОВЕ ЗА URL КОНФИГУРАЦИИ ==========
class OrdersURLTests(TestCase):
    """Тестове за URL конфигурациите"""

    def test_order_list_url(self):
        """Тест за URL на списъка с поръчки"""
        response = self.client.get('/orders/')
        self.assertIn(response.status_code, [200, 302])

    def test_cart_url(self):
        """Тест за URL на количката"""
        response = self.client.get('/orders/cart/')
        self.assertIn(response.status_code, [200, 302])
