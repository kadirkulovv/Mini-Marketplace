from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthTests(APITestCase):
    def test_register_and_login_user(self):
        register_url = reverse('register')
        register_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'password2': 'password123',
            'phone': '+998901234567',
            'address': 'Toshkent shahar'
        }
        response = self.client.post(register_url, register_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
