from django.contrib.auth.models import User
from django.db import models
import caching.base
from markdown import markdown


class Entry(caching.base.CachingMixin, models.Model):
	created_by = models.ForeignKey(User)
	created_at = models.DateTimeField(auto_now_add=True)
	is_published = models.BooleanField(default=False)
	title = models.CharField(max_length=100)
	excerpt = models.TextField(blank=True)
	excerpt_html = models.TextField(blank=True)
	content = models.TextField()
	content_html = models.TextField()

	objects = caching.base.CachingManager()

	class Meta:
		get_latest_by = 'created_at'
		verbose_name_plural = ('Entries')

	def __unicode__(self):
		return self.title

	def save(self, *args, **kwargs):
		self.excerpt_html = markdown(self.excerpt)
		self.content_html = markdown(self.content)
		super(Entry, self).save(*args, **kwargs)

	@models.permalink
	def get_absolute_url(self):
		return ('blog.views.entry_detail', (), {'entry_id': self.id})
