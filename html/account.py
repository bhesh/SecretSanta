#!/usr/bin/python3
#
# Makes the index page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import sshttp

try:
	import sessions, sshtml, userstable

	if sessions.session_is_valid():
		DATA = """<h1>Welcome, {}!</h1>
			<p align="center">Your email: {}</p>
			<p align="center"><a href="{}">change name</a> | <a href="{}">change password</a></p>
			<p align="center"><a href="/signout.py"><br/>Sign out</a></p>""".format(
					sshttp.build_redirect_uri('/getacc.py', '/updateacc.py?changename=1'),
					sshttp.build_redirect_uri('/getacc.py', '/updateacc.py?changepassword=1'))
		ASIDE = """<h2>What is it?</h2>
			<p>Secret santa registration and group planner.</p>
			<h2 style="margin-top: 15px;">How does it work?</h2>
			<p>Create a group now and invite your friends!</p>"""
		MOBILE = '<p align="center"><br/><button><a href="{}">Create Group Now</a></button></p>'.format(sshttp.build_redirect_uri('/getacc.py', '/groupctl.py?creategroup=1'))

		user = sessions.get_user()
		DATA = DATA.format(userstable.USERS_SCHEMA.get(user, 'name'),
				userstable.USERS_SCHEMA.get(user, 'email'))

		replace = {
			'desktopNavLinks' : sshtml.buildDesktopNavLinks('Account'),
			'navLinks' : sshtml.buildNavLinks('Account'),
			'accountLinks' : sshtml.buildAccountLinks(True),
			'body' : sshtml.buildBody(data=DATA, aside=ASIDE, mobile=MOBILE)
		}
		sshttp.send200(sshtml.buildContainerPage(replace))
	else:
		sshttp.senderror(403)

except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

