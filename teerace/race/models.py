from django.db import models
from django.db.models import Avg, Sum
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from race.validators import is_map_file
from lib.file_storage import OverwriteStorage
from picklefield.fields import PickledObjectField
from annoying.functions import get_config


def generate_random_key():
	return User.objects.make_random_password(length=32)


class Map(models.Model):
	"""Representation of a map played in Teerace"""

	name = models.CharField(max_length=50, unique=True)
	author = models.CharField(max_length=100, blank=True)

	added_at = models.DateTimeField(auto_now_add=True)
	added_by = models.ForeignKey(User)

	def map_filename(self, filename):
		del filename
		return 'uploads/maps/{0}.map'.format(self.name)
	map_file = models.FileField(storage=OverwriteStorage(),
		upload_to=map_filename, validators=[is_map_file])
	crc = models.CharField(max_length=8, blank=True, null=True)

	map_type = models.ForeignKey('MapType', default=1)

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
	def total_playtime(self):
		return Run.objects.filter(map=self).aggregate(Sum('time'))['time__sum']

	@property
	def average_score(self):
		return Run.objects.filter(map=self).aggregate(Avg('time'))['time__avg']

	@property
	def best_score(self):
		try:
			return BestRun.objects.get(user=self, map=self).run
		except BestRun.DoesNotExist:
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

	def __unicode__(self):
		return self.displayed_name

	def save(self, *args, **kwargs):
		self.slug = slugify(self.displayed_name)
		super(MapType, self).save(*args, **kwargs)


class Run(models.Model):
	"""Representation of one map finish"""

	map = models.ForeignKey('Map')
	server = models.ForeignKey('Server', related_name='runs')
	user = models.ForeignKey(User, blank=True, null=True)
	nickname = models.CharField(max_length=24)

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
		if created:
			best_run.run = self
			best_run.save()

	def checkpoints_list(self):
		return self.checkpoints.split(';')

	def __unicode__(self):
		return u"{0} - {1} - {2:.{precision}f}s".format(self.map, self.user,
			self.time, precision=get_config('RESULT_PRECISION', 3))

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
	user = models.ForeignKey(User)
	map = models.ForeignKey('Map')
	run = models.ForeignKey('Run')

	# UGLY hack to make rank rebuilding relatively easy
	time = models.FloatField()

	#SCORING = (20, 14, 10, 8, 6, 5, 4, 3, 2, 1)
	#          40  34  31    27, 26...3, 2, 1
	SCORING = (40, 34, 31) + tuple(range(27, 0, -1))
	points = models.IntegerField(default=0)

	class Meta:
		unique_together = ('user', 'map')

	def __unicode__(self):
		return repr(self.run)

	def save(self, *args, **kwargs):
		self.time = self.run.time
		super(BestRun, self).save(*args, **kwargs)


class Server(models.Model):
	"""
	Representation of Teeworlds server hooked up to Teerace

	We use maintainer account to interact with API.
	"""

	name = models.CharField(max_length=100, verbose_name="server name")
	description = models.TextField(blank=True)
	address = models.CharField(max_length=50, blank=True)
	maintained_by = models.ForeignKey(User, related_name='maintained_servers',
		verbose_name="maintainer")
	is_active = models.BooleanField(default=True, verbose_name="active",
		help_text="Designates whether this server should be treated as active."
			" Unselect this instead of deleting servers.")
	last_connection_at = models.DateTimeField(auto_now=True)
	played_map = models.ForeignKey(Map, null=True, blank=True)
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


# DIRTY is this even allowed?
from race import badges
