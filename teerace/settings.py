# pylint: disable-msg-cat=WCREFI

try:
	from settings_local import *
except ImportError:
	from settings_default import *
