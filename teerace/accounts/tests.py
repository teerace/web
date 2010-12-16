from django.test import TestCase
from accounts.forms import LoginForm, RegisterForm


class RegisterTest(TestCase):
	fixtures = ['tests.json']

	def setUp(self):
		self.data = {
			'username': 'testclient',
			'password1': 'test123',
			'password2': 'test123',
			'email1': 'testclient@example.com',
			'email2': 'testclient@example.com',
		}

	def test_user_already_exists(self):
		form = RegisterForm(self.data)
		self.assertFalse(form.is_valid())
		self.assertEqual(form["username"].errors,
			["Username is already taken"])

	def test_passwords_dont_match(self):
		data = self.data
		data['password2'] = '123test'
		form = RegisterForm(data)
		self.assertFalse(form.is_valid())
		self.assertEqual(form["password2"].errors,
			["You must type the same password each time"])

	def test_emails_dont_match(self):
		data = self.data
		data['email2'] = 'clienttest@example.com'
		form = RegisterForm(data)
		self.assertFalse(form.is_valid())
		self.assertEqual(form["email2"].errors,
			["You must type the same e-mail address each time"])

	def test_success(self):
		data = self.data
		data['username'] = 'newclient'
		form = RegisterForm(data)
		self.assertTrue(form.is_valid())


class LoginTest(TestCase):
	fixtures = ['tests.json']

	def setUp(self):
		self.data = {
			'username': 'testclient',
			'password': 'test123',
		}

	def test_wrong_username(self):
		data = self.data
		data['username'] = 'toastclient'
		form = LoginForm(data)
		self.assertFalse(form.is_valid())
		self.assertEqual(form.errors['__all__'],
			["Invalid username and/or password"])

	def test_success(self):
		data = self.data
		form = LoginForm(data)
		self.assertTrue(form.is_valid())
