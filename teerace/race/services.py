from contextlib import suppress
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count, Sum
from pinax.badges.models import BadgeAward
from pinax.badges.registry import badges

from .models import Map, Run


def get_latest_map():
    with suppress(Map.DoesNotExist):
        return Map.objects.latest("id")


def get_map_count():
    return Map.objects.count()


def get_total_downloads():
    return Map.objects.aggregate(Sum("download_count"))["download_count__sum"] or 0


def get_date_run_count(date_):
    return Run.objects.filter(
        created_at__range=(date_, date_ + timedelta(days=1))
    ).count()


def get_yesterday_run_count():
    value = cache.get("runs_yesterday_count")
    if value is None:
        from .tasks import update_yesterday_runs

        update_yesterday_runs.apply()
        value = cache.get("runs_yesterday_count")
    return value


def get_cached_totals():
    keys = ["total_runs", "total_runtime", "total_playtime"]
    values = cache.get_many(keys)
    if set(keys) != set(values):
        from .tasks import update_totals

        update_totals.apply()
        values = cache.get_many(keys)
    return values


def get_user_badges(user):
    if not user.is_authenticated:
        return []
    return set(
        (slug, level)
        for slug, level in BadgeAward.objects.filter(user=user).values_list(
            "slug", "level"
        )
    )


class GetBadges:
    user_badges = None
    user_count = None
    badge_counts = None

    def __call__(self, user_badges, user_count):
        self.user_badges = user_badges
        self.user_count = user_count
        self.badge_counts = self.get_counts()
        return [self.get_info(*params) for params in self.get_registered_badges()]

    def get_registered_badges(self):
        for badge_cls in badges._registry.values():
            for level, badge in enumerate(badge_cls.levels):
                yield (badge_cls, level, badge)

    def get_counts(self):
        badges_awarded = BadgeAward.objects.values("slug", "level").annotate(
            num=Count("pk")
        )
        return {
            self.get_slug(badge["slug", badge["level"]]): badge["num"]
            for badge in badges_awarded
        }

    def get_slug(self, badge_slug, level):
        return f"{badge_slug}_{level}"

    def get_count(self, badge_cls, level):
        return self.badge_counts.get(self.get_slug(badge_cls.slug, level), 0)

    def get_percentage(self, badge_cls, level):
        count = self.get_count(badge_cls, level)
        if self.user_count:
            return count / self.user_count * 100
        return 0

    def user_has_badge(self, badge_cls, level):
        return (badge_cls.slug, level) in self.user_badges

    def get_info(self, badge_cls, level, badge):
        return {
            "slug": badge_cls.slug,
            "level": level,
            "name": badge.name,
            "description": badge.description,
            "count": self.get_count(badge_cls, level),
            "percentage": self.get_percentage(badge_cls, level),
            "user_has": self.user_has_badge(badge_cls, level),
        }


get_badges = GetBadges()
