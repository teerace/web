import unittest
from django.contrib.auth.models import User
from django.test.client import Client
from django.utils import simplejson
from race.models import Map, Server
from lib.aes import aes_encrypt

class TestCase(unittest.TestCase):
	def setUp(self):
		self.client = JsonClient()
		if not User.objects.count():
			self.user = User.objects.create_user(
				username = "test",
				password = "test",
				email = "test@test.com",
			)
		else:
			self.user = User.objects.get(pk=1)
		self.map = Map.objects.get_or_create(
			name='test',
			created_by=self.user,
			author='test author',
			map_file='uploads/maps/test_fd23d879.map',
			crc='fd23d879'
		)[0]
		self.server = Server.objects.get_or_create(
			name = "Test server",
			maintained_by = self.user,
		)[0]
		self.extra = {
			'HTTP_API_AUTH': self.server.public_key,
		}


class JsonClient(Client):

	def post(self, path, data=None, content_type='application/json',
		follow=False, **extra):
		if content_type == 'application/json':
			data = simplejson.dumps(data)
		return super(JsonClient, self).post(path, data, content_type, follow, **extra)


class RunTestCase(TestCase):

	def testAuthSuccess(self):
		# we intentionally want to receive 405 Not Implemented
		response = self.client.get('/api/1/runs/', {}, **self.extra)
		self.assertEqual(response.status_code, 405)

	def testAuthFailure(self):
		self.extra['HTTP_API_AUTH'] = 'invalid'
		response = self.client.get('/api/1/runs/', {}, **self.extra)
		self.assertEqual(response.status_code, 401)

	def testCreateRunSuccess(self):
		data = {
			'map_name': self.map.name,
			'user_id': self.user.id,
			'nickname': "[GER] Ueber Tester",
			'time': 14.72,
			'created_at': "2010-12-10 16:53:20",
		}
		response = self.client.post('/api/1/runs/', data, **self.extra)
		self.assertEqual(response.status_code, 201)

	def testCreateRunWrongMapFailure(self):
		data = {
			'map_name': "wrong_map",
			'user_id': self.user.id,
			'nickname': "[AUS] Lame Badass",
			'time': 151.02,
		}
		response = self.client.post('/api/1/runs/', data, **self.extra)
		self.assertEqual(response.status_code, 400)

	def testValidateUserWrongUserFailure(self):
		data = {
			'map_name': "wrong_map",
			'user_id': 2, # what
			'nickname': "[AUS] Lame Badass",
			'time': 151.02,
		}
		response = self.client.post('/api/1/runs/', data, **self.extra)
		self.assertEqual(response.status_code, 400)


class UserTestCase(TestCase):

	def testValidateUserSuccess(self):
		data = {
			'username': "test",
			'password': "test",
		}
		data['password'] = aes_encrypt(data['password'], self.server.private_key)
		response = self.client.post('/api/1/users/validate/', data, **self.extra)
		self.assertTrue(simplejson.loads(response.content))

	def testValidateUserWrongPasswordFailure(self):
		data = {
			'username': "test",
			'password': "toast", # WHOOOPS, A TYPO!
		}
		data['password'] = aes_encrypt(data['password'], self.server.private_key)
		response = self.client.post('/api/1/users/validate/', data, **self.extra)
		self.assertFalse(simplejson.loads(response.content))

	def testValidateUserWrongUsernameFailure(self):
		data = {
			'username': "toast", # O NOEZ
			'password': "toast", # WHOOOPS, A TYPO!
		}
		data['password'] = aes_encrypt(data['password'], self.server.private_key)
		response = self.client.post('/api/1/users/validate/', data, **self.extra)
		self.assertFalse(simplejson.loads(response.content))

