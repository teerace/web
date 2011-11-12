from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from piston.handler import AnonymousBaseHandler
from piston.utils import throttle, validate
from api.forms import TokenClientForm
from race.models import Server
from lib.piston_utils import rc, rcs


class ServerHandler(AnonymousBaseHandler):
	allowed_methods = ()
	fields = ('address')
	model = Server


class AnonClientHandler(AnonymousBaseHandler):
	allowed_methods = ('GET', 'POST')
	model = User
	
	@throttle(5, 600)
	def _read_servers(self, request, *args, **kwargs):
		return Server.objects.exclude(is_active=False)

	def read(self, request, action, *args, **kwargs):
		"""
		URL
			**/api/1/anonclient/servers/**
		Shortdesc
			Returns a list of Teerace servers.
		Arguments
			- none
		Data
			- none
		Result
			- 200
				list of Server objects

		"""
		allowed_actions = ['servers']
		if action in allowed_actions:
			return getattr(self, '_read_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)

	@throttle(5, 600)
	@validate(TokenClientForm)
	def _create_get_token(self, request, *args, **kwargs):
		form = request.form.cleaned_data
		user = authenticate(username=form.get('username'),
			password=form.get('password'))
		if not user or not user.is_active:
			return False
		return user.profile.api_token

	def create(self, request, action, *args, **kwargs):
		"""
		URL
			**/api/1/anonclient/get_token/**
		Shortdesc
			Returns API token of the matched User.
		Arguments
			- none
		Data
			- username / string / username of the user
			- password / string / user's password
		Result
			- 200, when there was no match
				False
			- 200, when there is a match
				Matched user API token

		"""
		allowed_actions = ['get_token']
		if action in allowed_actions:
			return getattr(self, '_create_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)
