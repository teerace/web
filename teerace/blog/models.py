from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from markdown import markdown
from threadedcomments.models import ThreadedComment, DEFAULT_MAX_COMMENT_DEPTH


class Entry(models.Model):
	created_by = models.ForeignKey(User)
	created_at = models.DateTimeField(auto_now_add=True)
	is_published = models.BooleanField(default=False)
	title = models.CharField(max_length=100)
	excerpt = models.TextField(blank=True)
	excerpt_html = models.TextField(blank=True)
	content = models.TextField()
	content_html = models.TextField()

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


def post_comment_save(instance, **kwargs):
	if kwargs['created']:
		i = 0
		c = instance.parent
		while c != None:
			c = c.parent
			i = i + 1
			if i > DEFAULT_MAX_COMMENT_DEPTH:
				instance.parent = instance.parent.parent
				instance.save()
				return
		
post_save.connect(post_comment_save, sender=ThreadedComment,
	dispatch_uid='accounts.models')