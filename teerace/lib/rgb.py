"""
Converts RGB and long RGB values to hexadecimal colours
Awesome work of Robert Chmielowiec.
"""

def rgb_to_rgblong(red, green, blue):
	return red * pow (256, 2) + green * 256 + blue

def rgblong_to_rgb(rgb):
	return rgb / pow (256, 2), (rgb & 65535 ^ 255) / 256, rgb & 255

def rgb_to_hex(red, green, blue):
	return "#%02x%02x%02x" % (red, green, blue)

def rgblong_to_hex(rgb):
	return rgb_to_hex(*rgblong_to_rgb(rgb))
