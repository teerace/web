from django.contrib.auth.models import User
from brabeion import badges
from piston.handler import BaseHandler
from piston.utils import rc, require_extended
from accounts.models import UserProfile
from api.forms import ValidateUserForm
from race import tasks
from race.forms import RunForm
from race.models import Run, Map, BestRun, Server
from lib.aes import AES
from lib.piston_utils import validate_mime


class RunHandler(BaseHandler):
	"""
	Handles posting of Run objects to webapp.
	"""

	allowed_methods = ('GET', 'POST')
	fields = ('id', 'user', 'map')
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
				return rc.NOT_FOUND
		# FIXME jsonize output
		resp = rc.BAD_REQUEST
		resp.write("'id' parameter missing")
		return resp

	def _read_best(self, request, *args, **kwargs):
		if 'map_name' in kwargs:
			map_obj = Map.objects.get(name=kwargs['map_name'])
			return BestRun.objects.exclude(points=0) \
				.filter(map=map_obj).select_related()[:len(BestRun.SCORING)]

	def read(self, request, action, *args, **kwargs):
		# without '_read_' prefix
		allowed_actions = ['detail', 'best']
		if action in allowed_actions:
			return getattr(self, '_read_' + action)(request, *args, **kwargs)
		# base = Run.objects
		# if id:
		# 	return base.get(pk=id)
		# elif map_name:
		# 	map_obj = Map.objects.get(name=map_name)
		# 	return BestRun.objects.filter(map=map_obj)[:10]
		return rc.BAD_REQUEST


	@require_extended
	@validate_mime(RunForm)
	def create(self, request, action, *args, **kwargs):
		"""
		Creates a Run object.
		Checks for new badges and adds a Celery task to rebuild ranks.
		"""
		if not action == 'new':
			return rc.BAD_REQUEST
		run = Run(
			map = request.form.map,
			server = request.server,
			user = request.form.user,
			nickname = request.form.cleaned_data['nickname'],
			time = request.form.cleaned_data['time'],
		)
		run.save()
		badges.possibly_award_badge("run_finished", user=request.form.user, run=run)
		tasks.redo_ranks.delay(run.id)
		return "Created"


class UserProfileHandler(BaseHandler):
	allowed_methods = ()
	fields = ('points', 'country')
	model = UserProfile


class UserHandler(BaseHandler):
	"""
	Handles user/password checking.
	
	Uses AES and base64 to receive password, remember of
	using your server private key to generate cipher.
	
	Example of password encoding:
		`base64_encode(AES(PRIVATE_KEY).encrypt(password))`
	"""

	allowed_methods = ('GET', 'POST')
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
			return User.objects.get(pk=kwargs['id'])
		return rc.BAD_REQUEST

	def _read_profile(self, request, *args, **kwargs):
		if 'id' in kwargs:
			return UserProfile.objects.get(pk=kwargs['id'])
		return rc.BAD_REQUEST

	def _read_rank(self, request, *args, **kwargs):
		if 'id' in kwargs:
			return UserProfile.objects.get(pk=kwargs['id']).position
		return rc.BAD_REQUEST

	def _read_map_rank(self, request, *args, **kwargs):
		if 'id' in kwargs and 'map_name' in kwargs:
			return UserProfile.objects.get(pk=kwargs['id']) \
				.map_position(kwargs['map_name'])
		return rc.BAD_REQUEST

	def read(self, request, action, *args, **kwargs):
		# without '_read_' prefix
		allowed_actions = ['detail', 'profile', 'rank', 'map_rank']
		if action in allowed_actions:
			return getattr(self, '_read_' + action)(request, *args, **kwargs)

	@require_extended
	@validate_mime(ValidateUserForm)
	def create(self, request, action, *args, **kwargs):
		"""
		Returns User object or False, whether provided
		username and password pass the test.
		"""
		if not action == 'auth':
			return rc.BAD_REQUEST
		key = request.server.private_key
		try:
			password = AES(key).decrypt(request.form.cleaned_data['password'])
			user = User.objects.get(username=request.form.cleaned_data['username'])
		except (TypeError, User.DoesNotExist):
			return False
		return user if user.check_password(password) else False


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
				return rc.NOT_FOUND
		return rc.BAD_REQUEST

	def read(self, request, action, *args, **kwargs):
		# without '_read_' prefix
		allowed_actions = ['list', 'detail']
		if action in allowed_actions:
			return getattr(self, '_read_' + action)(request, *args, **kwargs)


class ServerHandler(BaseHandler):
	allowed_methods = ()
	fields = ('id', 'name', 'description')
	model = Server

class PingHandler(BaseHandler):
	"""
	Used to check if server is online.
	"""

	allowed_methods = ('GET',)

	def read(self, request):
		return "PONG"
