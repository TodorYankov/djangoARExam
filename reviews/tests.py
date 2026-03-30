# reviews/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from products.models import Category, Product
from .models import Review, ReviewVote
from decimal import Decimal

User = get_user_model()


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Лаптопи')
        self.product = Product.objects.create(
            name='HP Pavilion',
            description='Мощен лаптоп',
            price=Decimal('1200.00'),
            stock_quantity=10,
            category=self.category
        )

    def test_review_creation(self):
        """Тест за създаване на отзив"""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title='Отличен продукт!',
            comment='Много съм доволен от покупката.',
            is_approved=True
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.title, 'Отличен продукт!')
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, self.product)
        self.assertTrue(review.is_approved)
        self.assertEqual(str(review), f"{self.user.username} - {self.product.name} - 5★")

    def test_review_rating_validation_min(self):
        """Тест за валидация на минимална оценка"""
        review = Review(
            product=self.product,
            user=self.user,
            rating=0,
            title='Твърде ниска оценка',
            comment='Невалидна оценка'
        )
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_review_rating_validation_max(self):
        """Тест за валидация на максимална оценка"""
        review = Review(
            product=self.product,
            user=self.user,
            rating=6,
            title='Твърде висока оценка',
            comment='Невалидна оценка'
        )
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_review_unique_per_user_product(self):
        """Тест за уникалност на отзив за потребител и продукт"""
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title='Първи отзив',
            comment='Отлично'
        )
        with self.assertRaises(Exception):
            Review.objects.create(
                product=self.product,
                user=self.user,
                rating=4,
                title='Втори отзив',
                comment='Не би трябвало да може'
            )

    def test_review_updates_product_rating(self):
        """Тест за обновяване на средния рейтинг на продукта"""
        # Създаваме първи отзив
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title='Отличен',
            comment='Много добър продукт',
            is_approved=True
        )

        # Създаваме втори отзив от друг потребител
        Review.objects.create(
            product=self.product,
            user=self.user2,
            rating=3,
            title='Среден',
            comment='Средна оценка',
            is_approved=True
        )

        # Обновяваме средния рейтинг на продукта
        self.product.update_average_rating()

        # Средно аритметично от 5 и 3 е 4.0
        self.assertEqual(self.product.average_rating, Decimal('4.00'))
        self.assertEqual(self.product.total_reviews, 2)

    def test_review_requires_rating(self):
        """Тест че оценката е задължителна"""
        review = Review(
            product=self.product,
            user=self.user,
            title='Без оценка',
            comment='Нямам оценка'
        )
        with self.assertRaises(ValidationError):
            review.full_clean()


class ReviewVoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Лаптопи')
        self.product = Product.objects.create(
            name='HP Pavilion',
            price=Decimal('1200.00'),
            stock_quantity=10,
            category=self.category
        )
        self.review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title='Отличен',
            comment='Много добър продукт',
            is_approved=True
        )

    def test_vote_creation(self):
        """Тест за създаване на глас"""
        vote = ReviewVote.objects.create(
            review=self.review,
            user=self.user2,
            is_helpful=True
        )
        self.assertTrue(vote.is_helpful)
        self.assertEqual(vote.review, self.review)
        self.assertEqual(vote.user, self.user2)

    def test_vote_unique_per_user_review(self):
        """Тест за уникалност на глас за потребител и отзив"""
        ReviewVote.objects.create(
            review=self.review,
            user=self.user2,
            is_helpful=True
        )
        with self.assertRaises(Exception):
            ReviewVote.objects.create(
                review=self.review,
                user=self.user2,
                is_helpful=False
            )

    def test_vote_str_method(self):
        """Тест за текстово представяне на гласа"""
        vote = ReviewVote.objects.create(
            review=self.review,
            user=self.user2,
            is_helpful=True
        )
        expected = f"{self.user2.username} - Полезен"
        self.assertEqual(str(vote), expected)

