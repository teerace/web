from brabeion.base import BadgeDetail as BaseBadgeDetail

class BadgeDetail(BaseBadgeDetail):
    def __init__(self, level=None, user=None, points=None):
		super(BadgeDetail, self).__init__(level, user)
		self.points = points
		