#!/usr/bin/python3
#
# Makes the register page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import re
import sshttp

try:
	import sessions, sshtml, userstable

	args = sshttp.get_parameters()

	if sessions.session_is_valid():
		DATA = '<p>You are already signed in. Please sign out to continue.</p>'
		ASIDE = """<h2>What is it?</h2>
		<p>Secret santa account registration</p>
		<h2 style="margin-top: 15px;">How does it work?</h2>
		<p>Enter your information in the fields. Once completed, you can either create a group or be invited by others.</p>"""
		MOBILE = ''
		replace = {
			'desktopNavLinks' : sshtml.buildDesktopNavLinks(),
			'navLinks' : sshtml.buildNavLinks(),
			'accountLinks' : sshtml.buildAccountLinks(False),
			'body' : sshtml.buildBody(data=DATA, aside=ASIDE, mobile=MOBILE)
		}
		sshttp.send200(sshtml.buildContainerPage(replace))
	else:
		if sshttp.is_get():
			DATA = """<form id="register" action="/register.py" method="post">
					<div class="register">
						<h1>Register</h1>
						<p>Please fill out this form to create an account.</p>
						{}
						<hr/>

						<label for="email">Email</label>
						<input type="text" placeholder="Enter your email" name="email" required/>

						<label for="password">Password</label>
						<input type="password" placeholder="Enter your password" name="password" required/>

						<label for="retype">Retype Password</label>
						<input type="password" placeholder="Retype your password" name="retype" required/>

						<label for="name">Name</label>
						<input type="text" placeholder="Enter your name" name="name" required/>
						<hr/>

						<p>By creating an account you agree to our <a href="#">Terms & Privacy</a>.</p>
						<button><a href="javascript:void(0);" onclick="document.getElementById('register').submit()">Create Account</a></button>
						<p class="signin">Already have an account? <a href="/getacc.py">Sign in</a></p>
					</div>
				</form> """
			ASIDE = """<h2>What?</h2>
			<p>Secret santa registration and group planner.</p>
			<h2 style="margin-top: 15px;">How?</h2>
			<p>Register now and invite your friends!</p>"""
			MOBILE = '<p align="center"><br/><button><a href="/register.py">Register Now</a></button></p>'

			ERROR = '<p><font color="#a93226">{}</font><br/></p>'

			formatting = ''
			if 'noemail' in args:
				formatting = ERROR.format('Must provide an email')
			elif 'nopassword' in args:
				formatting = ERROR.format('Must provide a password')
			elif 'noretype' in args:
				formatting = ERROR.format('Must retype the password')
			elif 'noname' in args:
				formatting = ERROR.format('Must provide a name')
			elif 'bademail' in args:
				formatting = ERROR.format('Please provide a real email')
			elif 'passwordmismatch' in args:
				formatting = ERROR.format('Passwords did not match')
			elif 'emailinuse' in args:
				formatting = ERROR.format('Email is already in use')
			replace = {
				'resources' : sshtml.buildResources({'/css/register.css' : 'stylesheet'}),
				'desktopNavLinks' : sshtml.buildDesktopNavLinks(),
				'navLinks' : sshtml.buildNavLinks(),
				'accountLinks' : sshtml.buildAccountLinks(False),
				'body' : sshtml.buildBody(data=DATA.format(formatting), aside=ASIDE, mobile=MOBILE)
			}
			sshttp.send200(sshtml.buildContainerPage(replace))

		elif sshttp.is_post():
			EMAIL_MATCH = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

			parameters = dict()
			if 'email' not in args:
				parameters['noemail'] = 1
				sshttp.send302(sshttp.build_uri('/register.py', parameters))
			elif 'password' not in args:
				parameters['nopassword'] = 1
				sshttp.send302(sshttp.build_uri('/register.py', parameters))
			elif 'retype' not in args:
				parameters['noretype'] = 1
				sshttp.send302(sshttp.build_uri('/register.py', parameters))
			elif 'name' not in args:
				parameters['noname'] = 1
				sshttp.send302(sshttp.build_uri('/register.py', parameters))
			elif not EMAIL_MATCH.fullmatch(args.getvalue('email')):
				parameters['bademail'] = 1
				sshttp.send302(sshttp.build_uri('/register.py', parameters))
			elif args.getvalue('password') != args.getvalue('retype'):
				parameters['passwordmismatch'] = 1
				sshttp.send302(sshttp.build_uri('/register.py', parameters))
			else:
				users = userstable.SSUsers(DATABASE)
				email = args.getvalue('email').lower()
				name = args.getvalue('name')
				password = args.getvalue('password')
				if users.get_user_by_email(email, cols=['id']):
					parameters['emailinuse'] = 1
					sshttp.send302(sshttp.build_uri('/register.py', parameters))
				else:
					uid = users.create_user(email, name, password)
					DATA = '<p>Registration successful. Click <a href="/getacc.py">here</a> to sign in.</p>'
					ASIDE = """<h2>What?</h2>
					<p>Secret santa registration and group planner.</p>
					<h2 style="margin-top: 15px;">How?</h2>
					<p>Register now and invite your friends!</p>"""
					MOBILE = '<p align="center"><br/><button><a href="/register.py">Register Now</a></button></p>'
					replace = {
						'desktopNavLinks' : sshtml.buildDesktopNavLinks(),
						'navLinks' : sshtml.buildNavLinks(),
						'accountLinks' : sshtml.buildAccountLinks(False),
						'body' : sshtml.buildBody(data=DATA, aside=ASIDE, mobile=MOBILE)
					}
					sshttp.send200(sshtml.buildContainerPage(replace))

		else:
			sshttp.senderror(405)
except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

