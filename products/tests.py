from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Category, Product, Review

User = get_user_model()

class ProductTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.user = User.objects.create_user('normaluser', 'user@example.com', 'password123')
        self.category = Category.objects.create(name='Smartfonlar')
        self.product = Product.objects.create(
            category=self.category,
            name='iPhone 15',
            description='Yangi avlod telefoni',
            price=1200.00,
            stock=10,
            is_active=True
        )

    def test_category_list_public(self):
        url = reverse('category_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_category_create_permission(self):
        url = reverse('category_list_create')
        data = {'name': 'Noutbuklar'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_list_filter_search(self):
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'iPhone'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_product_review_and_rating(self):
        url = reverse('product-reviews', kwargs={'pk': self.product.id})
        self.client.force_authenticate(user=self.user)

        review_data = {'rating': 5, 'comment': 'Ajoyib smartfon, tavsiya qilaman!'}
        response = self.client.post(url, review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)

        detail_url = reverse('product-detail', kwargs={'pk': self.product.id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.data['avg_rating'], 5.0)
        self.assertEqual(detail_response.data['reviews_count'], 1)

        repeat_response = self.client.post(url, review_data)
        self.assertEqual(repeat_response.status_code, status.HTTP_400_BAD_REQUEST)
