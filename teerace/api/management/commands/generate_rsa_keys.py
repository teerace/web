import sys
from django.core.management.base import BaseCommand
from lib.rsa import RSA


class Command(BaseCommand):
	help = ("Generates a new private/public key pair."
		" You have to put it in settings.py by yourself")

	def handle(self, *args, **options):
		msg = ("You are about to (re)generate public/private RSA keys,\n"
			"which means that CURRENTLY USED KEYS WILL EXPIRE.\n\n"
			"Are you sure you want to proceed? (yes/no): ")
		confirm = raw_input(msg)
		while 1:
			if confirm not in ('yes', 'no'):
				confirm = raw_input('Please enter either "yes" or "no": ')
				continue
			if confirm == 'yes':
				RSA(no_import=True).generate_keys()
				self.stdout.write("Successfully generated RSA keys.\n"
					"You may want to share public_key.pem file"
					" with gameserver maintainers.\n")
				sys.exit(0)
			break
		self.stdout.write("Aborted.\n")
