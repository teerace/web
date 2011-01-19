from datetime import datetime
from django.contrib.auth.models import User
from brabeion import badges
from piston.handler import BaseHandler
from piston.utils import require_extended
from accounts.models import UserProfile
from api.forms import ValidateUserForm, ValidateUserTokenForm, SkinUserForm
from race import tasks
from race.forms import RunForm
from race.models import Run, Map, BestRun, Server
from lib.aes import AES
from lib.piston_utils import rc, rcs, validate_mime
from lib.rgb import rgblong_to_hex


class RunHandler(BaseHandler):
	allowed_methods = ('GET', 'POST')
	fields = ('id', 'user', 'map', 'time')
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

	def _read_best(self, request, *args, **kwargs):
		if 'map_name' in kwargs:
			map_obj = Map.objects.get(name=kwargs['map_name'])
			return BestRun.objects.exclude(points=0) \
				.filter(map=map_obj).select_related()[:len(BestRun.SCORING)]
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


		URL
			**/api/1/runs/best/{map_name}/**
		Shortdesc
			Returns [BestRun.SCORING] best results of a map
		Arguments
			- map_name / string / the map name
		Data
			- none
		Result
			- 400 - when the was no map_name specified
			- 200 - when everything went fine
				a list of BestRun objects, which has map, user and run attributes.
		"""
		# without '_read_' prefix
		allowed_actions = ['detail', 'best']
		if action in allowed_actions:
			return getattr(self, '_read_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)

	@require_extended
	@validate_mime(RunForm)
	def _create_new(self, request, *args, **kwargs):
		run = Run(
			map = request.form.map,
			server = request.server,
			user = request.form.user,
			nickname = request.form.cleaned_data['nickname'],
			time = request.form.cleaned_data['time'],
		)
		request.form.user.profile.update_connection(request.server)
		run.save()
		badges.possibly_award_badge("run_finished",
			user=request.form.user, run=run)
		tasks.redo_ranks.delay(run.id)
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
			- map_name / string / name of the finished map
			- user_id / integer / ID of the user who finished the map
			- nickname / string / currently used nickname by the user
			- time / float / user result
			- (optional) no_weapons / bool / Send True when run was finished
				on a map with weapons disabled
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
				return user
			except User.DoesNotExist:
				return rc(rcs.NOT_FOUND)
		return rc(rcs.BAD_REQUEST)

	def _read_profile(self, request, *args, **kwargs):
		if 'id' in kwargs:
			try:
				profile = UserProfile.objects.get(pk=kwargs['id'])
				return profile
			except UserProfile.DoesNotExist:
				return rc(rcs.NOT_FOUND)
		return rc(rcs.BAD_REQUEST)

	def _read_rank(self, request, *args, **kwargs):
		if 'id' in kwargs:
			try:
				profile = UserProfile.objects.get(pk=kwargs['id'])
				return profile.position
			except UserProfile.DoesNotExist:
				return rc(rcs.NOT_FOUND)
		return rc(rcs.BAD_REQUEST)

	def _read_map_rank(self, request, *args, **kwargs):
		if 'id' in kwargs and 'map_name' in kwargs:
			try:
				profile = UserProfile.objects.get(pk=kwargs['id'])
				return profile.map_position(kwargs['map_name'])
			except UserProfile.DoesNotExist:
				return rc(rcs.NOT_FOUND)
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


		URL
			**/api/1/users/map_rank/{id}/{map_name}/**
		Shortdesc
			Returns user global rank.
		Arguments
			- id / integer / ID of the user
			- map_name / string / name of the map
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
	@validate_mime(ValidateUserForm)
	def _create_auth(self, request, *args, **kwargs):
		key = request.server.secret_key
		try:
			password = AES(key).decrypt(request.form.cleaned_data.get('password'))
			user = User.objects.get(username=request.form.cleaned_data.get('username'))
		except (TypeError, User.DoesNotExist):
			return False
		return user if user.check_password(password) else False

	@require_extended
	@validate_mime(ValidateUserTokenForm)
	def _create_auth_token(self, request, *args, **kwargs):
		key = request.server.secret_key
		try:
			user = User.objects.get(
				profile__api_token=request.form.cleaned_data.get('api_token')
			)
		except User.DoesNotExist:
			return False
		return user

	def create(self, request, action, *args, **kwargs):
		"""
		URL
			**/api/1/users/auth/**
		Shortdesc
			Handles user/password checking.
		Longdesc
			Returns User object or False, whether provided
			username and password pass the test.

			Uses AES and base64 to receive password, remember of
			using your server private key to generate cipher.

			Example of password encoding:
				`AES(SECRET_KEY).encrypt(password)`
		Arguments
			- none
		Data
			- username / string
			- password / string / **encrypted** password
		Result
			- 200, when data fails validation
				False
			- 200, when user data are correct
				User object

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

		"""
		allowed_actions = ['auth', 'auth_token']
		if action in allowed_actions:
			return getattr(self, '_create_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)

	@validate_mime(SkinUserForm, 'PUT')
	def _update_skin(self, request, *args, **kwargs):
		if 'id' in kwargs:
			try:
				profile = UserProfile.objects.get(id=kwargs['id'])
				profile.has_skin = True
				form = request.form.cleaned_data
				profile.skin_name = form['skin_name']
				profile.skin_body_color_raw = form['body_color']
				profile.skin_body_color = rgblong_to_hex(form['body_color'])
				profile.skin_feet_color_raw = form['feet_color']
				profile.skin_feet_color = rgblong_to_hex(form['feet_color'])
				profile.save()
				return profile
			except UserProfile.DoesNotExist:
				return rc(rcs.BAD_REQUEST)
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
	fields = ('id', 'name', 'author', 'crc', 'run_count', 'get_download_url')
	model = Map

	@classmethod
	def resource_uri(cls, map_obj=None):
		map_name = 'map_name'
		if map_obj:
			map_name = map_obj.name
			return ('api_maps_detail', [map_name])

	def _read_list(self, request, *args, **kwargs):
		return Map.objects.all()

	def _read_detail(self, request, *args, **kwargs):
		if 'map_name' in kwargs:
			try:
				map_obj = Map.objects.get(pk=kwargs['map_name'])
				return map_obj
			except Map.DoesNotExist:
				return rc(rcs.NOT_FOUND)
		return rc(rcs.BAD_REQUEST)

	def read(self, request, action, *args, **kwargs):
		"""
		URL
			**/api/1/maps/detail/{map_name}/**
		Shortdesc
			Returns an instance of Map.
		Arguments
			- map_name / string / name of the map
		Data
			- none
		Result
			- 404 - when Map with specified map_name doesn't exist
			- 400 - when there was no map_name specified
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
		"""
		# without '_read_' prefix
		allowed_actions = ['list', 'detail']
		if action in allowed_actions:
			return getattr(self, '_read_' + action)(request, *args, **kwargs)
		return rc(rcs.BAD_REQUEST)


class ServerHandler(BaseHandler):
	allowed_methods = ()
	fields = ('id', 'name', 'description')
	model = Server

class PingHandler(BaseHandler):
	"""
	Used to check if server is online.
	
	Updates server and its users last connection time.
	"""

	allowed_methods = ('POST',)

	@require_extended
	def create(self, request):
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
		Result
			- 200 - when everything went fine
				PONG
		"""
		users_dict = request.data.get('users')
		if users_dict:
			del users_dict[0] # let's be certain not to include Anonymous
			UserProfile.objects.filter(id__in=users_dict.keys()).update(
				last_played_server=self.server,
				last_connection_at=datetime.now()
			)
			# TODO save nicknames somewhere
		return "PONG"
