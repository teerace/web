from datetime import datetime
from django.contrib.auth.models import User
from piston.handler import BaseHandler
from piston.utils import rc
from race.models import Map, Run
from lib.aes import aes_decrypt


class RunHandler(BaseHandler):
	"""
	Handles posting of Run objects to webapp.
	"""

	allowed_methods = ('POST',)
	model = Run

	@classmethod
	def resource_uri(cls):
		return ('api_run_manage', [])

	def create(self, request):
		"""
		Create one or more Run objects.
		
		To create more than one object, use list:
			[
			{...run1...},
			{...run2...}
			]
		"""
		if request.content_type:
			data = request.data

			success_count = 0
			run_count = len(data)
			for run in data:
				map_name = run['map']
				try:
					map_obj = Map.objects.get(name=map_name)
				except Map.DoesNotExist:
					continue
				user_id = run['user']
				try:
					user = User.objects.get(pk=user_id)
				except User.DoesNotExist:
					continue
				Run(
					map = map_obj,
					server = request.server,
					user = user,
					nickname = run['nickname'],
					time = float(run['time']),
					created_at = datetime.utcfromtimestamp(run['created_at'])
				).save()
				success_count += 1
			if success_count:
				resp = rc.CREATED
				resp.write(
					"Successfully stored {0} of {1} submitted runs.".format(
						success_count,
						run_count,
					)
				)
			else:
				resp = rc.BAD_REQUEST
				resp.write("None of the {0} submitted runs were stored.".format(run_count))
			return resp
		else:
			super(RunHandler, self).create(request)


class ValidateUserHandler(BaseHandler):
	"""
	Handles user/password checking.
	
	Uses AES and base64 to receive password, remember of
	using your server private key to generate cipher.
	
	Example of password encoding:
		base64_encode(aes_encrypt('password', PRIVATE_KEY))
	"""

	allowed_methods = ('GET',)
	model = User

	@classmethod
	def resource_uri(cls, username=None, encoded_pass=None):
		username_uri = 'username'
		encoded_pass_uri = 'encoded_pass'
		if username:
			username_uri = username.username
		if encoded_pass:
			encoded_pass_uri = encoded_pass
		return ('api_user_validate', [username_uri, encoded_pass_uri])

	def read(self, request, username, encoded_pass):
		"""
		Returns True or False, whether provided
		username and password pass the test.
		"""
		key = request.server.private_key
		try:
			password = aes_decrypt(encoded_pass, key)
			user = User.objects.get(username=username)
		except (TypeError, User.DoesNotExist):
			return False
		return user.check_password(password)
