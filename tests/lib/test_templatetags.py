import pytest

from lib.templatetags.human_duration import sectodur


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (-1, "-"),
        (0, "-"),
        (1, "1 sec"),
        (1.4, "1.4 secs"),
        (2, "2 secs"),
        (50, "50 secs"),
        (100, "1 min 40 secs"),
        (120, "2 mins"),
        (121, "2 mins 1 sec"),
        (122, "2 mins 2 secs"),
        (612.2, "10 mins 12.2 secs"),
        (3599, "59 mins 59 secs"),
        (3600, "1 hr"),
        (3601, "1 hr 1 sec"),
        (3602, "1 hr 2 secs"),
        (3660, "1 hr 1 min"),
        (3661, "1 hr 1 min 1 sec"),
        (3662, "1 hr 1 min 2 secs"),
        (3722, "1 hr 2 mins 2 secs"),
        (7199, "1 hr 59 mins 59 secs"),
        (7200, "2 hrs"),
        (7201, "2 hrs 1 sec"),
        (7202, "2 hrs 2 secs"),
        (7260, "2 hrs 1 min"),
        (7261, "2 hrs 1 min 1 sec"),
        (7262, "2 hrs 1 min 2 secs"),
        (86399, "23 hrs 59 mins 59 secs"),
        (86400, "1 day"),
        (172800, "2 days"),
        (34560000, "400 days"),
    ],
)
def test_sectodur(test_input, expected):
    assert sectodur(test_input) == expected
