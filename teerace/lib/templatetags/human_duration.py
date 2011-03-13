# Import template library
from django import template

# Set register
register = template.Library()

# Register filter
@register.filter
def sectodur(value, arg = ''):

	"""
	#######################################################
	#                                                     #
	#   Seconds-to-Duration Template Tag                  #
	#   Dan Ward 2009 (http://d-w.me)                     #
	#                                                     #
	#######################################################

	Usage: {{ VALUE|sectodur[:"long"] }}

	NOTE: Please read up 'Custom template tags and filters'
	if you are unsure as to how the template tag is
	implemented in your project.
	"""

	# Place seconds in to integer
	secs = int(value)

	# If seconds are greater than 0
	if secs > 0:

		# Import math library
		import math

		# Place durations of given units in to variables
		day_secs = 86400
		hour_secs = 3600
		min_secs = 60

		# If short string is enabled
		if arg != 'long':

			# Set short names
			day_unit_name = ' day'
			hour_unit_name = ' hr'
			min_unit_name = ' min'
			sec_unit_name = ' sec'
			
			# Set short duration unit splitters
			last_dur_splitter = ' '
			next_dur_splitter = last_dur_splitter
		
			# If short string is not provided or any other value
		else:

			# Set long names
			day_unit_name = ' day'
			hour_unit_name = ' hour'
			min_unit_name = ' minute'
			sec_unit_name = ' second'

			# Set long duration unit splitters
			last_dur_splitter = ' and '
			next_dur_splitter = ', '
		
		# Create string to hold outout
		duration_string = ''
		
		# Calculate number of days from seconds
		days = int(math.floor(secs / int(day_secs)))
		
		# Subtract days from seconds
		secs = secs - (days * int(day_secs))
		
		# Calculate number of hours from seconds (minus number of days)
		hours = int(math.floor(secs / int(hour_secs)))
		
		# Subtract hours from seconds
		secs = secs - (hours * int(hour_secs))
		
		# Calculate number of minutes from seconds (minus number of days and hours)
		minutes = int(math.floor(secs / int(min_secs)))
		
		# Subtract days from seconds
		secs = secs - (minutes * int(min_secs))
		
		# Calculate number of seconds (minus days, hours and minutes)
		seconds = secs
		
		# If number of days is greater than 0				
		if days > 0:
			
			# Add multiple days to duration string
			duration_string += ' ' + str(days) + day_unit_name + (days > 1 and 's' or '')
		
		# Determine if next string is to be shown
		if hours > 0:

			# If there are no more units after this
			if minutes <= 0 and seconds <= 0:

				# Set hour splitter to last
				hour_splitter = last_dur_splitter

			# If there are unit after this
			else:

				# Set hour splitter to next
				hour_splitter = (len(duration_string) > 0 and next_dur_splitter or '')

		# If number of hours is greater than 0
		if hours > 0:

			# Add multiple days to duration string
			duration_string += hour_splitter + ' ' + str(hours) + hour_unit_name + \
				(hours > 1 and 's' or '')

		# Determine if next string is to be shown
		if minutes > 0:

			# If there are no more units after this
			if seconds <= 0:

				# Set minute splitter to last
				min_splitter = last_dur_splitter

			# If there are unit after this
			else:

				# Set minute splitter to next
				min_splitter = (len(duration_string) > 0 and next_dur_splitter or '')

		# If number of minutes is greater than 0
		if minutes > 0:

			# Add multiple days to duration string
			duration_string += min_splitter + ' ' + str(minutes) + min_unit_name + \
				(minutes > 1 and 's' or '')

		# Determine if next string is last
		if seconds > 0:

			# Set second splitter
			sec_splitter = (len(duration_string) > 0 and last_dur_splitter or '')

		# If number of seconds is greater than 0
		if seconds > 0:

			# Add multiple days to duration string
			duration_string += sec_splitter + ' ' + str(seconds) + sec_unit_name + \
				(seconds > 1 and 's' or '')

		# Return duration string
		return duration_string.strip()

	# If seconds are not greater than 0
	else:

		# Provide 'No duration' message
		return '-'
