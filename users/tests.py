from datetime import timedelta
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from users.models import EmailVerification, User


class UserRegistratioViewTestCase(TestCase):

    def test_user_registration_get(self):
        path = reverse('users:registration')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store - Регистрация')
        self.assertTemplateUsed(response, 'users/registration.html')

    def test_user_registration_post_success(self):
        data = {'first_name': 'Veronique', 'last_name': 'Ivanova',
        'username': 'Veronique', 'email': 'kovalsky2912@gmail.com',
        'password1': '12345678vV', 'password2': '12345678vV'}
        path = reverse('users:registration')
        self.assertFalse(User.objects.filter(username=data['username']).exists())
        response = self.client.post(path, data)

        # check creating of user
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'), fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(username=data['username']).exists())

        # check creating of email verification
        email_verification = EmailVerification.objects.filter(user__username=data['username'])
        self.assertTrue(email_verification.exists())
        self.assertEqual(email_verification.first().expiration.date(),
                         (now() + timedelta(hours=48)).date())

    def test_user_registration_post_errors(self):
        data = {'first_name': 'Veronique', 'last_name': 'Ivanova',
                'username': 'Veronique', 'email': 'kovalsky2912@gmail.com',
                'password1': '12345678vV', 'password2': '12345678vV'}
        path = reverse('users:registration')
        User.objects.create(username=data['username'])
        response = self.client.post(path, data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Пользователь с таким именем уже существует.', html=True)
