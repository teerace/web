from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from blog.models import Entry


class LatestEntriesFeed(Feed):
	feed_type = Atom1Feed
	title = "Teerace blog"
	link = "/blog/"
	subtitle = "Updates on changes and additions to Teerace."

	def items(self):
		return Entry.objects.exclude(is_published=False) \
			.order_by('-created_at')[:5]

	def item_title(self, item):
		return item.title

	def item_link(self, item):
		return item.get_absolute_url()

	def item_description(self, item):
		return item.content_html

	def item_author_name(self, item):
		return item.created_by

	def item_pubdate(self, item):
		return item.created_at