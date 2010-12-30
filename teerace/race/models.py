from django.db import models
from django.db.models import Avg, Sum
from django.contrib.auth.models import User
from race.validators import is_map_file
from lib.file_storage import OverwriteStorage


def generate_random_key():
	return User.objects.make_random_password(length=32)


class Map(models.Model):
	"""Representation of a map played in Teerace"""

	name = models.CharField(max_length=50, unique=True)
	created_by = models.CharField(max_length=100, blank=True)

	added_at = models.DateTimeField(auto_now_add=True)
	added_by = models.ForeignKey(User)

	def map_filename(self, filename):
		del filename
		return 'uploads/maps/{0}.map'.format(self.name)
	map_file = models.FileField(storage=OverwriteStorage(),
		upload_to=map_filename, validators=[is_map_file])
	crc = models.CharField(max_length=8)

	has_unhookables = models.BooleanField(default=False)
	has_deathtiles = models.BooleanField(default=False)
	shield_count = models.IntegerField(default=0)
	heart_count = models.IntegerField(default=0)
	grenade_count = models.IntegerField(default=0)
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
			return Run.objects.get(map=self, is_record=True)
		except Run.DoesNotExist:
			return None

	def get_download_url(self):
		return self.map_file.url

	def __unicode__(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('race.views.map_detail', (), {'map_id': self.id})


class Run(models.Model):
	"""Representation of one map finish"""

	map = models.ForeignKey(Map)
	server = models.ForeignKey('Server', related_name='runs')
	user = models.ForeignKey(User)
	nickname = models.CharField(max_length=24)
	time = models.FloatField()
	created_at = models.DateTimeField(auto_now_add=True)

	# denormalised data, also gives us primitive object history
	is_personal_best = models.BooleanField(default=False)
	was_personal_best = models.BooleanField(default=False)
	is_record = models.BooleanField(default=False)
	was_record = models.BooleanField(default=False)
	diff_from_personal_best = models.FloatField(default=0.0)

	def set_personal_record(self):
		try:
			current_pb = Run.objects.get(map=self.map, user=self.user,
				is_personal_best=True)
			if self.time < current_pb.time:
				self.is_personal_best = True
				current_pb.set_was_pb()
			self.diff_from_personal_best = self.time - current_pb.time
		except Run.DoesNotExist:
			self.is_personal_best = True
		except Run.MultipleObjectsReturned:
			self.clear_pb()

	def set_was_pb(self):
		self.is_personal_best = False
		self.was_personal_best = True
		self.save()

	def clear_pb(self):
		broken_qs = Run.objects.filter(map=self.map, user=self.user,
			is_personal_best=True).order_by('time')
		broken_qs.exclude(pk=broken_qs[0].id).update(is_personal_best=False)

	def set_map_record(self):
		try:
			current_record = Run.objects.get(map=self.map, is_record=True)
			if self.time < current_record.time:
				self.is_record = True
				current_record.set_was_record()
		except Run.DoesNotExist:
			self.is_record = True
		except Run.MultipleObjectsReturned:
			self.clear_record()

	def set_was_record(self):
		self.is_record = False
		self.was_record = True
		self.save()

	def clear_record(self):
		broken_qs = Run.objects.filter(map=self.map,
			is_record=True).order_by('time')
		broken_qs.exclude(pk=broken_qs[0].id).update(is_record=False)

	def promote_to_best(self):
		best_run, created = BestRun.objects.get_or_create(map=self.map,
			user=self.user, defaults={'run': self})
		if not created:
			best_run.run = self
			best_run.save()

	def __unicode__(self):
		return u"{0} - {1} - {2:.2f}s".format(self.map, self.user, self.time)

	def save(self, *args, **kwargs):
		# imitate overriding create()
		create = True if not self.pk else False
		if create:
			self.set_personal_record()
			# we don't want anonymous users to own map records
			if self.user.id != 0:
				self.set_map_record()
		super(Run, self).save(*args, **kwargs)
		if create and self.is_personal_best:
			self.promote_to_best()


class BestRun(models.Model):
	user = models.ForeignKey(User)
	map = models.ForeignKey(Map)
	run = models.ForeignKey(Run)

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

	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	maintained_by = models.ForeignKey(User, related_name='maintained_servers')
	last_connection_at = models.DateTimeField(auto_now=True)
	public_key = models.CharField(max_length=32, default=generate_random_key,
		unique=True)
	private_key = models.CharField(max_length=32, default=generate_random_key,
		unique=True)

	def __unicode__(self):
		return self.name

	def _regenerate_key(self, field_name):
		if not field_name in ('public_key', 'private_key'):
			raise ValueError("_regenerate_key() can only be used with"
				" public_key/private_key fields")
		new_key = generate_random_key()
		setattr(self, field_name, new_key)
		self.save()
		return new_key

	def regenerate_public_key(self):
		return self._regenerate_key('public_key')

	def regenerate_private_key(self):
		return self._regenerate_key('private_key')


# DIRTY is this even allowed?
from race import badges
