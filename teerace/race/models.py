from zlib import crc32
from django.db import models
from django.contrib.auth.models import User
from lib.file_storage import OverwriteStorage


class Map(models.Model):
	"""Representation of a map played in Teerace"""

	name = models.CharField(max_length=50, unique=True)
	author = models.CharField(max_length=100, blank=True)

	# Just a convention. It should be 'added_at/by', though.
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User)

	def map_filename(self, filename):
		del filename
		return 'uploads/maps/{0}_{1}.map'.format(self.name, self.crc)
	map_file = models.FileField(storage=OverwriteStorage(),
		upload_to=map_filename)
	crc = models.CharField(max_length=8)

	def __unicode__(self):
		return self.name

	def save(self, *args, **kwargs):
		if self.map_file:
			self.crc = '{0:x}'.format(crc32(self.map_file.read()) & 0xffffffff)
			self.map_file.close()
		super(Map, self).save(*args, **kwargs)


class Run(models.Model):
	"""Representation of one map finish"""

	map = models.ForeignKey(Map)
	server = models.ForeignKey('Server', related_name='runs')
	user = models.ForeignKey(User)
	nickname = models.CharField(max_length=24)
	time = models.FloatField()
	reported_at = models.DateTimeField(auto_now_add=True)
	created_at = models.DateTimeField()

	def __unicode__(self):
		return u"{0} - {1} - {2}s".format(self.map, self.user, self.time)


class Server(models.Model):
	"""
	Representation of Teeworlds server hooked up to Teerace
	
	We use maintainer account to interact with API.
	"""

	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	maintained_by = models.ForeignKey(User, related_name='maintained_servers')

	@staticmethod
	def generate_random_key():
		return User.objects.make_random_password(length=32)
	public_key = models.CharField(max_length=32, default=generate_random_key,
		unique=True)
	private_key = models.CharField(max_length=32, default=generate_random_key,
		unique=True)

	def __unicode__(self):
		return self.name
