from Crypto.Cipher import AES
from django.core.cache import cache
import base64

"""
Based on:
http://www.codekoala.com/blog/2009/aes-encryption-python-using-pycrypto/
"""

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

def aes_helper(function, string, key):
	"""
	Base function for aes_encrypt and aes_decrypt
	"""

	if len(key) != BLOCK_SIZE:
		raise TypeError("Length of key used to generate"
			" cipher have to match BLOCK_SIZE")

	cipher = cache.get(key)
	if cipher is None:
		cipher = AES.new(key)
		cache.set(key, cipher)

	return function(cipher, string)


def aes_encrypt(string, key):
	"""
	Encrypts `string` using cipher generated from `key`
	AND encodes result with base64.
	"""

	encode_aes = lambda c, s: base64.b64encode(c.encrypt(pad(s)))

	return aes_helper(encode_aes, string, key)


def aes_decrypt(string, key):
	"""
	Decodes encoded `string` with base64 and decrypts
	result using cipher generated from `key`.
	"""

	decode_aes = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

	return aes_helper(decode_aes, string, key)
