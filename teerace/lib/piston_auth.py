from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser
from race.models import Server


class APIKeyAuthentication(object):
	"""
	API key authenticater.
	"""
	def __init__(self, realm='API'):
		self.realm = realm

	@staticmethod
	def is_authenticated(request):
		auth_string = request.REQUEST.get('key', None)

		if not auth_string:
			return False

		if not len(auth_string) == 32:
			return False

		try:
			server = Server.objects.get(public_key=auth_string)
			request.user = server.maintained_by
			request.server = server
			request.throttle_extra = server.id
		except Server.DoesNotExist:
			request.user = AnonymousUser()

		return not request.user in (False, None, AnonymousUser())

	def challenge(self):
		resp = HttpResponse("{0} API - Authorization Required".format(self.realm))
		resp.status_code = 401
		return resp
