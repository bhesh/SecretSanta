#!/usr/bin/python3
#
# Signs out the user
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import datetime
import sessions, sshttp

try:
	sessions.delete_session()

	args = sshttp.get_parameters()
	redirect = sshttp.get_redirect()

	if redirect:
		sshttp.send302(redirect, headers={
				'Set-Cookie' : 'ssid=expired; Secure; Expires="{}"'.format(datetime.datetime.utcfromtimestamp(0))
		})
	else:
		sshttp.send302('/', headers={
				'Set-Cookie' : 'ssid=expired; Secure; Expires="{}"'.format(datetime.datetime.utcfromtimestamp(0))
		})

except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

