
"""
http://stackoverflow.com/questions/312443/#312464
"""

def chunks(l, n):
	for i in xrange(0, len(l), n):
		yield l[i:i+n]