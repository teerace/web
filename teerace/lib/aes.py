from Crypto.Cipher import AES as Cipher_AES
import base64

"""
Based on:
http://www.codekoala.com/blog/2009/aes-encryption-python-using-pycrypto/
"""

class AES(object):
	# the block size for the cipher object; must be 16, 24, or 32 for AES
	BLOCK_SIZE = 16

	# the character used for padding--with a block cipher such as AES, the value
	# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
	# used to ensure that your value is always a multiple of BLOCK_SIZE
	PADDING = '{'

	def __init__(self, key):
		self.key = key
		self.cipher = None
		self._generate_cipher()

	def pad(self, string):
		""" one-liner to sufficiently pad the text to be encrypted """
		return string + (self.BLOCK_SIZE - len(string) % self.BLOCK_SIZE) * self.PADDING

	def _generate_cipher(self):
		if len(self.key) != self.BLOCK_SIZE:
			raise TypeError("Length of the key used to generate"
				" a cipher have to match BLOCK_SIZE")
		self.cipher = Cipher_AES.new(self.key)

	def decrypt(self, string):
		return self.cipher.decrypt(base64.b64decode(string)).rstrip(self.PADDING)

	def encrypt(self, string):
		return base64.b64encode(self.cipher.encrypt(self.pad(string)))
