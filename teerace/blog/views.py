from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from blog.models import Entry
from annoying.decorators import render_to


def entry_list(request):
	entries = Entry.objects.filter(status=Entry.PUBLISHED_STATUS) \
		.order_by('-created_at').select_related()
	list_view = ListView.as_view(template_name='blog/entry_list.html', queryset=entries, context_object_name='entry_list')
	return list_view(request)


@render_to('blog/entry_detail.html')
def entry_detail(request, entry_id, slug=None):
	if request.user.is_staff or request.user.is_superuser:
		entries = Entry.objects.exclude(status=Entry.HIDDEN_STATUS)
	else:
		entries = Entry.objects.filter(status=Entry.PUBLISHED_STATUS)
	entry = get_object_or_404(
		entries.select_related(),
		pk=entry_id
	)
	return {
		'entry': entry,
	}
