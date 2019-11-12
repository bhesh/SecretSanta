#!/usr/bin/python3
#
# Makes the signin page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import datetime
import sshttp

try:
	import sessions, sshtml, userstable, sessionstable

	args = sshttp.get_parameters()
	redirect = sshttp.get_redirect()

	if sessions.session_is_valid():
		if redirect:
			sshttp.print302(redirect)
		else:
			sshttp.print302('/')
	else:
		if sshttp.is_get():
			DATA = """<div class="container">
					<h1>Sign in</h1>
					<p>Please enter your account information.</p>
					{}
					<hr/>
					<form id="signin" action="{}" method="post">
						<div class="signin">
							<label for="email">Email</label>
							<input type="text" placeholder="Enter your email" name="email" required/>

							<label for="email">Password</label>
							<input type="password" placeholder="Enter your password" name="password" required/>

							<button><a href="javascript:void(0);" onclick="document.getElementById('signin').submit()">Sign in</a></button>
						</div>
					</form>
					<hr/>
					<p class="register">Don't have an account? <a href="/register.py">Register</a></p>
				</div>"""
			ASIDE = """<h2>What?</h2>
			<p>Secret santa registration and group planner.</p>
			<h2 style="margin-top: 15px;">How?</h2>
			<p>Register now and invite your friends!</p>"""
			MOBILE = '<p align="center"><br/><button><a href="/register.py">Register Now</a></button></p>'

			ERROR='<p><font color="#a93226">{}</font><br/></p>'

			formatting = ''
			if 'noemail' in args:
				formatting = ERROR.format('Must provide an email')
			elif 'nopassword' in args:
				formatting = ERROR.format('Must provide a password')
			elif 'invalid' in args:
				formatting = ERROR.format('Invalid username or password')
			data = DATA.format(formatting, sshttp.build_redirect_uri('/signin.py', redirect))
			replace = {
				'resources' : sshtml.buildResources({'/css/signin.css' : 'stylesheet'}),
				'desktopNavLinks' : sshtml.buildDesktopNavLinks(),
				'navLinks' : sshtml.buildNavLinks(),
				'accountLinks' : sshtml.buildAccountLinks(False),
				'body' : sshtml.buildBody(data=data, aside=ASIDE, mobile=MOBILE)
			}
			sshttp.send200(sshtml.buildContainerPage(replace))

		elif sshttp.is_post():
			parameters = dict()
			if redirect:
				parameters['redirect'] = redirect
			if 'email' not in args:
				parameters['noemail'] = 1
				sshttp.send302(sshttp.build_uri('/signin.py', parameters))
			elif 'password' not in args:
				parameters['nopassword'] = 1
				sshttp.send302(sshttp.build_uri('/signin.py', parameters))
			else:
				users = userstable.SSUsers(DATABASE)
				ssids = sessionstable.SSSessions(DATABASE)

				email = args.getvalue('email')
				password = args.getvalue('password')

				if not users.validate_user(email, password):
					parameters['invalid'] = 1
					sshttp.send302(sshttp.build_uri('/signin.py', parameters))

				else:
					uid = users.get_user_by_email(email, ['id'])[0]
					ssid = ssids.create_session(uid)
					expiration = ssids.get_session(ssid, ['expiration'])[0]
					if redirect:
						sshttp.send302(redirect, headers={'Set-Cookie' : 'ssid={}; Secure; Expires="{}"'
								.format(ssid, datetime.datetime.fromtimestamp(expiration))})
					else:
						sshttp.send302('/', headers={'Set-Cookie' : 'ssid={}; Secure; Expires="{}"'
								.format(ssid, datetime.datetime.fromtimestamp(expiration))})

		else:
			sshttp.senderror(405)
except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

