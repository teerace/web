from django.views.generic.list_detail import object_list, object_detail
from blog.models import Entry


def entry_list(request):
	entries = Entry.objects.exclude(is_published=False) \
		.order_by('-created_at').select_related()
	return object_list(request, queryset=entries, template_object_name='entry')


def entry_detail(request, entry_id):
	entries = Entry.objects.exclude(is_published=False) \
		.order_by('-created_at').select_related()
	return object_detail(request, queryset=entries, object_id=entry_id,
		template_object_name='entry')
