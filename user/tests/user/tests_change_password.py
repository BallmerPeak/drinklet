from django.test import TestCase
from django.contrib.auth.models import User
from user.models import UserProfile
from user.views import change_password
from django.test import RequestFactory
from django.test import Client


class ChangePasswordTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('testuser', 'email@email.com', 'password')
        self.profile = UserProfile.objects.create(user=self.user)

    def test_change_success(self):
        c = Client()
        c.login(username='testuser', password='password')
        test = c.post('/user/change_password', {'oldpwd': 'password', 'newpwd':'pass', 'confirmpwd':'pass'})
        self.assertEqual(test.content, b'{"redirect": "/user/profile"}')
        self.assertEqual(test.status_code, 200)

    def test_old_password_incorrect(self):
        request = self.factory.post('/user/change_password', {'oldpwd': 'test', 'newpwd':'pass', 'confirmpwd':'pass'})
        request.user = self.user
        self.assertEqual(change_password(request).status_code, 401)
        self.assertEqual(change_password(request).content, b'Your old password was entered incorrectly. Please enter it again.')

    def test_new_password_mismatch(self):
        request = self.factory.post('/user/change_password', {'oldpwd': 'password', 'newpwd':'pass', 'confirmpwd':'word'})
        request.user = self.user
        self.assertEqual(change_password(request).status_code, 401)
        self.assertEqual(change_password(request).content, b"The two password fields didn't match.")

    def test_empty_password(self):
        request = self.factory.post('/user/change_password', {'oldpwd': 'password', 'newpwd':'', 'confirmpwd':''})
        request.user = self.user
        self.assertEqual(change_password(request).status_code, 401)
        self.assertEqual(change_password(request).content, b'You cannot have an empty password')

    def test_change_to_same_password(self):
        request = self.factory.post('/user/change_password', {'oldpwd': 'password', 'newpwd':'password', 'confirmpwd':'password'})
        request.user = self.user
        self.assertEqual(change_password(request).status_code, 401)
        self.assertEqual(change_password(request).content, b'You cannot change to the same password')
