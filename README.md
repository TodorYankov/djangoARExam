# **TechShop**

TechShop is an e-commerce web application developed with Django.
It allows users to browse products, place orders, and manage their purchases, while also providing an administrative interface for product and order management.

### Table of Contents
* Overview
* Features
* Installation
* Usage

### Overview
TechShop was created as an exam project to demonstrate Django development skills. It includes three main applications:
* **products** – product management (catalog, details, categories)
* **orders** – order processing (cart, checkout, history)
* **core** – core functionality (home page, navigation) + user profiles – planned for the next version

The application showcases:
* Product catalog with categories and stock tracking.
* Shopping cart and order placement.
* Order management with status updates.
* Admin panel for managing products, categories, and orders.
* Responsive user interface built with Bootstrap 5.

The goal is to provide a solid foundation for an online store that can be extended with additional features like user accounts, payment integration, and more.

### Features
* **Product Management**
  - List products by category.
  - Search and filter products.
  - Detailed product view.
  - Track stock quantity and availability.
* **Order Management**
  - Create new orders (manual entry by staff).
  - Automatic calculation of total price based on order items.
  - Multiple order statuses: Pending, Processing, Completed, Cancelled.
  - View order details with items and prices.
* **Admin Interface**
  - Customized Django admin for easy management of products, categories, and orders.
  - Inline editing of order items.
  - Status filters and search.
* **Responsive Design**
  - Mobile‑friendly interface with Bootstrap 5.
  - Intuitive navigation.

### Installation
Follow these steps to set up the project locally.

### Prerequisites
* Python 3.12 or higher
* pip
* Git
* Virtual environment (recommended)

### Clone the repository
- https://github.com/TodorYankov/djangoBRExam.git
- http://83.228.97.7/ -> Here is an installed and working empty project
- http://83.228.97.7/2/ -> Here is an installed and working project 
with a created category, product, and order

### **Create and activate a virtual environment**
#### **Windows:** (bash)
 - python -m venv .venv
 - .venv\Scripts\activate
#### Linux / macOS: (bash)
 - python3 -m venv .venv
 - source .venv/bin/activate

### Install Pillow in the virtual environment.
 - python -m pip install Pillow   

### **Install dependencies** (bash)
 - pip install -r requirements.txt

### **Environment variables**
In manage.py, add the following (adjust values as needed):
* SECRET_KEY=your_secret_key_here
* DEBUG=True
* ALLOWED_HOSTS=127.0.0.1,localhost

You can generate a secret key with: (bash)
- python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

### **Apply migrations** (bash)
- python manage.py makemigrations   # create migration files based on model changes
- python manage.py migrate           # apply migrations to the database

### **Create a superuser (for admin access)** (bash)
python manage.py createsuperuser

### **Run the development server** (bash)
python manage.py runserver

Open http://127.0.0.1:8000/ in your browser.

### **Usage**

### **Admin panel**
1.Go to http://127.0.0.1:8000/admin/ and log in with your superuser credentials.
2.From the dashboard you can:
- Add/edit categories and products.
- View and manage orders.
- Change order status.

### **User‑facing pages**
- Home page – http://127.0.0.1:8000/ – displays featured products (if any) and links to categories.
- Product list – http://127.0.0.1:8000/products/ – shows all products with filtering options.
- Product detail – click on any product to see full details.
- Orders – (staff only) http://127.0.0.1:8000/orders/ – list of orders with create/edit/delete capabilities.

### **Creating an order**
1. Go to the orders list and click New order.
2. Fill in the customer details and add items (select product and quantity).
3. The total amount is calculated automatically.
4. After saving, you can change the status from the order detail view.


With sample data (one category + one product)
- Here you need to create a fixture – this is Django's way to export/import data.

- Steps to create a fixture:

- On your local computer (where you have a working project with sample data):

- bash
- python manage.py dumpdata products.Category products.Product --indent 2 > initial_data.json
- This will create a JSON file with a structure like this:

