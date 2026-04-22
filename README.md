# 🛍️ **TechShop**

### An E-Commerce Web Application built with Django | Уеб приложение за електронен магазин

[![Test User](https://img.shields.io/badge/Test_User-testuser/testpass123-green)]
[![GitHub repo](https://img.shields.io/badge/GitHub-TechShop-blue?logo=github)](https://github.com/TodorYankov/djangoARExam)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0.1-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-5.2.1-red.svg)](https://redis.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 **Table of Contents** | **Съдържание**
- [Overview](#-overview--общ-преглед)
- [Live Demo](#-live-demo--демо-на-живо)
- [Features](#-features--функционалности)
- [Technology Stack](#-technology-stack--технологичен-стек)
- [Installation](#-installation--инсталация)
- [Usage](#-usage--употреба)
- [API Endpoints](#-api-endpoints)
- [Testing](#-testing--тестване)
- [Project Structure](#-project-structure--структура-на-проекта)
- [License](#-license--лиценз)

---

## 🔍 **Overview** | **Общ преглед**

### 🇬🇧 English
**TechShop** is an e-commerce web application developed with **Django**. It allows users to browse products, place orders, leave reviews, and manage their purchases while providing an administrative interface for managing products, categories, orders, and reviews.

This project was created as an exam project for the **Django Advanced** course at **SoftUni**.

### 🇧🇬 Български
**TechShop** е уеб приложение за електронен магазин, разработено с **Django**. То позволява на потребителите да разглеждат продукти, да правят поръчки, да оставят отзиви и да управляват покупките си, като същевременно предоставя административен интерфейс за управление на продукти, категории, поръчки и отзиви.

Този проект е създаден като изпитен проект за курса **Django Advanced** в **SoftUni**.

### 🎯 **Key Demonstrations** | **Демонстрирани умения**

| 🇬🇧 English | 🇧🇬 Български |
|------------|--------------|
| Advanced database modeling with PostgreSQL | Разширено моделиране на бази данни с PostgreSQL |
| Asynchronous processing with Celery and Redis | Асинхронна обработка със Celery и Redis |
| RESTful API with JWT authentication | RESTful API с JWT автентикация |
| Customized administrative interface | Персонализиран административен интерфейс |
| User profiles and authentication | Потребителски профили и автентикация |
| Product reviews and ratings | Отзиви и рейтинги за продукти |
| Loyalty points system | Система за точки за лоялност |

---

## 🌐 **Live Demo** | **Демо на живо**

| 🇬🇧 English | 🇧🇬 Български |
|------------|--------------|
| **Current project:** https://web6.site/django/ | **Текущ проект:** https://web6.site/django/ |

---

## ⚙️ **Features** | **Функционалности**

### 👤 **Users & Profiles** | **Потребители и профили**

| 🇬🇧 English | 🇧🇬 Български |
|------------|--------------|
| Registration, login, logout | Регистрация, вход, изход |
| Personal profile with photo, phone, address | Персонален профил със снимка, телефон, адрес |
| Favourite products | Любими продукти |
| Loyalty points system | Система за точки за лоялност |
| Password change | Смяна на парола |
| Three user levels: Customers, Staff, Managers | Три нива на потребители: Customers, Staff, Managers |

### 📦 **Products** | **Продукти**

| 🇬🇧 English | 🇧🇬 Български |
|------------|--------------|
| Categories and product types | Категории и типове продукти |
| Search by name, description, category | Търсене по име, описание, категория |
| Filter by price, availability, type | Филтриране по цена, наличност, тип |
| Sort by price, name, date | Сортиране по цена, име, дата |
| Detailed view with similar products | Детайлен изглед с подобни продукти |
| Full CRUD operations | Пълни CRUD операции |

### 🛒 **Orders** | **Поръчки**

| 🇬🇧 English | 🇧🇬 Български |
|------------|--------------|
| Add to cart functionality | Добавяне в количка |
| Automatic total calculation | Автоматично изчисляване на обща сума |
| Statuses: Pending, Processing, Completed, Cancelled | Статуси: Чакаща, Обработва се, Изпълнена, Отказана |
| Order history | История на поръчките |

### ⭐ **Reviews** | **Отзиви**

| 🇬🇧 English | 🇧🇬 Български |
|------------|--------------|
| Rating from 1 to 5 stars | Оценка от 1 до 5 звезди |
| Comments and titles | Коментари и заглавия |
| Automatic average rating calculation | Автоматично изчисляване на среден рейтинг |
| Helpful votes | Гласуване за полезност |
| Administrative review approval | Административно одобрение на отзиви |

### 🔧 **Admin Interface** | **Административен интерфейс**

| 🇬🇧 English | 🇧🇬 Български |
|------------|--------------|
| Customized Django admin | Персонализиран Django admin |
| Inline editors | Вградени inline редактори |
| Bulk actions | Масови действия |

---

## 🛠️ **Technology Stack** | **Технологичен стек**

| Technology | Version | Технология | Версия |
|------------|---------|------------|-------|
| Django | 6.0.1 | Django | 6.0.1 |
| Django REST Framework | 3.15.2 | Django REST Framework | 3.15.2 |
| Celery | 5.4.0 | Celery | 5.4.0 |
| Redis | 5.2.1 | Redis | 5.2.1 |
| PostgreSQL | 14+ | PostgreSQL | 14+ |
| Bootstrap | 5.3 | Bootstrap | 5.3 |
| Python | 3.12+ | Python | 3.12+ |

---

## 🚀 **Installation** | **Инсталация**

### 📋 **Requirements** | **Изисквания**

| 🇬🇧 English | 🇧🇬 Български |
|------------|--------------|
| Python 3.12 or higher | Python 3.12 или по-висока |
| pip | pip |
| PostgreSQL 14+ | PostgreSQL 14+ |
| Redis (for Celery) | Redis (за Celery) |
| Git | Git |
| Virtual environment (recommended) | Виртуална среда (препоръчително) |

### 📝 **Step-by-Step Installation** | **Инсталация стъпка по стъпка**

#### 1️⃣ **Clone the repository** | **Клониране на хранилището**
```bash
git clone https://github.com/TodorYankov/djangoARExam.git
cd djangoARExam
2️⃣ Create and activate virtual environment | Създаване и активиране на виртуална среда
Windows (bash):

bash
python -m venv .venv
.venv\Scripts\activate
Linux / macOS:

bash
python3 -m venv .venv
source .venv/bin/activate
3️⃣ Install dependencies | Инсталиране на зависимостите
bash
pip install -r requirements.txt
4️⃣ Configure PostgreSQL | Конфигуриране на PostgreSQL
sql
sudo -u postgres psql
CREATE DATABASE djangoARExam;
-- Use existing postgres user or create a new one
GRANT ALL PRIVILEGES ON DATABASE djangoARExam TO postgres;
\q
5️⃣ Environment variables | Променливи на средата
Create .env file in the project root | Създайте файл .env в главната директория:

env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database - PostgreSQL
DB_NAME=djangoARExam
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0
Generate secret key | Генерирайте секретен ключ:

bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
6️⃣ Start Redis (in separate terminal) | Стартиране на Redis (в отделен терминал)
Linux/macOS:

bash
redis-server
Windows (with WSL):

bash
sudo service redis-server start
7️⃣ Apply migrations | Прилагане на миграциите
bash
python manage.py makemigrations
python manage.py migrate
8️⃣ Create superuser | Създаване на суперпотребител
bash
python manage.py createsuperuser
9️⃣ Start Celery worker (in separate terminal) | Стартиране на Celery worker (в отделен терминал)
bash
celery -A djangoARExam worker --loglevel=info
🔟 Start the server | Стартиране на сървъра
bash
python manage.py runserver
Open http://127.0.0.1:8000/ in your browser | Отворете http://127.0.0.1:8000/ в браузъра

📦 Optional: Load sample data | По желание: Зареждане на примерни данни
bash
python manage.py loaddata initial_data.json
📖 Usage | Употреба
🔐 Admin Panel | Административен панел
Go to http://127.0.0.1:8000/admin/ and login with superuser credentials

Manage categories, products, orders, reviews, user groups

Отидете на http://127.0.0.1:8000/admin/ и влезте с данните на суперпотребителя

Управлявайте категории, продукти, поръчки, отзиви, потребителски групи

🌍 User Pages | Потребителски страници
Page	URL	Description	Описание
🏠 Home	/	Featured products and navigation	Представени продукти и навигация
📦 Products	/products/	Product list, search, filters	Списък с продукти, търсене, филтри
🔍 Product Detail	/products/<id>/	Detailed info, add to cart, favourites	Подробна информация, добавяне в количка, любими
🛒 Cart	/orders/cart/	Added products	Добавени продукти
📋 Orders	/orders/	Order history (authenticated users)	История на поръчките (автентикирани потребители)
👤 Profile	/accounts/profile/	Personal information, favourites	Лична информация, любими
📝 Registration	/accounts/register/	Create new account	Създаване на нов акаунт
🔑 Login	/accounts/login/	Sign in	Влизане в системата
🌐 API Endpoints
Method	Endpoint	Description	Описание
GET	/api/products/	List products	Списък с продукти
GET	/api/categories/	List categories	Списък с категории
POST	/api/token/	Obtain JWT token	Получаване на JWT токен
POST	/api/token/refresh/	Refresh JWT token	Обновяване на JWT токен
GET	/api/test-task/	Test Celery task	Тест на Celery задача
🧪 Testing | Тестване
The project includes 67 tests covering models, forms, and views.

Проектът включва 67 теста, покриващи модели, форми и изгледи.

bash
# Run all tests | Стартиране на всички тестове
python manage.py test

# Run tests for specific app | Стартиране на тестовете за конкретно приложение
python manage.py test accounts
python manage.py test products
python manage.py test reviews
Expected output | Очакван резултат:

Ran 67 tests in 94.748s
OK

### ✅ Manual Test Scenario | Ръчен тестов сценарий

You can manually test the complete order flow with a predefined test user:

**Test credentials** | **Тестови данни за вход:**

| Username | Password | Role |
|----------|----------|------|
| testuser | testpass123 | Regular Customer |
| teststaff | staffpass123 | Staff Member |
| testmanager | managerpass123 | Manager |

**Successfully executed test** | **Успешно изпълнен тест:**

1. Log in with `testuser` / `testpass123`
2. Browse products and add **two different products** to the cart
3. Go to cart and proceed to checkout
4. Complete the order

> ✅ **Result** | **Резултат:** Order with two products was successfully created and appears in order history.
> 
> ✅ **Резултат:** Поръчка с два продукта беше успешно създадена и се вижда в историята на поръчките.

### 📦 Sample Data

To load sample products and categories:
```bash
python manage.py loaddata initial_data.json

📁 Project Structure | Структура на проекта
text
djangoARExam/
├── 📁 accounts/          # User profiles, authentication | Потребителски профили, автентикация
├── 📁 core/              # Main pages, common views | Основни страници, общи изгледи
├── 📁 products/          # Products, categories, API | Продукти, категории, API
├── 📁 orders/            # Orders, shopping cart | Поръчки, количка
├── 📁 reviews/           # Reviews, ratings | Отзиви, оценки
├── 📁 static/            # Static files (CSS, JS, images) | Статични файлове
├── 📁 templates/         # HTML templates | HTML шаблони
├── 📁 media/             # User uploaded files | Качени от потребителите файлове
├── 📁 djangoARExam/      # Project settings | Настройки на проекта
├── 🐍 manage.py          # Django management script | Django управляващ скрипт
├── 📄 requirements.txt   # Dependencies | Зависимости
└── 🔒 .env               # Environment variables (not in Git) | Променливи на средата
📄 License | Лиценз
This project is created for educational purposes as part of the Django Advanced course at SoftUni.

Този проект е създаден за образователни цели като част от курса Django Advanced в SoftUni.

👨‍💻 Author | Автор
Todor Yankov | Тодор Янков

GitHub: @TodorYankov

README updated: April 2026 | README актуализиран: април 2026 г.

Project for Django Advanced course – SoftUni | Проект за курса Django Advanced – SoftUni
