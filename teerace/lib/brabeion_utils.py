from pinax.badges.base import BadgeDetail as BaseBadgeDetail


class BadgeDetail(BaseBadgeDetail):
    def __init__(self, level=None, user=None, points=None):
        super().__init__(level, user)
        self.points = points
