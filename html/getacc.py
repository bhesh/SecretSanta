#!/usr/bin/python3
#
# Gets the account information
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import sys
import sessions, sshttp

try:
	referer = sshttp.get_referer()
	if sessions.session_is_valid():
		if referer:
			sshttp.sendredirect(referer)
		else:
			sshttp.sendredirect('/')
	else:
		sshttp.sendredirect('/login.py', referer)
except:
	sshttp.senderror(500)
	print(sys.exc_info()[0], file=sys.stderr)

