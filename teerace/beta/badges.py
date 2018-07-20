from annoying.functions import get_config
from pinax.badges.base import Badge as BadgeBase
from pinax.badges.base import BadgeAwarded
from pinax.badges.registry import badges

from lib.brabeion_utils import BadgeDetail


class LabRatBadge(BadgeBase):
    slug = "labrat"
    levels = [BadgeDetail("Lab Rat", "Participate in Teerace closed beta", 200)]
    events = ["logged_in"]
    multiple = False

    def award(self, **state):
        if get_config("BETA", False):
            return BadgeAwarded(level=1)


badges.register(LabRatBadge)
