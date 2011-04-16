from django.db import models
from django.db.models import Avg, Sum
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from race.validators import is_map_file, is_demo_file, is_ghost_file
from lib.file_storage import OverwriteStorage
from picklefield.fields import PickledObjectField
from annoying.functions import get_config, get_object_or_None
from actstream import action
from brabeion.signals import badge_awarded


def generate_random_key():
	return User.objects.make_random_password(length=32)


class Map(models.Model):
	"""Representation of a map played in Teerace"""

	name = models.CharField(max_length=50, unique=True)
	author = models.CharField(max_length=100, blank=True)

	added_at = models.DateTimeField(auto_now_add=True)
	added_by = models.ForeignKey(User, on_delete=models.PROTECT)

	def map_filename(self, filename):
		del filename
		return 'uploads/maps/{0}.map'.format(self.name)
	map_file = models.FileField(storage=OverwriteStorage(),
		upload_to=map_filename, validators=[is_map_file])
	crc = models.CharField(max_length=8, blank=True, null=True)

	map_type = models.ForeignKey('MapType', default=1,
		on_delete=models.SET_DEFAULT)

	has_unhookables = models.NullBooleanField(default=False)
	has_deathtiles = models.NullBooleanField(default=False)
	has_teleporters = models.NullBooleanField(default=False)
	has_speedups = models.NullBooleanField(default=False)
	shield_count = models.IntegerField(default=0, null=True)
	heart_count = models.IntegerField(default=0, null=True)
	grenade_count = models.IntegerField(default=0, null=True)
	has_image = models.BooleanField(default=False)

	# def get_map_image(self):
	# 	return "{0}images/maps/full/{1}.png".format(settings.MEDIA_ROOT,
	# 		self.name) if self.has_image else None

	download_count = models.IntegerField(default=0)

	@property
	def run_count(self):
		return Run.objects.filter(map=self).count()

	@property
	def total_runtime(self):
		return Run.objects.filter(map=self).aggregate(Sum('time'))['time__sum']

	@property
	def average_score(self):
		return Run.objects.filter(map=self).aggregate(Avg('time'))['time__avg']

	@property
	def best_score(self):
		return self.get_best_score()

	def get_best_score(self):
		try:
			return BestRun.objects.filter(map=self)[0].run
		except IndexError:
			return None

	def get_download_url(self):
		return self.map_file.url

	def __unicode__(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('race.views.map_detail', (), {'map_id': self.id})


class MapType(models.Model):
	slug = models.SlugField(max_length=20)
	displayed_name = models.CharField(max_length=50)
	description = models.TextField(blank=True)

	def __unicode__(self):
		return self.displayed_name

	def save(self, *args, **kwargs):
		self.slug = slugify(self.displayed_name)
		super(MapType, self).save(*args, **kwargs)


class Run(models.Model):
	"""Representation of one map finish"""

	map = models.ForeignKey('Map', on_delete=models.CASCADE)
	server = models.ForeignKey('Server', blank=True, null=True,
		related_name='runs', on_delete=models.SET_NULL)
	user = models.ForeignKey(User, blank=True, null=True,
		on_delete=models.SET_NULL)
	nickname = models.CharField(max_length=15)
	clan = models.CharField(max_length=11, blank=True)

	# yep, 24 semicolons and 25 time decimals,
	# which length is MAX_DIGITS + decimal separator (.)
	# 24 + 25 * (12 + 1) = 349
	checkpoints = models.CharField(max_length=349, blank=True)

	DECIMAL_PLACES = get_config('RESULT_PRECISION', 3)
	MAX_DIGITS = DECIMAL_PLACES + 9

	time = models.DecimalField(max_digits=MAX_DIGITS,
		decimal_places=DECIMAL_PLACES)
	created_at = models.DateTimeField(auto_now_add=True)

	def set_personal_record(self):
		try:
			current_best = BestRun.objects.get(map=self.map, user=self.user)
			if self.time < current_best.run.time:
				self.promote_to_best()
		except BestRun.DoesNotExist:
			self.promote_to_best()

	def promote_to_best(self):
		if self.user == None:
			return
		best_run, created = BestRun.objects.get_or_create(map=self.map,
			user=self.user, defaults={'run': self})
		if not created:
			best_run.run = self
			best_run.save()

	def checkpoints_list(self):
		return self.checkpoints.split(';')

	class Meta:
		get_latest_by = 'created_at'
		ordering = ['time', 'created_at']

	def __unicode__(self):
		return u"{0} - {1} - {2:.{precision}f}s".format(self.map, self.user,
			self.time, precision=self.DECIMAL_PLACES)

	def save(self, *args, **kwargs):
		# imitate overriding create()
		created = True if not self.pk else False
		super(Run, self).save(*args, **kwargs)
		if created:
			self.set_personal_record()

	def delete(self, *args, **kwargs):
		self.server_set.clear()
		super(Map, self).delete(*args, **kwargs)


class BestRun(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	map = models.ForeignKey('Map', on_delete=models.CASCADE)
	run = models.ForeignKey('Run', on_delete=models.CASCADE)

	# UGLY hack to make rank rebuilding relatively easy
	time = models.DecimalField(max_digits=Run.MAX_DIGITS,
		decimal_places=Run.DECIMAL_PLACES)

	#SCORING = (20, 14, 10, 8, 6, 5, 4, 3, 2, 1)
	#          40  34  31    27, 26...3, 2, 1
	SCORING = (40, 34, 31) + tuple(range(27, 0, -1))
	points = models.IntegerField(default=0)

	def demo_filename(self, filename):
		del filename
		return 'uploads/demos/m{0}_u{1}.demo'.format(self.map_id, self.user_id)
	demo_file = models.FileField(blank=True, null=True,
		storage=OverwriteStorage(), upload_to=demo_filename,
		validators=[is_demo_file])

	def ghost_filename(self, filename):
		del filename
		return 'uploads/ghosts/m{0}_u{1}.demo'.format(self.map_id, self.user_id)
	ghost_file = models.FileField(blank=True, null=True,
		storage=OverwriteStorage(), upload_to=ghost_filename,
		validators=[is_ghost_file])

	def get_demo_url(self):
		return self.demo_file.url

	def get_ghost_url(self):
		return self.ghost_file.url

	class Meta:
		unique_together = ('user', 'map')
		ordering = ['time', 'run__created_at']

	def __unicode__(self):
		return repr(self.run)

	def save(self, *args, **kwargs):
		was_run_id = get_object_or_None(BestRun, user=self.user, map=self.map)
		if was_run_id:
			was_run_id = was_run_id.run_id
		new_run_id = self.run_id
		self.time = self.run.time
		super(BestRun, self).save(*args, **kwargs)
		if was_run_id != new_run_id:
			if self.run == self.map.best_score:
				action.send(self.user, verb='broke the record on',
					target=self.map)
			else:
				action.send(self.user, verb='broke his best score on',
					target=self.map)


class Server(models.Model):
	"""
	Representation of Teeworlds server hooked up to Teerace

	We use maintainer account to interact with API.
	"""

	name = models.CharField(max_length=100, verbose_name="server name")
	description = models.TextField(blank=True)
	address = models.CharField(max_length=50, blank=True)
	maintained_by = models.ForeignKey(User, related_name='maintained_servers',
		verbose_name="maintainer", on_delete=models.PROTECT)
	is_active = models.BooleanField(default=True, verbose_name="active",
		help_text="Designates whether this server should be treated as active."
			" Unselect this instead of deleting servers.")
	last_connection_at = models.DateTimeField(auto_now=True)
	played_map = models.ForeignKey(Map, null=True, blank=True, on_delete=models.SET_NULL)
	anonymous_players = PickledObjectField()
	api_key = models.CharField(max_length=32, unique=True)

	def __unicode__(self):
		return self.name

	def regenerate_api_key(self):
		new_key = generate_random_key()
		self.api_key = new_key
		self.save()
		return new_key

	def save(self, *args, **kwargs):
		if not self.pk:
			self.api_key = generate_random_key()
		super(Server, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		self.players.clear()
		super(Server, self).delete(*args, **kwargs)


def post_badge_save(sender, **kwargs):
	badge = kwargs['badge_award']
	action.send(badge.user, verb='earned achievement {0}'.format(badge.name),
		action_object=badge)

badge_awarded.connect(post_badge_save)


# DIRTY is this even allowed?
from race import badges