json
[
  {
    "model": "products.category",
    "pk": 1,
    "fields": {
      "name": "Лаптопи",
      "description": "Лаптопи за всякакви нужди"
    }
  },
  {
    "model": "products.product",
    "pk": 1,
    "fields": {
      "name": "HP Compaq",
      "category": 1,
      "price": "180.00",
      "stock_quantity": 10
    }
  }
]
- Place this file in the products/fixtures/ directory (create it if it doesn't exist).




This README was created as part of an exam project documentation.





# **TechShop**

TechShop е уеб приложение за електронен магазин, разработено с Django.
То позволява на потребителите да разглеждат продукти, 
да правят поръчки и да управляват покупките си, като 
същевременно предоставя административен интерфейс за 
управление на продукти и поръчки.

Съдържание:
* Общ преглед
* Функционалности
* Инсталация
* Употреба


Общ преглед
TechShop е създаден като изпитен проект, целящ да демонстрира 
умения за разработка с Django. Той включва три основни приложения: 
* products – управление на продуктите (каталог, детайли, категории)
* orders – обработка на поръчки (количка, плащане, история)
* core – основна функционалност (начална страница, навигация) + потребителски профили - в следващата версия на продукта   
 
 Приложението показва:
* Каталог с продукти, категории и следене на наличност.
* Количка за пазаруване и създаване на поръчки.
* Управление на поръчки с промяна на статуса.
* Административен панел за управление на продукти, категории и поръчки.
* Адаптивен потребителски интерфейс, изграден с Bootstrap 5.

Целта е да се осигури солидна основа за онлайн магазин, която може да бъде разширявана с допълнителни функции като потребителски акаунти, плащания и други.
 
Функционалности
* Управление на продукти
  -  Списък на продуктите по категории.
  - Търсене и филтриране на продукти.
  - Детайлен изглед на продукт.
  - Следене на количество и наличие.

* Управление на поръчки
  - Създаване на нови поръчки (ръчно въвеждане от служител).
  - Автоматично изчисляване на общата сума на база артикулите в поръчката.
  - Няколко статуса на поръчка: Чакаща, Обработва се, Изпълнена, Отказана.
  - Преглед на детайли на поръчка с артикули и цени.

* Административен интерфейс
  - Персонализиран Django admin за лесно управление на продукти, категории и поръчки.
  - Вграден редактор на артикули в поръчката (inline).
  - Филтри по статус и търсене.

* Адаптивен дизайн
  - Мобилно-приятелски интерфейс с Bootstrap 5.
  - Интуитивна навигация.
  
* Инсталация
Следвайте тези стъпки, за да настроите проекта локално.

* Изисквания
  - Python 3.12 или по-нова версия
  - pip
  - Git
  - Виртуална среда (препоръчително) 

* Клониране на хранилището
- git clone https://github.com/TodorYankov/djangoBRExam.git
- http://83.228.97.7/     -> Тук се намира инсталиран и работещ празен проект
- http://83.228.97.7/2/  -> Тук се намира инсталиран и работещ проект 
със създадена категория, продукт и поръчка

* Създаване и активиране на виртуална среда
  - #### Windows: (bash)
    - python -m venv .venv
    - .venv\Scripts\activate
  - #### Linux / macOS: (bash)
    - python3 -m venv .venv
    - source .venv/bin/activate

* Инсталирайте Pillow във виртуалната среда.
 - python -m pip install Pillow    

* Инсталиране на зависимостите (bash)
  - pip install -r requirements.txt

* Настройка на променливи на средата
  - В manage.py добавете следното (коригирайте стойностите според нуждите):
     - SECRET_KEY=your_secret_key_here
     - DEBUG=True
     - ALLOWED_HOSTS=127.0.0.1,localhost
  - Можете да генерирате таен ключ чрез: (bash)
     - python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

* Прилагане на миграциите (bash)
  - python manage.py makemigrations – създава миграционни файлове (в папка migrations/) на базата на промените в моделите (например когато създадете нов модел или промените съществуващ).
  - python manage.py migrate – прилага тези миграции към базата данни (създава/променя таблиците).
  
* Създаване на суперпотребител (за административния панел) (bash)
  - python manage.py createsuperuser

* Зареждане на примерни данни (по желание) (bash)
  - python manage.py loaddata initial_data.json

* Стартиране на сървъра за разработка (bash)
  - python manage.py runserver
  - Отворете http://127.0.0.1:8000/ в браузъра си.
  
### Употреба
#### Административен панел
1. Отидете на http://127.0.0.1:8000/admin/ и влезте с данните на суперпотребителя.
2. От таблото можете да:
- Добавяте/редактирате категории и продукти. Първо трябва да създадете нова категория и след това нов продукт.
- Преглеждате и управлявате поръчки.
- Променяте статуса на поръчка.

#### Потребителски страници
* Начална страница – http://127.0.0.1:8000/ – показва представени продукти (ако има) и връзки към категории.
* Списък с продукти – http://127.0.0.1:8000/products/ – всички продукти с опции за филтриране.
* Детайли на продукт – кликнете върху произволен продукт, за да видите подробности.
* Поръчки – (само за служители) http://127.0.0.1:8000/orders/ – списък с поръчки, с възможност за създаване, редактиране и изтриване.

#### Създаване на поръчка
1.Отидете в списъка с поръчки и натиснете Нова поръчка.
2.Попълнете данните на клиента и добавете артикули (изберете продукт и количество).
3.Общата сума се изчислява автоматично.
4.След запис можете да промените статуса от детайлния изглед на поръчката.


С примерни данни (една категория + един продукт)
- Тук трябва да създадете fixture - това е начинът на Django да експортира/импортира данни .

- Стъпки за създаване на fixture:

- На вашия локален компютър (където имате работещ проект с примерни данни):

- bash
- python manage.py dumpdata products.Category products.Product --indent 2 > initial_data.json
- Това ще създаде JSON файл със структура като тази :

json
[
  {
    "model": "products.category",
    "pk": 1,
    "fields": {
      "name": "Лаптопи",
      "description": "Лаптопи за всякакви нужди"
    }
  },
  {
    "model": "products.product",
    "pk": 1,
    "fields": {
      "name": "HP Compaq",
      "category": 1,
      "price": "180.00",
      "stock_quantity": 10
    }
  }
]
- Поставете този файл в products/fixtures/ директория (създайте я, ако я няма)


Това README е създадено като част от документацията за изпитен проект.
