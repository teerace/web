import json
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser
from race.models import Server
from piston.decorator import decorator
from piston.resource import Resource as PistonResource
from piston.utils import rc, FormValidationError


class APIKeyAuthentication(object):
	"""
	API key authenticater.
	"""
	def __init__(self, realm='API'):
		self.realm = realm

	@staticmethod
	def is_authenticated(request):
		auth_string = request.META.get('HTTP_API_AUTH', None)

		if not auth_string:
			return False

		if not len(auth_string) == 32:
			return False

		try:
			server = Server.objects.get(public_key=auth_string)
			request.user = server.maintained_by
			request.server = server
			server.save() # bumps the last_connection_at
			request.throttle_extra = server.id
		except Server.DoesNotExist:
			request.user = AnonymousUser()

		return not request.user in (False, None, AnonymousUser())

	def challenge(self):
		resp = HttpResponse("{0} API - Authorization Required".format(self.realm))
		resp.status_code = 401
		return resp
		

def validate_mime(v_form, operation='POST'):
	""" This fetches the submitted data for the form 
	from request.data because we always expect JSON data
	It is otherwise a copy of piston.util.validate.
	"""
	del operation

	@decorator
	def wrap(wrapped_function, self, request, *a, **kwa):
		if not hasattr(request, 'data'):
			raise AttributeError("Validator expects serialized data.")
		form = v_form(request.data)

		if form.is_valid():
			setattr(request, 'form', form)
			return wrapped_function(self, request, *a, **kwa)
		else:
			raise FormValidationError(form)
	return wrap


class Resource(PistonResource):

	def form_validation_response(self, exception):
		"""
		Turns the error object into a serializable construct.
		All credit for this method goes to Jacob Kaplan-Moss
		"""

		# Create a 400 status_code response
		resp = rc.BAD_REQUEST
		resp.content = ""

		# Serialize the error.form.errors object
		json_errors = json.dumps(
			dict(
				(k, map(unicode, v))
				for (k,v) in exception.form.errors.iteritems()
			)
		)
		resp.write(json_errors)
		return resp
