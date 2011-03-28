from brabeion import badges
from brabeion.base import Badge as BadgeBase, BadgeAwarded
from lib.brabeion_utils import BadgeDetail


class MinionBadge(BadgeBase):
	slug = 'minion'
	levels = [
		BadgeDetail("Teerace Minion", "Teerace staff member", 200),
	]
	events = [
		'logged_in',
	]
	multiple = False

	def award(self, **state):
		user = state['user']
		if user.is_staff or user.is_superuser:
			return BadgeAwarded(level=1)


badges.register(MinionBadge)
