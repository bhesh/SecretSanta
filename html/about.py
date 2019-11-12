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

	DATA = """<p>Simple solution to annoying partner assignments. Ensures no one knows any other person's partner.</p>
			<p><h2>Future Plans</h2></p>
			<p><h3>Groups</h3></p>
			<ul>
				<li>Group administrators</li>
				<li>Group privacy tools</li>
				<li>Restricted partner viewing</li>
			</ul>
			<p><h3>Allow Partner Assignment Rules</h3></p>
			<ul>
				<li>Household exclusion</li>
				<li>Location exclusions</li>
				<li>Age matching</li>
			</ul>
			<p><h3>Registries</h3></p>
			<ul>
				<li>List of present ideas</li>
				<li>Claim purchase</li>
			</ul>"""
	if loggedin:
		DATA += """<p align="center"><br/><button><a href="{}">Create a Group Now</a></button></p>
			<p class="footnote">Website designed by Brian Hession</p>""".format(sshttp.build_redirect_uri('/getacc.py', '/groupctl.py?creategroup=1'))
	else:
		DATA += """<p align="center"><br/><button><a href="/register.py">Register Now</a></button></p>
			<p class="footnote">Website designed by Brian Hession</p>"""
	ASIDE = """ <h2>What is it?</h2>
	<p>Secret santa registration and group planner.</p>
	<h2 style="margin-top: 15px;">How does it work?</h2>
	<p>Register now and invite your friends!</p> """
	MOBILE = '<p align="center"><br/><button><a href="/register.py">Register Now</a></button></p>'
	if loggedin:
		ASIDE = """<h2>What is it?</h2>
			<p>Secret santa registration and group planner.</p>
			<h2 style="margin-top: 15px;">How does it work?</h2>
			<p>Create a group now and invite your friends!</p>"""
		MOBILE = '<p align="center"><br/><button><a href="{}">Create a Group Now</a></button></p>'.format(sshttp.build_redirect_uri('/getacc.py', '/groupctl.py?creategroup=1'))

	replace = {
		'desktopNavLinks' : sshtml.buildDesktopNavLinks('About'),
		'navLinks' : sshtml.buildNavLinks('About'),
		'accountLinks' : sshtml.buildAccountLinks(loggedin),
		'body' : sshtml.buildBody(data=DATA, aside=ASIDE, mobile=MOBILE)
	}
	sshttp.send200(sshtml.buildContainerPage(replace))
except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

