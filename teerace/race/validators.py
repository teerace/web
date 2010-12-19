from django.core.exceptions import ValidationError


def is_map_file(field):
	content = field.read()
	if content[:4] not in ('DATA', 'ATAD'):
		raise ValidationError("It's not a valid Teeworlds map file.")
