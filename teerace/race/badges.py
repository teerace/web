from decimal import Decimal

from pinax.badges.base import Badge as BadgeBase
from pinax.badges.base import BadgeAwarded
from pinax.badges.registry import badges

from lib.brabeion_utils import BadgeDetail

from .models import Map, Run


class RunCountBadge(BadgeBase):
    slug = "runcount"
    levels = [
        BadgeDetail("Newcomer", "Finish one run", 10),
        BadgeDetail("Experienced", "Finish 100 runs", 30),
        BadgeDetail("Legend", "Finish 1000 runs", 70),
        BadgeDetail("???", "Finish 5000 runs", 200),
    ]
    events = ["run_finished"]
    multiple = False

    def award(self, **state):
        user = state["user"]
        runs = user.profile.completions
        if runs > 5000:
            return BadgeAwarded(level=4)
        if runs > 1000:
            return BadgeAwarded(level=3)
        if runs > 100:
            return BadgeAwarded(level=2)
        return BadgeAwarded(level=1)


class RuntimeBadge(BadgeBase):
    slug = "runtime"
    levels = [
        BadgeDetail("Happy Hour", "Accumulate one hour of time played", 10),
        BadgeDetail("Hang 10", "Accumulate 10 hours of time played", 30),
        BadgeDetail("Hooked", "Accumulate 24 hours of time played", 70),
    ]
    events = ["run_finished"]
    multiple = False

    def award(self, **state):
        user = state["user"]
        runtime = user.profile.runtime
        # a day
        if runtime > 86400:
            return BadgeAwarded(level=3)
            # 10 hours
        if runtime > 36000:
            return BadgeAwarded(level=2)
            # 1 hour
        if runtime > 3600:
            return BadgeAwarded(level=1)


class GlobetrotterBadge(BadgeBase):
    slug = "globetrotter"
    levels = [BadgeDetail("Globetrotter", "Complete 1 run on each map", 20)]
    events = ["run_finished"]
    multiple = False

    def award(self, **state):
        user = state["user"]
        maps = Map.objects.values_list("name", flat=True)
        maps_finished = (
            Run.objects.filter(user=user).values_list("map__name", flat=True).distinct()
        )
        # check if maps equals to maps_finished
        if set(maps_finished).issuperset(maps):
            return BadgeAwarded(level=1)


class HailToTheKingBadge(BadgeBase):
    slug = "hailtotheking"
    levels = [
        BadgeDetail(
            "Hail to the King!", "Make your way to 1st place in global rank", 200
        )
    ]
    events = ["rank_processed"]
    multiple = False

    def award(self, **state):
        user = state["user"]
        if user.profile.position == 1:
            return BadgeAwarded(level=1)


class RunScoreBadge(BadgeBase):
    slug = "runscore"
    levels = [
        BadgeDetail(
            "Floating point drifter",  # Oh lol, thanks to heinrich5991 :)
            "Complete a run with time ending with .999",
            50,
        ),
        BadgeDetail("Lucky Sevens", "Complete a run with time ending with .777", 50),
        BadgeDetail("Spawn of Satan", "Complete a run with time ending with .666", 50),
        BadgeDetail(
            "I can see dead zeroes", "Complete a run with time ending with .000", 50
        ),
        BadgeDetail("Pi", "Complete a run with exactly 3.142 seconds", 50),
    ]
    events = ["run_finished"]
    multiple = False

    def award(self, **state):
        run = state["run"]
        time = run.time
        remainder = time % 1  # 7.148 -> 0.148
        remainder_map = {
            Decimal("0.999"): BadgeAwarded(level=1),
            Decimal("0.777"): BadgeAwarded(level=2),
            Decimal("0.666"): BadgeAwarded(level=3),
            Decimal("0.000"): BadgeAwarded(level=4),
        }
        remainder_award = remainder_map.get(remainder)
        if remainder_award:
            return remainder_award
        if time == Decimal("3.142"):
            return BadgeAwarded(level=5)


badges.register(RunCountBadge)
badges.register(RuntimeBadge)
badges.register(RunScoreBadge)
badges.register(GlobetrotterBadge)
badges.register(HailToTheKingBadge)
