"""
Converts RGB and long RGB values to hexadecimal colours
Awesome work of Robert Chmielowiec.
"""

def rgb_to_rgblong (r, g, b):
	return r * pow (256, 2) + g * 256 + b

def rgblong_to_rgb (rgb):
	return rgb / pow (256, 2), (rgb & 65535 ^ 255) / 256, rgb & 255

def rgb_to_hex(r, g, b):
	return "#%02x%02x%02x" % (r, g, b)
