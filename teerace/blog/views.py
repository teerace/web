from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from blog.models import Entry
from annoying.decorators import render_to


def entry_list(request):
	entries = Entry.objects.exclude(is_published=False) \
		.order_by('-created_at').select_related()
	return object_list(request, queryset=entries, template_object_name='entry')


@render_to('blog/entry_detail.html')
def entry_detail(request, entry_id, slug=None):
	entry = get_object_or_404(
		Entry.objects.exclude(is_published=False).select_related(),
		pk=entry_id
	)
	return {
		'entry': entry,
	}
