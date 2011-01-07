from brabeion import badges
from brabeion.base import Badge as BadgeBase, BadgeAwarded, BadgeDetail
from race.models import Map, Run


class RunCountBadge(BadgeBase):
	slug = 'runcount'
	levels = [
		BadgeDetail("Newcomer", "Finished one run"),
		BadgeDetail("Experienced", "Finished 100 runs"),
		BadgeDetail("Legend", "Finished 1000 runs"),
		BadgeDetail("???", "Finished 5000 runs"),
	]
	events = [
		'run_finished',
	]
	multiple = False

	def award(self, **state):
		user = state['user']
		runs = user.get_profile().completions
		if runs > 5000:
			return BadgeAwarded(level=4)
		if runs > 1000:
			return BadgeAwarded(level=3)
		if runs > 100:
			return BadgeAwarded(level=2)
		return BadgeAwarded(level=1)


class PlaytimeBadge(BadgeBase):
	slug = 'playtime'
	levels = [
		BadgeDetail("Happy Hour", "Accumulate one hour of time played"),
		BadgeDetail("Hang 10", "Accumulate 10 hours of time played"),
		BadgeDetail("Hooked", "Accumulate 24 hours of time played"),
	]
	events = [
		'run_finished',
	]
	multiple = False

	def award(self, **state):
		user = state['user']
		playtime = user.get_profile().playtime
		# a day
		if playtime > 86400:
			return BadgeAwarded(level=3)
		# 10 hours
		if playtime > 36000:
			return BadgeAwarded(level=2)
		# 1 hour
		if playtime > 3600:
			return BadgeAwarded(level=1)


class GlobetrotterBadge(BadgeBase):
	slug = 'globetrotter'
	levels = [
		BadgeDetail("Globetrotter", "Complete 1 run on each map"),
	]
	events = [
		'run_finished',
	]
	multiple = False

	def award(self, **state):
		user = state['user']
		maps = Map.objects.values_list('name', flat=True)
		maps_finished = Run.objects.filter(user=user).values_list('map__name',
			flat=True).distinct()
		# check if maps equals to maps_finished
		if set(maps_finished).issubset(maps):
			return BadgeAwarded(level=1)


badges.register(RunCountBadge)
badges.register(PlaytimeBadge)
badges.register(GlobetrotterBadge)