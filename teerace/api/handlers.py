from datetime import datetime
from django.contrib.auth.models import User
from brabeion import badges
from piston.handler import BaseHandler
from piston.utils import require_extended
from accounts.models import UserProfile
from api.forms import (ValidateUserTokenForm,
	UserGetByNameForm, SkinUserForm, RunForm)
from race import tasks
from race.models import Run, Map, BestRun, Server
from lib.rsa import RSA
from lib.piston_utils import rc, rcs, validate_mime
from lib.rgb import rgblong_to_hex
from annoying.functions import get_object_or_None


class RunHandler(BaseHandler):
	allowed_methods = ('GET', 'POST')
	fields = ('id', 'user', 'time', 'checkpoints_list')
	model = Run

	@classmethod
	def resource_uri(cls, run=None):
		run_id = 'id'
		if run:
			run_id = run.id
			return ('api_runs_detail', [run_id])

	def _read_detail(self, request, *args, **kwargs):
		if 'id' in kwargs:
			try:
				run = Run.objects.get(pk=kwargs['id'])
				return run
			except Run.DoesNotExist:
				return rc(rcs.NOT_FOUND)
		return rc(rcs.BAD_REQUEST)

	def read(self, request, action, *args, **kwargs):
		"""
		URL
			**/api/1/runs/detail/{id}/**
		Shortdesc
			Returns an instance of Run.
		Arguments
			- id / integer / ID of requested Run
		Data
			- none
		Result
			- 404 - when Run with specified ID doesn't exist
			- 400 - when there was no ID specified
			- 200 - when everything went fine
				Run object

		"""
		# without '_read_' prefix
		allowed_actions = ['detail']
		if action in allowed_actions:
			return getattr(self, '_read_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)

	@require_extended
	@validate_mime(RunForm)
	def _create_new(self, request, *args, **kwargs):
		try:
			filtered_checkpoints = ";".join([v for v in \
				request.form.cleaned_data['checkpoints'].split(";") if float(v) != 0.0])
		except ValueError:
			filtered_checkpoints = ""
		run = Run(
			map = request.form.map,
			server = request.server,
			user = request.form.user,
			nickname = request.form.cleaned_data['nickname'],
			time = request.form.cleaned_data['time'],
			checkpoints = filtered_checkpoints,
		)
		run.save()
		tasks.redo_ranks.delay(run.id)
		tasks.set_server_map.delay(request.server.id, request.form.map.id)
		if request.form.user != None:
			request.form.user.profile.update_connection(request.server)
			badges.possibly_award_badge("run_finished",
				user=request.form.user, run=run)
		return run

	def create(self, request, action, *args, **kwargs):
		"""
		URL
			**/api/1/runs/new/**
		Shortdesc
			Handles posting of Run objects to webapp.
		Longdesc
			Creates a Run object.
			Checks for new badges and adds a Celery task to rebuild ranks.
		Arguments
			- none
		Data
			- map_id / integer / ID of the finished map
			- user_id / integer / ID of the user who finished the map
			                      (use None for anonymous user)
			- nickname / string / currently used nickname by the user
			- time / decimal / user result
			- checkpoints / string / semicolon-delimited (;) list of checkpoint times
		Results
			- 400 - when data fails validation
				dictionary containing error message(s)
			- 200 - when everything went fine
				Run object
		"""
		allowed_actions = ['new']
		if action in allowed_actions:
			return getattr(self, '_create_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)


class UserProfileHandler(BaseHandler):
	allowed_methods = ()
	fields = ('points', 'country', 'get_skin')
	model = UserProfile


class UserHandler(BaseHandler):
	allowed_methods = ('GET', 'POST', 'PUT')
	fields = ('id', 'username', 'is_superuser', 'is_staff', 'profile')
	model = User

	@classmethod
	def resource_uri(cls, user=None):
		user_id = 'user_id'
		if user:
			user_id = user.id
			return ('api_users_detail', [user_id])

	def _read_detail(self, request, *args, **kwargs):
		if 'id' in kwargs:
			try:
				user = User.objects.get(pk=kwargs['id'])
			except User.DoesNotExist:
				return rc(rcs.NOT_FOUND)
			return user
		return rc(rcs.BAD_REQUEST)

	def _read_profile(self, request, *args, **kwargs):
		if 'id' in kwargs:
			try:
				profile = UserProfile.objects.get(pk=kwargs['id'])
			except UserProfile.DoesNotExist:
				return rc(rcs.NOT_FOUND)
			return profile
		return rc(rcs.BAD_REQUEST)

	def _read_rank(self, request, *args, **kwargs):
		if 'id' in kwargs:
			try:
				profile = UserProfile.objects.get(pk=kwargs['id'])
			except UserProfile.DoesNotExist:
				return rc(rcs.NOT_FOUND)
			return profile.position
		return rc(rcs.BAD_REQUEST)

	def _read_map_rank(self, request, *args, **kwargs):
		if 'id' in kwargs and 'map_id' in kwargs:
			try:
				profile = UserProfile.objects.get(pk=kwargs['id'])
			except UserProfile.DoesNotExist:
				return rc(rcs.NOT_FOUND)
			return {
				'position': profile.map_position(kwargs['map_id']),
				'bestrun': profile.best_score(kwargs['map_id']),
			}
		return rc(rcs.BAD_REQUEST)

	def read(self, request, action, *args, **kwargs):
		"""
		URL
			**/api/1/users/detail/{id}/**
		Shortdesc
			Returns an instance of User.
		Arguments
			- id / integer / ID of requested User
		Data
			- none
		Result
			- 404 - when User with specified ID doesn't exist
			- 400 - when there was no ID specified
			- 200 - when everything went fine
				User object


		URL
			**/api/1/users/profile/{id}/**
		Shortdesc
			Returns an instance of user's UserProfile.
		Arguments
			- id / integer / ID of requested UserProfile
		Data
			- none
		Result
			- 404 - when UserProfile with specified ID doesn't exist
			- 400 - when there was no ID specified
			- 200 - when everything went fine
				UserProfile object


		URL
			**/api/1/users/rank/{id}/**
		Shortdesc
			Returns user global rank.
		Arguments
			- id / integer / ID of User
		Data
			- none
		Result
			- 404 - when UserProfile with specified ID doesn't exist
			- 400 - when there was no ID specified
			- 200 - when everything went fine
				(integer) user global rank
				OR None when the user is not ranked


		URL
			**/api/1/users/map_rank/{id}/{map_id}/**
		Shortdesc
			Returns user global rank.
		Arguments
			- id / integer / ID of the user
			- map_id / integer / ID of the map
		Data
			- none
		Result
			- 404 - when UserProfile with specified ID doesn't exist
			- 400 - when there was no ID specified
			- 200 - when everything went fine
				(integer) user map rank
		"""
		# without '_read_' prefix
		allowed_actions = ['detail', 'profile', 'rank', 'map_rank']
		if action in allowed_actions:
			return getattr(self, '_read_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)

	@require_extended
	@validate_mime(ValidateUserTokenForm)
	def _create_auth_token(self, request, *args, **kwargs):
		try:
			user = User.objects.get(
				profile__api_token=request.form.cleaned_data.get('api_token')
			)
		except User.DoesNotExist:
			return False
		return user

	@require_extended
	@validate_mime(UserGetByNameForm)
	def _create_get_by_name(self, request, *args, **kwargs):
		try:
			user = User.objects.get(
				username=request.form.cleaned_data.get('username')
			)
		except User.DoesNotExist:
			return rc(rcs.NOT_FOUND)
		return user.id

	def create(self, request, action, *args, **kwargs):
		"""
		URL
			**/api/1/users/auth_token/**
		Shortdesc
			Handles user/password checking.
		Longdesc
			Returns User object or False, whether provided
			api token passes the test.
		Arguments
			- none
		Data
			- api_token / string / user's API token
		Result
			- 200, when data fails validation
				False
			- 200, when user data are correct
				User object


		URL
			**/api/1/users/get_by_name/**
		Shortdesc
			Returns User object of the matched username.
		Arguments
			- none
		Data
			- username / string / searched user name
		Result
			- 404, when there was no match
			- 200, when there is a match
				User object

		"""
		allowed_actions = ['auth_token', 'get_by_name']
		if action in allowed_actions:
			return getattr(self, '_create_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)

	@validate_mime(SkinUserForm, 'PUT')
	def _update_skin(self, request, *args, **kwargs):
		if 'id' in kwargs:
			try:
				profile = UserProfile.objects.get(id=kwargs['id'])
			except UserProfile.DoesNotExist:
				return rc(rcs.BAD_REQUEST)
			profile.has_skin = True
			form = request.form.cleaned_data
			profile.skin_name = form['skin_name']
			profile.skin_body_color_raw = form['body_color']
			profile.skin_body_color = rgblong_to_hex(form['body_color'])
			profile.skin_feet_color_raw = form['feet_color']
			profile.skin_feet_color = rgblong_to_hex(form['feet_color'])
			profile.save()
			return profile
		return rc(rcs.BAD_REQUEST)

	@require_extended
	def update(self, request, action, *args, **kwargs):
		"""
		URL
			**/api/1/users/skin/{id}/**
		Shortdesc
			Updates user skin settings
		Arguments
			- id / ID of the user
		Data
			- skin_name / string /
				name of used skin; if it's not an official skin,
				defaults to 'default'
			- body_color / integer / rgblong representation of body color
			- feet_color / integer / rgblong representation of feet color
		Result
			- 400, when data fails validation
			- 400, when requested UserProfile doesn't exist
			- 200, when everything went fine
				UserProfile object
		"""
		# without '_update_' prefix
		allowed_actions = ['skin']
		if action in allowed_actions:
			return getattr(self, '_update_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)


class MapHandler(BaseHandler):
	allowed_methods = ('GET',)
	fields = ('id', 'name', 'author', 'crc', 'run_count',
		'get_best_score', 'get_download_url')
	model = Map

	@classmethod
	def resource_uri(cls, map_obj=None):
		map_id = 'map_id'
		if map_obj:
			map_id = map_obj.id
			return ('api_maps_detail', [map_id])

	def _read_list(self, request, *args, **kwargs):
		return Map.objects.all()

	def _read_detail(self, request, *args, **kwargs):
		if 'map_id' in kwargs:
			try:
				map_obj = Map.objects.get(pk=kwargs['map_id'])
			except Map.DoesNotExist:
				return rc(rcs.NOT_FOUND)
			return map_obj
		return rc(rcs.BAD_REQUEST)

	def _read_rank(self, request, *args, **kwargs):
		if 'map_id' in kwargs:
			try:
				map_obj = Map.objects.get(pk=kwargs['map_id'])
			except Map.DoesNotExist:
				return rc(rcs.NOT_FOUND)
			offset = int(kwargs['offset'])-1 if 'offset' in kwargs else 0
			return BestRun.objects.filter(map=map_obj).select_related() \
				.order_by('-points')[offset:offset+5]
		return rc(rcs.BAD_REQUEST)

	def read(self, request, action, *args, **kwargs):
		"""
		URL
			**/api/1/maps/detail/{map_id}/**
		Shortdesc
			Returns an instance of Map.
		Arguments
			- map_id / integer / ID of the map
		Data
			- none
		Result
			- 404 - when Map with specified map_id doesn't exist
			- 400 - when there was no map_id specified
			- 200 - when everything went fine
				Map object


		URL
			**/api/1/maps/list/**
		Shortdesc
			Returns a list containing all Map objects
		Arguments
			- none
		Data
			- none
		Result
			- 200 - when everything went fine
				a list of Map objects


		URL
			**/api/1/maps/rank/{map_id}/[{offset}/]**
		Shortdesc
			Returns a list containing 5 elements of map rank,
			starting with offset (default is 1)
		Arguments
			- map_id / integer / ID of the map
			- offset / integer / 
		Data
			- none
		Result
			- 200 - when everything went fine
				a list of BestRun objects
		"""
		# without '_read_' prefix
		allowed_actions = ['list', 'detail', 'rank']
		if action in allowed_actions:
			return getattr(self, '_read_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)


class ServerHandler(BaseHandler):
	allowed_methods = ()
	fields = ('id', 'name', 'description')
	model = Server


class PingHandler(BaseHandler):
	"""
	GET: Used to check if server is online.
	
	POST: Updates server and its users last connection time.
	"""

	allowed_methods = ('GET', 'POST',)

	def read(self, request, action):
		"""
		URL
			**/api/1/hello/**
		Shortdesc
			Allows gameserver to check if webapp is online.
		Arguments
			- none
		Data
			- none
		Result
			- 200 - always
				PONG
		"""
		if action != 'hello':
			return rc(rcs.BAD_REQUEST)
		return "PONG"

	@require_extended
	def create(self, request, action):
		"""
		URL
			**/api/1/ping/**
		Shortdesc
			Updates server and its users last connection time.
		Arguments
			- none
		Data
			- users / dictionary / (int)user_id:(string)nickname dictionary
			- anonymous / tuple / a tuple with anonymous' nicknames
			- map / string / currently played map
		Result
			- 200 - when everything went fine
				PONG
		"""
		if action != 'ping':
			return rc(rcs.BAD_REQUEST)

		users_dict = request.data.get('users')
		if users_dict:
			UserProfile.objects.filter(id__in=users_dict.keys()).update(
				last_played_server=request.server,
				last_connection_at=datetime.now()
			)
			# TODO save nicknames of logged users
		server = request.server
		server.anonymous_players = request.data.get('anonymous') or ()
		server.played_map = get_object_or_None(Map, name=request.data.get('map'))
		server.save()
		return "PONG"
