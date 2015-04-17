from django.contrib.auth.models import User
from django_comments.moderation import CommentModerator, moderator
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from markdown import markdown
from annoying.functions import get_config


class Entry(models.Model):
	created_by = models.ForeignKey(User, on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True)
	published_at = models.DateTimeField(auto_now=True)
	enable_comments = models.BooleanField(default=True)
	is_micro = models.BooleanField(default=False, verbose_name="micro",
		help_text="Designates whether this entry should be displayed as micropost."
			" It will not be included in Teeplanet feed.")
	title = models.CharField(max_length=100)
	slug = models.CharField(max_length=100, blank=True)
	excerpt = models.TextField(blank=True,
		help_text="You may use Markdown syntax")
	excerpt_html = models.TextField(blank=True)
	content = models.TextField(help_text="You may use Markdown syntax")
	content_html = models.TextField()

	PUBLISHED_STATUS = 1
	DRAFT_STATUS = 2
	HIDDEN_STATUS = 3
	STATUS_CHOICES = (
		(PUBLISHED_STATUS, "Published"),
		(DRAFT_STATUS, "Draft"),
		(HIDDEN_STATUS, "Hidden"),
	)
	status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT_STATUS)

	def slugify_title(self):
		new_slug = slug = slugify(self.title) or "bad-title"
		# preventing slugs from being non-unique, wordpress-style
		n = 1
		while True:
			try:
				slug_dupe = Entry.objects.get(slug=new_slug)
			except Entry.DoesNotExist:
				break
			n += 1
			if n != 1:
				new_slug = "{0}-{1}".format(slug, n)
		return new_slug

	class Meta:
		get_latest_by = 'created_at'
		verbose_name_plural = ('Entries')

	def __unicode__(self):
		return self.title

	def save(self, *args, **kwargs):
		self.slug = self.slugify_title()
		if self.is_micro:
			# forcing no excerpt for micro entries
			self.excerpt = self.excerpt_html = ""
		else:
			self.excerpt_html = markdown(self.excerpt)
		self.content_html = markdown(self.content)
		super(Entry, self).save(*args, **kwargs)

	@models.permalink
	def get_absolute_url(self):
		return (
			'blog.views.entry_detail',
			(),
			{'entry_id': self.id, 'slug': self.slug},
		)


class EntryModerator(CommentModerator):
	enable_field = 'enable_comments'

moderator.register(Entry, EntryModerator)
