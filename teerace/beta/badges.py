from brabeion import badges
from brabeion.base import Badge as BadgeBase, BadgeAwarded
from lib.brabeion_utils import BadgeDetail
from annoying.functions import get_config


class LabRatBadge(BadgeBase):
	slug = 'labrat'
	levels = [
		BadgeDetail("Lab Rat", "Participate in Teerace closed beta", 200),
	]
	events = [
		'logged_in',
	]
	multiple = False

	def award(self, **state):
		if get_config('BETA', False):
			return BadgeAwarded(level=1)


badges.register(LabRatBadge)
