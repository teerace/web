from django.contrib.auth.models import User
from piston.handler import BaseHandler
from piston.utils import rc, require_extended
from api.forms import ValidateUserForm
from race.forms import RunForm
from race.models import Run
from lib.aes import aes_decrypt
from lib.piston_utils import validate_mime


class RunHandler(BaseHandler):
	"""
	Handles posting of Run objects to webapp.
	"""

	allowed_methods = ('POST',)
	model = Run

	@classmethod
	def resource_uri(cls):
		return ('api_run_manage', [])

	@require_extended
	@validate_mime(RunForm)
	def create(self, request):
		"""
		Creates a Run object.
		"""

		Run(
			map = request.form.map,
			server = request.server,
			user = request.form.user,
			nickname = request.form.cleaned_data['nickname'],
			time = request.form.cleaned_data['time'],
			created_at = request.form.cleaned_data['created_at']
		).save()
		return rc.CREATED


class ValidateUserHandler(BaseHandler):
	"""
	Handles user/password checking.
	
	Uses AES and base64 to receive password, remember of
	using your server private key to generate cipher.
	
	Example of password encoding:
		base64_encode(aes_encrypt('password', PRIVATE_KEY))
	"""

	allowed_methods = ('POST',)
	model = User

	@classmethod
	def resource_uri(cls):
		return ('api_user_validate', [])

	@require_extended
	@validate_mime(ValidateUserForm)
	def create(self, request):
		"""
		Returns True or False, whether provided
		username and password pass the test.
		"""

		key = request.server.private_key
		try:
			password = aes_decrypt(request.form.cleaned_data['password'], key)
			user = User.objects.get(username=request.form.cleaned_data['username'])
		except (TypeError, User.DoesNotExist):
			return False
		return user.check_password(password)
