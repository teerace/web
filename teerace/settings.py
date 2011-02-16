# pylint: disable-all

try:
	from settings_local import *
except ImportError:
	from settings_default import *
