from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product
from cart.models import Cart

User = get_user_model()

class Command(BaseCommand):
    help = 'Boshlang\'ich test ma\'lumotlarini bazaga yuklash'

    def handle(self, *args, **options):
        client_user, created = User.objects.get_or_create(
            username='mijoz',
            defaults={
                'email': 'mijoz@example.com',
                'phone': '+998901234567',
                'address': 'Toshkent shahar, Yunusobod tumani, 12-uy'
            }
        )
        if created:
            client_user.set_password('mijoz123')
            client_user.save()
            Cart.objects.get_or_create(user=client_user)

        cat_electronics, _ = Category.objects.get_or_create(name='Elektronika')
        cat_clothing, _ = Category.objects.get_or_create(name='Kiyim-kechak')
        cat_books, _ = Category.objects.get_or_create(name='Kitoblar')

        products_data = [
            {
                'category': cat_electronics,
                'name': 'iPhone 15 Pro Max',
                'description': '256GB Black Titanium flagman smartfoni',
                'price': 1350.00,
                'stock': 12,
                'is_active': True,
            },
            {
                'category': cat_electronics,
                'name': 'MacBook Pro 14 M3',
                'description': '16GB RAM, 512GB SSD noutbuki',
                'price': 1850.00,
                'stock': 7,
                'is_active': True,
            },
            {
                'category': cat_electronics,
                'name': 'Sony WH-1000XM5',
                'description': 'Shovqinni bekor qiluvchi simsiz quloqchin',
                'price': 340.00,
                'stock': 20,
                'is_active': True,
            },
            {
                'category': cat_clothing,
                'name': 'Nike Air Force 1',
                'description': 'Klassik oq rangli charm krossovka',
                'price': 110.00,
                'stock': 25,
                'is_active': True,
            },
            {
                'category': cat_clothing,
                'name': 'Oversize Hoodie',
                'description': 'Qalin paxtali kundalik xudi',
                'price': 45.00,
                'stock': 30,
                'is_active': True,
            },
            {
                'category': cat_books,
                'name': 'Python Asoslari',
                'description': 'Dasturlashni noldan o\'rganuvchilar uchun kitob',
                'price': 15.00,
                'stock': 50,
                'is_active': True,
            },
        ]

        created_count = 0
        for item in products_data:
            _, created = Product.objects.get_or_create(
                name=item['name'],
                defaults=item
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Tayyor: Test mijoz va {created_count} ta mahsulot bazaga qo\'shildi.'))

