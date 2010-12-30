from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from race.models import Map, Run, BestRun
from django_countries import CountryField


class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True, related_name='profile')
	registration_ip = models.IPAddressField(blank=True, null=True)
	last_activity_at = models.DateTimeField(auto_now_add=True)
	last_activity_ip = models.IPAddressField(blank=True, null=True)
	country = CountryField(blank=True)
	points = models.IntegerField(default=0)

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
	def playtime(self):
		return Run.objects.filter(user=self.user).aggregate(
			Sum('time')
		)['time__sum']

	@property
	def position(self):
		return User.objects.exclude(profile__points__lte=0) \
			.filter(profile__points__gte=self.points) \
			.order_by('profile__points').count()

	def map_position(self, map_id):
		raise NotImplementedError

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
			'body_color': self.skin_body_color,
			'feet_color': self.skin_feet_color,
		}

	class Meta:
		get_latest_by = 'user__created_at'

	def __unicode__(self):
		possessive = '' if self.user.username.endswith('s') else 's'
		return u"{0}'{1} profile".format(self.user.username, possessive)

	def get_absolute_url(self):
		return self.user.get_absolute_url()


def post_user_save(instance, **kwargs):
	if kwargs['created']:
		# very special case
		if instance.id == 0:
			return
		profile = UserProfile(user=instance)
		profile.save()

post_save.connect(post_user_save, sender=User,
	dispatch_uid='accounts.models')
