#!/usr/bin/python3
#
# Checks for an active session
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import datetime
import sshttp

try:
	import sessions

	args = sshttp.get_parameters()
	redirect = sshttp.get_redirect()

	if sessions.session_is_valid():
		if redirect:
			sshttp.send302(redirect)
		else:
			sshttp.send302('/')
	elif sshttp.has_cookies():
		sshttp.send302(sshttp.build_redirect_uri('/signin.py', redirect), headers={
				'Set-Cookie' : 'ssid=expired; Secure; Expires="{}"'.format(datetime.datetime.utcfromtimestamp(0))
		})
	else:
		sshttp.send302(sshttp.build_redirect_uri('/signin.py', redirect))
except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

