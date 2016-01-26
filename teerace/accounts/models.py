from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from race.models import Map, Run, BestRun
from django_countries.fields import CountryField
from picklefield.fields import PickledObjectField
from actstream import action


def generate_random_key():
	return User.objects.make_random_password(length=24)


class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True, related_name='profile')
	api_token = models.CharField(max_length=24, unique=True)
	registration_ip = models.GenericIPAddressField(blank=True, null=True)
	last_connection_at = models.DateTimeField(auto_now_add=True)
	last_played_server = models.ForeignKey('race.Server', blank=True, null=True,
		related_name='players', on_delete=models.SET_NULL)
	country = CountryField(blank=True)
	points = models.IntegerField(default=0)
	points_history = PickledObjectField(null=True)
	# points snapshot from 4:30 AM, not really precise, but who cares?
	yesterday_points = models.IntegerField(default=0)
	playtime = models.IntegerField(default=0)

	UNKNOWN_GENDER = 1
	MALE_GENDER = 2
	FEMALE_GENDER = 3
	GENDER_CHOICES = (
		(UNKNOWN_GENDER, "Unknown"),
		(MALE_GENDER, "Male"),
		(FEMALE_GENDER, "Female"),
	)
	gender = models.IntegerField(choices=GENDER_CHOICES, default=UNKNOWN_GENDER,
		blank=True)

	has_skin = models.BooleanField(default=False)
	skin_name = models.CharField(max_length=40, blank=True)
	skin_body_color = models.CharField(max_length=7, blank=True)
	skin_feet_color = models.CharField(max_length=7, blank=True)
	skin_body_color_raw = models.IntegerField(max_length=8, blank=True, null=True)
	skin_feet_color_raw = models.IntegerField(max_length=8, blank=True, null=True)

	@property
	def completions(self):
		return Run.objects.filter(user=self.user).count()

	@property
	def runtime(self):
		return Run.objects.filter(user=self.user).aggregate(
			Sum('time')
		)['time__sum']

	@property
	def points_progress(self):
		# points progress since yesterday (actually: since 4:30 AM)
		return "{0:+d}".format(self.points - self.yesterday_points)

	@property
	def position(self):
		if self.points <= 0:
			return None
		return User.objects.exclude(is_active=False) \
			.filter(profile__points__gt=self.points) \
			.order_by('profile__points').count()+1

	def is_female(self):
		return self.gender == self.FEMALE_GENDER

	def map_position(self, map_id):
		# first, retrieve player's map time
		try:
			map_obj = Map.objects.get(pk=map_id)
			player_time = BestRun.objects.get(map=map_obj, user=self.user).time
		except (Map.DoesNotExist, BestRun.DoesNotExist):
			return None
		# now, count all players with lower time and add 1 representing this player
		return BestRun.objects.filter(map=map_obj) \
			.exclude(user__is_active=False) \
			.filter(time__lt=player_time).count() + 1

	def update_playtime(self, seconds):
		if seconds <= 0:
			return
		self.playtime = self.playtime + seconds
		self.save()

	def update_connection(self, server):
		self.last_connection_at = datetime.now()
		self.last_played_server = server
		self.save()

	def is_online(self):
		return self.last_connection_at >= datetime.now()-timedelta(minutes=10)

	def playing_on(self):
		return self.last_played_server if self.is_online() else None

	def best_score(self, map_id):
		try:
			map_obj = Map.objects.get(pk=map_id)
			return BestRun.objects.get(map=map_obj, user=self.user).run
		except (Map.DoesNotExist, BestRun.DoesNotExist):
			return None

	SKIN_LIST = (
		'bluekitty', 'bluestripe', 'brownbear', 'cammo',
		'cammostripes', 'coala', 'default', 'limekitty',
		'pinky', 'redbopp', 'redstripe', 'saddo', 'toptri',
		'twinbop', 'twintri', 'warpaint'
	)

	def get_skin(self):
		if not self.has_skin:
			return None
		return {
			'url': '{0}images/skins/{1}.png'.format(settings.MEDIA_URL, self.skin_name),
			'body_color': self.skin_body_color_raw,
			'feet_color': self.skin_feet_color_raw,
		}

	def regenerate_token(self):
		self.api_token = generate_random_key()
		self.save()

	class Meta:
		get_latest_by = 'user__created_at'
		ordering = ['id']

	def __unicode__(self):
		possessive = '' if self.user.username.endswith('s') else 's'
		return u"{0}'{1} profile".format(self.user.username, possessive)

	def get_absolute_url(self):
		return self.user.get_absolute_url()


def post_user_save(instance, **kwargs):
	if kwargs['created']:
		profile = UserProfile(
			user=instance,
			api_token=generate_random_key()
		)
		profile.save()
		action.send(instance, verb='has registered')

post_save.connect(post_user_save, sender=User,
	dispatch_uid='accounts.models')


# DIRTY is this even allowed?
from accounts import badges
