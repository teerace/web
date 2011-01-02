from django.views.generic.list_detail import object_list, object_detail
from blog.models import Entry
from annoying.functions import get_config


def entry_list(request):
	entries = Entry.objects.exclude(is_published=False) \
		.order_by('-created_at').select_related()
	return object_list(request, queryset=entries, template_object_name='entry',
		paginate_by=get_config('ITEMS_PER_PAGE', 20))


def entry_detail(request, entry_id):
	entries = Entry.objects.exclude(is_published=False) \
		.order_by('-created_at').select_related()
	return object_detail(request, queryset=entries, object_id=entry_id,
		template_object_name='entry')
