from pinax.badges.base import Badge as BadgeBase
from pinax.badges.registry import badges

from lib.brabeion_utils import BadgeDetail


class LabRatBadge(BadgeBase):
    slug = "labrat"
    levels = [BadgeDetail("Lab Rat", "Participate in Teerace closed beta", 200)]
    events = ["logged_in"]
    multiple = False

    def award(self, **state):
        pass


badges.register(LabRatBadge)
