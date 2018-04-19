from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as api_reverse
from rest_framework_jwt.settings import api_settings


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


User = get_user_model()


class AUTHAPITestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(username='admin', email='admin@gmail.com')
        user.set_password("mydjango")
        user.save()

    def test_created_user(self):
        qs = User.objects.filter(username='admin')
        self.assertEqual(qs.count(), 1)

    def test_register_user_api(self):
        register_url = api_reverse('api-auth:register')
        data = {
            'username': 'user_0',
            'email': 'user_0@gmail.com',
            'password': 'mydjango',
            'password2': 'mydjango'
        }
        response = self.client.post(register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        token_len = len(response.data.get("token", 0))
        self.assertGreater(token_len, 0)

    def test_register_user_api_fail(self):
        register_url = api_reverse('api-auth:register')
        data = {
            'username': 'user_0',
            'email': 'user_0@gmail.com',
            'password': 'mydjango',
        }
        response = self.client.post(register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password2'][0], 'This field is required.')

    def test_login_user_api(self):
        login_url = api_reverse('api-auth:login')
        data = {
            'username': 'admin',
            'password': 'mydjango',
        }
        response = self.client.post(login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data.get("token", 0)
        token_len = 0
        if token != 0:
            token_len = len(token)
        self.assertGreater(token_len, 0)

    def test_login_user_api_fail(self):
        login_url = api_reverse('api-auth:login')
        data = {
            'username': 'fake_user',
            'password': 'mydjango',
        }
        response = self.client.post(login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        token = response.data.get("token", 0)
        token_len = 0
        if token != 0:
            token_len = len(token)
        self.assertEqual(token_len, 0)

    def test_token_register_api(self):
        login_url = api_reverse('api-auth:login')
        data = {
            'username': 'admin',
            'password': 'mydjango',
        }
        response = self.client.post(login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data.get("token", None)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)

        register_url = api_reverse('api-auth:register')
        data2 = {
            'username': 'user_1',
            'email': 'user_1@gmail.com',
            'password': 'mydjango',
            'password2': 'mydjango'
        }
        response = self.client.post(register_url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_token_login_api(self):
        login_url = api_reverse('api-auth:login')
        data = {
            'username': 'admin',
            'password': 'mydjango',
        }
        response = self.client.post(login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data.get("token", None)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response2 = self.client.post(login_url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
