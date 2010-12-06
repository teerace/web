from django.contrib.auth.models import User
from piston.handler import BaseHandler
from race.models import Run


class RunHandler(BaseHandler):
	model = Run

class UserHandler(BaseHandler):
	model = User

