from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from django.test.client import Client
from django.utils import simplejson
from race.models import Map, Server
from lib.rsa import RSA

class TestCase(DjangoTestCase):
	fixtures = ['tests']

	def setUp(self):
		self.client = JsonClient()
		try:
			self.user = User.objects.get(pk=1)
		except User.DoesNotExist:
			self.user = User.objects.create_user('testclient', 'hello@world.com',
				'test123')
		self.user.save()
		self.map = Map.objects.get(pk=1)
		self.server = Server.objects.get(pk=1)
		self.extra = {
			'HTTP_API_AUTH': self.server.api_key,
		}

	def tearDown(self):
		self.user.delete()


class JsonClient(Client):

	def post(self, path, data=None, content_type='application/json',
		follow=False, **extra):
		if content_type == 'application/json':
			data = simplejson.dumps(data)
		return super(JsonClient, self).post(path, data, content_type, follow, **extra)

	def put(self, path, data=None, content_type='application/json',
		follow=False, **extra):
		if content_type == 'application/json':
			data = simplejson.dumps(data)
		return super(JsonClient, self).put(path, data, content_type, follow, **extra)


class ApiTest(TestCase):

	def test_auth_success(self):
		# we intentionally want to receive 405 Method Not Allowed
		response = self.client.put('/api/1/runs/detail/1/', {}, **self.extra)
		self.assertEqual(response.status_code, 405)

	def test_auth_no_key(self):
		self.extra['HTTP_API_AUTH'] = ''
		response = self.client.get('/api/1/runs/detail/1/', {}, **self.extra)
		self.assertEqual(response.status_code, 401)

	def test_auth_invalid_key(self):
		self.extra['HTTP_API_AUTH'] = 'invalid'
		response = self.client.get('/api/1/runs/detail/1/', {}, **self.extra)
		self.assertEqual(response.status_code, 403)


class RunTest(TestCase):

	def test_create_run_success(self):
		data = {
			'map_name': self.map.name,
			'user_id': self.user.id,
			'nickname': "[GER] Ueber Tester",
			'time': 14.72,
			'created_at': "2010-12-10 16:53:20",
		}
		response = self.client.post('/api/1/runs/new/', data, **self.extra)
		self.assertEqual(response.status_code, 200)

	def test_create_run_wrong_map(self):
		data = {
			'map_name': "wrong_map",
			'user_id': self.user.id,
			'nickname': "[AUS] Lame Badass",
			'time': 151.02,
		}
		response = self.client.post('/api/1/runs/new/', data, **self.extra)
		self.assertEqual(response.status_code, 400)

	def test_create_map_wrong_user(self):
		data = {
			'map_name': "wrong_map",
			'user_id': 666, # what
			'nickname': "[AUS] Lame Badass",
			'time': 151.02,
		}
		response = self.client.post('/api/1/runs/new/', data, **self.extra)
		self.assertEqual(response.status_code, 400)


class UserTestCase(TestCase):

	def test_validate_user_success(self):
		data = {
			'username': "testclient",
			'password': "test123",
		}
		data['password'] = RSA().encrypt(data['password']).encode('base64')
		response = self.client.post('/api/1/users/auth/', data, **self.extra)
		self.assertTrue(simplejson.loads(response.content))

	def test_validate_user_wrong_password(self):
		data = {
			'username': "testclient",
			'password': "toast123", # WHOOOPS, A TYPO!
		}
		data['password'] = RSA().encrypt(data['password']).encode('base64')
		response = self.client.post('/api/1/users/auth/', data, **self.extra)
		self.assertFalse(simplejson.loads(response.content))

	def test_validate_user_wrong_username(self):
		data = {
			'username': "toastclient", # O NOEZ
			'password': "toast123", # WHOOOPS, A TYPO!
		}
		data['password'] = RSA().encrypt(data['password']).encode('base64')
		response = self.client.post('/api/1/users/auth/', data, **self.extra)
		self.assertFalse(simplejson.loads(response.content))

	def test_update_skin_success(self):
		data = {
			'skin_name': "bluekitty",
			'body_color': 16777215,
			'feet_color': 16777215,
		}
		response = self.client.put('/api/1/users/skin/1/', data, **self.extra)
		self.assertEqual(response.status_code, 200)

	def test_update_skin_custom_name_success(self):
		data = {
			'skin_name': "coolbanana",
			'body_color': 16777215,
			'feet_color': 16777215,
		}
		response = self.client.put('/api/1/users/skin/1/', data, **self.extra)
		self.assertEqual(response.status_code, 200)

	def test_update_skin_too_big_int(self):
		data = {
			'skin_name': "bluekitty",
			'body_color': 16777215,
			'feet_color': 16777216,
		}
		response = self.client.put('/api/1/users/skin/1/', data, **self.extra)
		self.assertEqual(response.status_code, 400)

