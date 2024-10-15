import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Refcode, User
import uuid
import time

class RefcodeViewsetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_code_success(self):
        url = reverse('refcode-create-code')  
        payload = {
            "expDate": time.time() + 3600  
        }
        response = self.client.post(url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('code', response.data)

    def test_create_code_without_exp_date(self):
        url = reverse('refcode-create-code')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "Не передан параметр истечения срока действия кода")

    def test_create_code_with_active_code(self):
        Refcode.objects.create(
            code=uuid.uuid4(),
            date_created=time.time(),
            date_end=time.time() + 3600,
            user=self.user,
            is_active=True
        )
        url = reverse('refcode-create-code')
        payload = {
            "expDate": time.time() + 3600
        }
        response = self.client.post(url, json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "У данного пользователя уже существует активный код")

    def test_destroy_code_success(self):
        refcode = Refcode.objects.create(
            code=uuid.uuid4(),
            date_created=time.time(),
            date_end=time.time() + 3600,
            user=self.user,
            is_active=True
        )
        url = reverse('refcode-destroy-code', args=[refcode.id])  
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Refcode.objects.filter(id=refcode.id).exists())


class ReferalViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_referals_unsuccess(self):
        url = reverse('referals')  
        response = self.client.get(url, {"refferer_id": self.user.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_referals_without_refferer_id(self):
        url = reverse('referals')  
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "Не передан id реферера")
