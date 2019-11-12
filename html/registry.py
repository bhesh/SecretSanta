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

	DATA = '<h1 style="text-align: center">Under construction</h1><p style="font-size: 256px;text-align: center"><i class="fas fa-tools"></i></p>'
	ASIDE = """ <h2>What?</h2>
	<p>Secret santa registration and group planner.</p>
	<h2 style="margin-top: 15px;">How?</h2>
	<p>Register now and invite your friends!</p> """
	MOBILE = '<p align="center"><br/><button><a href="/register.py">Register Now</a></button></p>'
	if loggedin:
		ASIDE = """<h2>What is it?</h2>
			<p>Secret santa registration and group planner.</p>
			<h2 style="margin-top: 15px;">How does it work?</h2>
			<p>Create a group now and invite your friends!</p>"""
		MOBILE = '<p align="center"><br/><button><a href="{}">Create a Group Now</a></button></p>'.format(sshttp.build_redirect_uri('/getacc.py', '/groupctl.py?creategroup=1'))

	replace = {
		'desktopNavLinks' : sshtml.buildDesktopNavLinks('Registry'),
		'navLinks' : sshtml.buildNavLinks('Registry'),
		'accountLinks' : sshtml.buildAccountLinks(loggedin),
		'body' : sshtml.buildBody(data=DATA, aside=ASIDE, mobile=MOBILE)
	}
	sshttp.send200(sshtml.buildContainerPage(replace))
except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

