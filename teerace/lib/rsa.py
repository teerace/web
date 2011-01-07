from M2Crypto import BIO, RSA as M2C_RSA
from annoying.functions import get_config


class RSA(object):
	PADDING = M2C_RSA.pkcs1_oaep_padding

	def __init__(self, public_key=None, private_key=None):
		self.public_key = public_key if public_key \
			else get_config('RSA_PUBLIC_KEY', None)
		self.private_key = private_key if private_key \
			else get_config('RSA_PRIVATE_KEY', None)
		self._import_keys()

	def _import_keys(self):
		public_bio = BIO.MemoryBuffer(self.public_key)
		self.rsa_public = M2C_RSA.load_pub_key_bio(public_bio) \
			if public_bio else None

		private_bio = BIO.MemoryBuffer(self.private_key)
		self.rsa_private = M2C_RSA.load_key_bio(private_bio) \
			if private_bio else None

	def decrypt(self, string):
		if not self.rsa_private:
			raise AttributeError("'RSA_PRIVATE_KEY' setting missing.")
		return self.rsa_private.private_decrypt(string, self.PADDING)

	def encrypt(self, string):
		if not self.rsa_public:
			raise AttributeError("'RSA_PUBLIC_KEY' setting missing.")
		return self.rsa_public.public_encrypt(string, self.PADDING)
