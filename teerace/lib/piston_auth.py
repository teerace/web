from django.http import HttpResponse
from django.contrib.auth.models import User, AnonymousUser
from race.models import Server


class APIKeyAuthentication(object):
	"""
	API key authenticater.
	"""
	def __init__(self, realm='API'):
		self.realm = realm

	def is_authenticated(self, request):
		auth_string = request.REQUEST.get('key', None)

		if not auth_string:
			return False

		if not len(auth_string) == 32:
			return False

		try:
			server = Server.objects.get(api_key=auth_string)
		except Server.DoesNotExist:
			return False

		request.user = server.maintained_by
		request.server = server
		request.throttle_extra = server.id

		return not request.user in (False, None, AnonymousUser())

	def challenge(self):
		resp = HttpResponse("Authorization Required")
		resp.status_code = 401
		return resp
