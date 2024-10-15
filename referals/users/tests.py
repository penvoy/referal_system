from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ref.models import Refcode, Referrals


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('register')  

    def test_register_user_success(self):
        data = {
            'username': 'testuser',
            'password': 'password123',
            'email': 'test@example.com'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

    def test_register_user_missing_fields(self):
        data = {
            'username': 'testuser',
            # 'password' отсутствует
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReferalRegisterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('refregister')  
        self.referrer = User.objects.create(username='referrer', password='password123')
        self.refcode = Refcode.objects.create(code='testcode', user=self.referrer)

    def test_referal_register_success(self):
        data = {
            'username': 'referraluser',
            'password': 'password123',
            'email':'user@test.com',
            'refcode': 'testcode'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertTrue(Referrals.objects.filter(reffered__username='referraluser').exists())

    def test_referal_register_missing_refcode(self):
        data = {
            'username': 'referraluser',
            'password': 'password123',
            # 'refcode' отсутствует
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_referal_register_invalid_refcode(self):
        data = {
            'username': 'referraluser',
            'password': 'password123',
            'refcode': 'invalidcode'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

