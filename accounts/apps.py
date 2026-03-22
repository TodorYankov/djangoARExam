# accounts/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Потребители и профили'

    def ready(self):
        """Извиква се при стартиране на Django"""
        # Създаване на групи и разрешения след миграции
        post_migrate.connect(create_default_groups, sender=self)


def create_default_groups(sender, **kwargs):
    """
    Създава групите по подразбиране:
    - Customers (обикновени потребители)
    - Staff (персонал)
    - Managers (мениджъри)
    """
    from django.contrib.auth.models import Group, Permission
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # ========== 1. ГРУПА: CUSTOMERS ==========
    customers_group, created = Group.objects.get_or_create(name='Customers')
    if created:
        print('✅ Създадена група: Customers')

    # ========== 2. ГРУПА: STAFF ==========
    staff_group, created = Group.objects.get_or_create(name='Staff')
    if created:
        print('✅ Създадена група: Staff')

        # Даване на разрешения на Staff
        staff_permissions = [
            'can_manage_orders',
            'can_view_reports',
        ]

        for perm_codename in staff_permissions:
            try:
                permission = Permission.objects.get(codename=perm_codename)
                staff_group.permissions.add(permission)
            except Permission.DoesNotExist:
                pass

    # ========== 3. ГРУПА: MANAGERS ==========
    managers_group, created = Group.objects.get_or_create(name='Managers')
    if created:
        print('✅ Създадена група: Managers')

        manager_permissions = [
            'can_manage_inventory',
            'can_manage_orders',
            'can_view_reports',
        ]

        for perm_codename in manager_permissions:
            try:
                permission = Permission.objects.get(codename=perm_codename)
                managers_group.permissions.add(permission)
            except Permission.DoesNotExist:
                pass

    # ========== 4. СЪЗДАВАНЕ НА ТЕСТОВИ ПОТРЕБИТЕЛИ ==========
    # Само при разработка (не в production)
    import sys
    if 'runserver' in sys.argv or 'migrate' in sys.argv:

        # Тестов потребител (Customers)
        if not User.objects.filter(username='testuser').exists():
            test_user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Тест',
                last_name='Потребител',
                phone_number='0888123456'
            )
            test_user.groups.add(customers_group)
            print('✅ Създаден тестов потребител: testuser / testpass123')

        # Тестов персонал (Staff)
        if not User.objects.filter(username='teststaff').exists():
            staff_user = User.objects.create_user(
                username='teststaff',
                email='staff@example.com',
                password='staffpass123',
                first_name='Тест',
                last_name='Персонал',
                phone_number='0888123456',
                is_staff=True
            )
            staff_user.groups.add(staff_group)
            print('✅ Създаден тестов персонал: teststaff / staffpass123')

        # Тестов мениджър (Managers)
        if not User.objects.filter(username='testmanager').exists():
            manager_user = User.objects.create_user(
                username='testmanager',
                email='manager@example.com',
                password='managerpass123',
                first_name='Тест',
                last_name='Мениджър',
                phone_number='0888123456',
                is_staff=True
            )
            manager_user.groups.add(managers_group)
            print('✅ Създаден тестов мениджър: testmanager / managerpass123')

