from piston.handler import BaseHandler
from race.models import Run


class RunHandler(BaseHandler):
	model = Run
