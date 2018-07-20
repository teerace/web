from datetime import date, timedelta

from django.db import models
from django.template.defaultfilters import slugify
from picklefield.fields import PickledObjectField


class Chart(models.Model):
    displayed_name = models.CharField(max_length=30)
    description = models.TextField()
    slug = models.SlugField(max_length=30, unique=True)
    data = PickledObjectField(null=True)

    def append(self, new_data, timestamp=None):
        yesterday = date.today() - timedelta(1)
        if not self.data:
            self.data = []
        elif not timestamp:
            if self.data[-1][0] == yesterday:
                # making sure we save only one time per day
                # unless timestamp is specified
                return
        timestamp = yesterday if not timestamp else timestamp
        self.data.append((timestamp, new_data))
        self.save()

    def __str__(self):
        return "Chart {0}".format(self.displayed_name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.displayed_name)
        super().save(*args, **kwargs)
