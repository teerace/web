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

	@property
	def points(self):
		return BestRun.objects.filter(user=self).aggregate(
			Sum('points')
		)['points__sum']

	def best_score(self, map_id):
		try:
			map_obj = Map.objects.get(pk=map_id)
			return BestRun.objects.get(map=map_obj).run
		except (Map.DoesNotExist, BestRun.DoesNotExist):
			return None

	class Meta:
		get_latest_by = 'user__created_at'

	def __unicode__(self):
		return u"{0}'s profile".format(self.user.username)


def post_user_save(instance, **kwargs):
	if kwargs['created']:
		profile = UserProfile(user=instance)
		profile.save()

post_save.connect(post_user_save, sender=User,
	dispatch_uid='accounts.models')
