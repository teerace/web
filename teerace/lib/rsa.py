from M2Crypto import BIO, RSA as M2C_RSA
from annoying.functions import get_config


class RSA(object):
	PADDING = M2C_RSA.pkcs1_oaep_padding
	LENGTH = 2048
	PUBLIC_EXPONENT = 3
	public_key = private_key = None
	rsa_public = rsa_private = None

	PROJECT_DIR = get_config('PROJECT_DIR', '')
	public_key_filename = PROJECT_DIR + '/public_key.pem'
	private_key_filename = PROJECT_DIR + '/private_key.pem'

	def __init__(self, public_key=None, private_key=None, no_import=False):
		if public_key:
			self.public_key = public_key
		if private_key:
			self.private_key = private_key
		if not no_import:
			self._import_keys()

	def _import_keys(self):
		public_bio = BIO.MemoryBuffer(self.public_key) if self.public_key \
			else None
		self.rsa_public = M2C_RSA.load_pub_key_bio(public_bio) \
			if public_bio else M2C_RSA.load_pub_key(self.public_key_filename)

		private_bio = BIO.MemoryBuffer(self.private_key) if self.private_key \
			else None
		self.rsa_private = M2C_RSA.load_key_bio(private_bio) \
			if private_bio else M2C_RSA.load_key(self.private_key_filename,
				callback=self.dpc)

	def generate_keys(self):
		keys = M2C_RSA.gen_key(self.LENGTH, self.PUBLIC_EXPONENT)
		keys.save_key(self.private_key_filename, callback=self.dpc)
		keys.save_pub_key(self.public_key_filename)

	def decrypt(self, string):
		if not self.rsa_private:
			raise AttributeError("private_key.pem file missing.")
		return self.rsa_private.private_decrypt(string, self.PADDING)

	def encrypt(self, string):
		if not self.rsa_public:
			raise AttributeError("public_key.pem file missing.")
		return self.rsa_public.public_encrypt(string, self.PADDING)

	@staticmethod
	def dpc(*args):
		""" dummy passphrase callback """
		return 'teerace'
