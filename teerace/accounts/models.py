from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from race.models import Map, Run, BestRun


class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True, related_name='profile')
	registration_ip = models.IPAddressField(blank=True, null=True)
	last_activity_at = models.DateTimeField(auto_now_add=True)
	last_activity_ip = models.IPAddressField(blank=True, null=True)
	points = models.IntegerField(default=0)

	@property
	def completions(self):
		return Run.objects.filter(user=self.user).count()

	@property
	def playtime(self):
		return Run.objects.filter(user=self.user).aggregate(
			Sum('time')
		)['time__sum']

	def best_score(self, map_id):
		try:
			map_obj = Map.objects.get(pk=map_id)
			return BestRun.objects.get(map=map_obj).run
		except (Map.DoesNotExist, BestRun.DoesNotExist):
			return None

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
