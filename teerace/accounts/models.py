from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True, related_name='profile')
	# workaround for get_latest_by (I'd love to use user's attr)
	created_at = models.DateTimeField(auto_now_add=True)
	registration_ip = models.IPAddressField(blank=True, null=True)
	last_activity_at = models.DateTimeField(auto_now_add=True)
	last_activity_ip = models.IPAddressField(blank=True, null=True)

	class Meta:
		get_latest_by = 'created_at'

	def __unicode__(self):
		return u"{0}'s profile".format(self.user.username)


def post_user_save(instance, **kwargs):
	if kwargs['created']:
		profile = UserProfile(user=instance)
		profile.save()

post_save.connect(post_user_save, sender=User,
	dispatch_uid='accounts.models')
