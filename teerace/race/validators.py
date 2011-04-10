from django.core.exceptions import ValidationError


def is_map_file(field):
	content = field.read()
	if content[:4] not in ('DATA', 'ATAD'):
		raise ValidationError("It's not a valid Teeworlds map file.")
	if content[4] != '\x04':
		raise ValidationError("This map file version is not supported by Teerace"
			" (0.5 or 0.6 is required).")



def is_demo_file(field):
	content = field.read()
	if content[:7] not in ('TWDEMO0',):
		raise ValidationError("It's not a valid Teeworlds demo file.")
	if content[7] < 3:
		raise ValidationError("This demo file version is not supported by Teerace"
			" (0.6 is required).")

