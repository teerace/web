from django.core.exceptions import ValidationError


def is_map_file(field):
    content = field.read()
    if content[:4] not in (b"DATA", b"ATAD"):
        raise ValidationError("It's not a valid Teeworlds map file.")
    if content[4] != 4:
        raise ValidationError(
            "This map file version is not supported by Teerace"
            " (0.5 or 0.6 is required)."
        )


def is_demo_file(field):
    content = field.read()
    if content[:6] != b"TWDEMO":
        raise ValidationError("It's not a valid Teeworlds demo file.")
    if content[7] != 4:
        raise ValidationError(
            "This demo file version is not supported by Teerace" " (0.6 is required)."
        )


def is_ghost_file(field):
    content = field.read()
    if content[:7] != b"TWGHOST":
        raise ValidationError("It's not a valid Teeworlds ghost file.")
