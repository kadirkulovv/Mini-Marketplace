from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order

User = get_user_model()

class OrderAndCartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('shopper', 'shopper@example.com', 'password123', address='Toshkent')
        self.category = Category.objects.create(name='Aksessuarlar')
        self.product = Product.objects.create(
            category=self.category,
            name='AirPods Pro',
            price=250.00,
            stock=5,
            is_active=True
        )

    def test_cart_add_and_order_create_flow(self):
        self.client.force_authenticate(user=self.user)

        cart_add_url = reverse('cart-add')
        add_response = self.client.post(cart_add_url, {'product_id': self.product.id, 'quantity': 2})
        self.assertEqual(add_response.status_code, status.HTTP_200_OK)
        self.assertEqual(add_response.data['total_price'], 500.00)

        order_url = reverse('order-list')
        order_response = self.client.post(order_url, {'address': 'Chilonzor 9'})
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order_response.data['status'], Order.STATUS_PENDING)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 0)

        order_id = order_response.data['id']
        cancel_url = reverse('order-cancel', kwargs={'pk': order_id})
        cancel_response = self.client.post(cancel_url)
        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel_response.data['status'], Order.STATUS_CANCELLED)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
