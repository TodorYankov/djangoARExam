# accounts/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import CustomUser
from accounts.forms import CustomUserCreationForm, CustomUserChangeForm
from products.models import Product, Category

User = get_user_model()


# ========== ТЕСТОВЕ ЗА МОДЕЛА CustomUser ==========

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Лаптопи')
        self.product = Product.objects.create(
            name='HP Pavilion',
            price=1200,
            stock_quantity=10,
            category=self.category
        )

    def test_user_creation(self):
        """Тест за създаване на потребител"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_str_method(self):
        """Тест за текстово представяне на потребителя"""
        self.assertEqual(str(self.user), f"{self.user.username} ({self.user.email})")

    def test_user_loyalty_points_default(self):
        """Тест за начални точки за лоялност"""
        self.assertEqual(self.user.loyalty_points, 0)

    def test_add_loyalty_points(self):
        """Тест за добавяне на точки за лоялност"""
        self.user.add_loyalty_points(100)
        self.assertEqual(self.user.loyalty_points, 100)

    def test_use_loyalty_points(self):
        """Тест за използване на точки за лоялност"""
        self.user.loyalty_points = 200
        self.user.save()
        self.user.use_loyalty_points(50)
        self.assertEqual(self.user.loyalty_points, 150)

    def test_use_too_many_points(self):
        """Тест за опит за използване на повече точки от наличните"""
        self.user.loyalty_points = 50
        self.user.save()
        result = self.user.use_loyalty_points(100)
        self.assertFalse(result)
        self.assertEqual(self.user.loyalty_points, 50)

    def test_add_to_favourites(self):
        """Тест за добавяне на продукт към любими"""
        self.user.add_to_favourites(self.product)
        self.assertIn(self.product, self.user.favourites.all())

    def test_remove_from_favourites(self):
        """Тест за премахване на продукт от любими"""
        self.user.add_to_favourites(self.product)
        self.user.remove_from_favourites(self.product)
        self.assertNotIn(self.product, self.user.favourites.all())

    def test_is_favourite(self):
        """Тест за проверка дали продукт е в любими"""
        self.user.add_to_favourites(self.product)
        self.assertTrue(self.user.is_favourite(self.product))

    def test_has_complete_profile(self):
        """Тест за проверка на попълненост на профила"""
        self.assertFalse(self.user.has_complete_profile)
        self.user.first_name = 'Test'
        self.user.last_name = 'User'
        self.user.phone_number = '0888123456'
        self.user.address = 'Sofia'
        self.user.date_of_birth = '1990-01-01'
        self.user.save()
        self.assertTrue(self.user.has_complete_profile)

    def test_profile_picture_url_default(self):
        """Тест за URL на профилна снимка по подразбиране"""
        self.assertEqual(self.user.profile_picture_url, '/static/images/default-avatar.png')


# ========== ТЕСТОВЕ ЗА ФОРМИТЕ ==========

class CustomUserCreationFormTest(TestCase):
    def test_valid_registration_form(self):
        """Тест за валидна форма за регистрация"""
        form_data = {
            'username': 'newuser123',
            'email': 'new@example.com',
            'confirm_email': 'new@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '0888 123 456',
            'address': 'Sofia, Bulgaria',
            'date_of_birth': '1990-01-01',
        }
        form = CustomUserCreationForm(data=form_data)

        # За дебъг - виж какви грешки има
        if not form.is_valid():
            print("Form errors:", form.errors)
            print("Form fields:", form.fields.keys())

        self.assertTrue(form.is_valid())

    def test_invalid_registration_form_passwords_dont_match(self):
        """Тест за невалидна форма - паролите не съвпадат"""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'pass123',
            'password2': 'pass456'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_invalid_registration_form_missing_username(self):
        """Тест за невалидна форма - липсващо потребителско име"""
        form_data = {
            'email': 'new@example.com',
            'password1': 'pass123',
            'password2': 'pass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


# ========== ТЕСТОВЕ ЗА ИЗГЛЕДИТЕ ==========

class AccountsViewsTest(TestCase):
    def setUp(self):
        """Настройка преди всеки тест"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_profile_view_status_code(self):
        """Тест за статус код на профил страницата"""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_view_template(self):
        """Тест за шаблон на профил страницата"""
        response = self.client.get(reverse('accounts:profile'))
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_dashboard_view_status_code(self):
        """Тест за статус код на dashboard страницата"""
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view_template(self):
        """Тест за шаблон на dashboard страницата"""
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertTemplateUsed(response, 'accounts/dashboard.html')

    def test_register_view_status_code(self):
        """Тест за статус код на страницата за регистрация"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_status_code(self):
        """Тест за статус код на страницата за вход"""
        self.client.logout()  # ← добавете този ред
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_favourites_view_status_code(self):
        """Тест за статус код на страницата с любими продукти"""
        response = self.client.get(reverse('accounts:favourites'))
        self.assertEqual(response.status_code, 200)

    def test_favourites_view_template(self):
        """Тест за шаблон на страницата с любими продукти"""
        response = self.client.get(reverse('accounts:favourites'))
        self.assertTemplateUsed(response, 'accounts/favourites.html')

    def test_profile_edit_view_status_code(self):
        """Тест за статус код на страницата за редактиране на профил"""
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 200)

    def test_password_change_view_status_code(self):
        """Тест за статус код на страницата за смяна на парола"""
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_redirect_to_login(self):
        """Тест за пренасочване на неавтентикиран потребител"""
        self.client.logout()
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:profile')}")

    def test_toggle_favourite_view(self):
        """Тест за добавяне/премахване на продукт от любими"""
        category = Category.objects.create(name='Лаптопи')
        product = Product.objects.create(
            name='Test Laptop',
            price=1000,
            stock_quantity=5,
            category=category
        )
        # Добавяне в любими
        response = self.client.get(reverse('accounts:toggle_favourite', args=[product.id]))
        self.assertRedirects(response, reverse('products:product_detail', args=[product.id]))
        self.assertIn(product, self.user.favourites.all())

        # Премахване от любими
        response = self.client.get(reverse('accounts:toggle_favourite', args=[product.id]))
        self.assertRedirects(response, reverse('products:product_detail', args=[product.id]))
        self.assertNotIn(product, self.user.favourites.all())

