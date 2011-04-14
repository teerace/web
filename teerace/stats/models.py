from datetime import date
from django.db import models
from django.template.defaultfilters import slugify
from picklefield.fields import PickledObjectField


class Chart(models.Model):
	displayed_name = models.CharField(max_length=30)
	description = models.TextField()
	slug = models.SlugField(max_length=30, unique=True)
	data = PickledObjectField(null=True)

	def update(self, new_data, timestamp=None):
		if not self.data:
			self.data = []
		timestamp = date.today() if not timestamp else timestamp
		self.data.append((timestamp, new_data))
		self.save()

	def __unicode__(self):
		return u"Chart {0}".format(displayed_name)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.displayed_name)
		super(Chart, self).save(*args, **kwargs)
