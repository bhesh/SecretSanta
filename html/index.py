#!/usr/bin/python3
#
# Makes the index page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import sys
import sessions, sshtml, sshttp

DATA = """ <p>Simple solution to annoying partner assignments. Ensures no one knows any other person's partner.</p>
<h2>Create your account today!</h2>
<p align="center"><br/><button><a href="register.html">Register Now</a></button></p> """
ASIDE = """ <h2>What?</h2>
<p>Secret santa registration and group planner.</p>
<h2 style="margin-top: 15px;">How?</h2>
<p>Register now and invite your friends!</p> """
MOBILE = '<p align="center"><br/><button><a href="register.html">Register Now</a></button></p>'

try:
	replace = {
		'desktopNavLinks' : sshtml.buildDesktopNavLinks('Home'),
		'navLinks' : sshtml.buildNavLinks('Home'),
		'accountLinks' : sshtml.buildAccountLinks(sessions.session_is_valid()),
		'body' : sshtml.buildBody(data=DATA, aside=ASIDE, mobile=MOBILE)
	}
	sshttp.send200(sshtml.buildContainerPage(replace))
except:
	sshttp.senderror(500)
	print(sys.exc_info()[0], file=sys.stderr)

