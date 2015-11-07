from django.test import TestCase
from user import forms
from django.contrib.auth.models import User


class RegisterTestCase(TestCase):

    post = {'username': '', 'email': '', 'pwd': '', 'pwd2':'' }

    def setUp(self):
        ###Simulate  bad POSTs###

        self.username = 'username'
        self.email = 'email'
        self.p1 = 'pwd'
        self.p2 = 'pwd2'
        self.var = list(self.post.keys())

        self.goodUsername = "John"
        self.goodEmail = "john@ballmer.com"
        self.goodPass = ["johnballmer", "johnballmer"]

        self.goodvars = [self.goodUsername, self.goodEmail, self.goodPass[0], self.goodPass[1]]

        self.badUsername = "John"
        self.badEmail = "johnballmer"
        self.badPass = ["swag", "schwag"]




    """<--Testing no fields-->"""
    def test_nofield(self):
        self.post = {'username': '', 'email': '', 'pwd': '', 'pwd2':'' }
        for i in range(4):
            for m in [x%4 for x in range(i, i + 3)]:
                self.post[self.var[m]] = self.goodvars[m]

            self.post = {'username': '', 'email': '', 'pwd': '', 'pwd2':'' }

        f = forms.RegisterForm(self.post)
        self.assertFalse(f.is_valid())

    """<--Testing bad username -->"""
    def test_bad_username(self):
        user = User.objects.create_user('Rick', self.goodEmail, self.goodPass[0])
        self.post = {self.username: 'Rick', self.email: 'rick@mail.com', self.p1: self.badPass[0], self.p2: self.badPass[1]}
        f = forms.RegisterForm(self.post)
        self.assertFalse(f.is_valid())


    """<--Testing bad password-->"""
    def test_bad_password(self):
        self.post = {self.username: self.goodUsername, self.email: self.goodEmail, self.p1: self.badPass[0], self.p2: self.badPass[1]}
        f = forms.RegisterForm(self.post)
        self.assertFalse(f.is_valid())
        User.objects.filter(username='Rick').delete()


    """<--Testing bad email-->"""
    def test_bad_email(self):
        self.post = {self.username: self.goodUsername, self.email: self.badEmail, self.p1: self.goodPass[0], self.p2: self.goodPass[1]}
        f = forms.RegisterForm(self.post)
        self.assertFalse(f.is_valid())

        """  Another test for duplicate emails  """
        user = User.objects.create_user('Rick', self.goodEmail, self.goodPass[0])
        self.post = {self.username: self.badUsername, self.email: self.goodEmail, self.p1: self.goodPass[0], self.p2: self.goodPass[1]}
        f = forms.RegisterForm(self.post)
        self.assertFalse(f.is_valid())
        User.objects.filter(username='Rick').delete()


    """<--Testing good data-->"""
    def test_good_data(self):
        self.post = {self.username: "john", self.email: "amadouba@uwm.edu", self.p1: "adfsf", self.p2: "adfsf"}
        f = forms.RegisterForm(self.post)
        self.assertTrue(f.is_valid(),msg = f.errors)