from django.conf import settings
from django.utils.translation import ugettext_lazy as _


DRAFTED = getattr(settings, "FAQ_DRAFTED", 1)
PUBLISHED = getattr(settings, "FAQ_PUBLISHED", 2)
REMOVED = getattr(settings, "FAQ_REMOVED", 3)

STATUS_CHOICES = (
    (DRAFTED, _("drafted")),
    (PUBLISHED, _("published")),
    (REMOVED, _("removed")),
)
STATUS_CHOICES = getattr(settings, "FAQ_STATUS_CHOICES", STATUS_CHOICES)
