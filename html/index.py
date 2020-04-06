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
	import sessions, sshtml

	loggedin = sessions.session_is_valid()

	DATA = '<p>Simple solution to annoying secret santa target assignments. Ensures no one knows any other person\'s target.</p>'
	if loggedin:
		DATA += """<h2>Create your group today!</h2><p align="center"><br/>
			<button><a href="{}">Create a Group Now</a></button>""".format(sshttp.build_redirect_uri('/getacc.py', '/groupctl.py?creategroup=1'))
	else:
		DATA += """<h2>Create your group today!</h2>
				<p align="center" style="margin: 15px;"><button><a href="/getacc.py">Sign in</a></button></p>
				<p align="center" style="margin-top: 15px;">Or if you do not have an account, <a href="/register.py">register now</a></p>"""
	ASIDE = """<h2>What is it?</h2>
		<p>Secret santa registration and group planner.</p>
		<h2 style="margin-top: 15px;">How does it work?</h2>
		<p>Register now and invite your friends!</p>"""
	MOBILE = '<p align="center"><br/><button><a href="/register.py">Register Now</a></button></p>'
	if loggedin:
		ASIDE = """<h2>What is it?</h2>
			<p>Secret santa registration and group planner.</p>
			<h2 style="margin-top: 15px;">How does it work?</h2>
			<p>Create a group now and invite your friends!</p>"""
		MOBILE = '<p align="center"><br/><button><a href="{}">Create a Group Now</a></button></p>'.format(sshttp.build_redirect_uri('/getacc.py', '/groupctl.py?creategroup=1'))

	replace = {
		'desktopNavLinks' : sshtml.buildDesktopNavLinks('Home'),
		'navLinks' : sshtml.buildNavLinks('Home'),
		'accountLinks' : sshtml.buildAccountLinks(loggedin),
		'body' : sshtml.buildBody(data=DATA, aside=ASIDE, mobile=MOBILE)
	}
	sshttp.send200(sshtml.buildContainerPage(replace))
except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

