from .models import Entry


def latest_entries():
    try:
        entries = (
            Entry.objects.filter(status=Entry.PUBLISHED_STATUS)
            .order_by("-created_at")
            .select_related()[:2]
        )

        if entries.count() > 1 and not entries[0].is_micro and not entries[1].is_micro:
            entries = entries[:1]
    except Entry.DoesNotExist:
        entries = None
    return entries
