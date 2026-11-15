# Mini Marketplace REST API

Django REST Framework asosida yaratilgan onlayn do'kon backend loyihasi.

## Asosiy imkoniyatlar
- JWT autentifikatsiya (register, login, refresh)
- Mahsulotlar va kategoriyalar boshqaruvi
- Kategoriya, narx oralig'i va ombordagi mavjudlik bo'yicha filtrlash
- Qidiruv, saralash va sahifalash (pagination)
- Savat (Cart) tizimi (tovar qo'shish, ayirish, tozalash)
- Buyurtmalar (Order) yaratish va boshqarish (tranzaksiyalar va ombor zaxirasi nazorati)
- Mahsulotlarga sharh va baho berish (Reviews & Ratings)
- Swagger va ReDoc orqali hujjatlashtirish

## O'rnatish va ishga tushirish

1. Virtual muhit yaratish va faollashtirish:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

3. `.env` faylini to'ldirish (`.env.example` namunasi bo'yicha):
```env
SECRET_KEY=django-insecure-marketplace-final-project-secret-key-12345
DEBUG=True
ALLOWED_HOSTS=*
PG_NAME=django_rest_final
PG_USER=postgres
PG_PASS=your-password
PG_HOST=localhost
PG_PORT=5432
```

4. Bazaga migratsiyalarni yurgizish:
```bash
python manage.py migrate
```

5. Boshlang'ich test ma'lumotlarini yuklash:
```bash
python manage.py seed_data
```

6. Serverni ishga tushirish:
```bash
python manage.py runserver
```

## API Hujjatlari va Testlar
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- Testlarni tekshirish: `python manage.py test`
