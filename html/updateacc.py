#!/usr/bin/python3
#
# Makes the account update page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import re
import sessions, sshtml, sshttp, userstable

try:
	args = sshttp.get_parameters()

	if not sessions.session_is_valid():
		sshttp.senderror(403)
	else:
		if sshttp.is_get():
			DATA = ''
			if 'changename' in args:
				DATA = """<form id="updateacc" action="/updateacc.py" method="post">
						<div class="register">
							<h1>Change name</h1>
							<p>Please fill out this form to update your name.</p>
							{}
							<hr/>

							<label for="newname">New Name</label>
							<input type="text" placeholder="Enter a new name" name="newname" required/>
							<hr/>

							<input type="hidden" name="changename" value="1"/>
							<button style="margin-bottom: 15px;"><a href="javascript:void(0);" onclick="document.getElementById('updateacc').submit()">Change Name</a></button>
						</div>
					</form> """
			elif 'changepassword' in args:
				DATA = """<form id="updateacc" action="/updateacc.py" method="post">
						<div class="register">
							<h1>Change password</h1>
							<p>Please fill out this form to update your password.</p>
							{}
							<hr/>

							<label for="password">Current Password</label>
							<input type="password" placeholder="Enter your password" name="password" required/>

							<label for="newpassword">New Password</label>
							<input type="password" placeholder="Enter a new password" name="newpassword" required/>

							<label for="retype">Retype Password</label>
							<input type="password" placeholder="Retype the new password" name="retype" required/>
							<hr/>

							<input type="hidden" name="changepassword" value="1"/>
							<button style="margin-bottom: 15px;"><a href="javascript:void(0);" onclick="document.getElementById('updateacc').submit()">Change Password</a></button>
						</div>
					</form> """
			ASIDE = """<h2>What is it?</h2>
			<p>Account update portal</p>
			<h2 style="margin-top: 15px;">How does it work?</h2>
			<p>Enter new information to update your account.</p>"""
			MOBILE = ''

			ERROR = '<p><font color="#a93226">{}</font><br/></p>'

			formatting = ''
			if 'nopassword' in args:
				formatting = ERROR.format('Must provide your current password')
			elif 'nonewpassword' in args:
				formatting = ERROR.format('Must provide a new password')
			elif 'noretype' in args:
				formatting = ERROR.format('Must retype the password')
			elif 'noname' in args:
				formatting = ERROR.format('Must provide a new name')
			elif 'passwordmismatch' in args:
				formatting = ERROR.format('Passwords did not match')
			elif 'invalid' in args:
				formatting = ERROR.format('Invalid password')
			replace = {
				'resources' : sshtml.buildResources({'/css/register.css' : 'stylesheet'}),
				'desktopNavLinks' : sshtml.buildDesktopNavLinks(),
				'navLinks' : sshtml.buildNavLinks(),
				'accountLinks' : sshtml.buildAccountLinks(True),
				'body' : sshtml.buildBody(data=DATA.format(formatting), aside=ASIDE, mobile=MOBILE)
			}
			sshttp.send200(sshtml.buildContainerPage(replace))

		elif sshttp.is_post():
			parameters = dict()

			# Change password
			if 'changepassword' in args:
				parameters['changepassword'] = 1
				if 'password' not in args:
					parameters['nopassword'] = 1
					sshttp.send302(sshttp.build_uri('/updateacc.py', parameters))
				elif 'newpassword' not in args:
					parameters['nonewpassword'] = 1
					sshttp.send302(sshttp.build_uri('/updateacc.py', parameters))
				elif 'retype' not in args:
					parameters['noretype'] = 1
					sshttp.send302(sshttp.build_uri('/updateacc.py', parameters))
				elif args.getvalue('newpassword') != args.getvalue('retype'):
					parameters['passwordmismatch'] = 1
					sshttp.send302(sshttp.build_uri('/updateacc.py', parameters))
				else:
					user = sessions.get_user()
					users = userstable.SSUsers(DATABASE)

					uid = userstable.USERS_SCHEMA.get(user, 'id')
					email = userstable.USERS_SCHEMA.get(user, 'email')
					password = args.getvalue('password')

					if not users.validate_user(email, password):
						parameters['invalid'] = 1
						sshttp.send302(sshttp.build_uri('/updateacc.py', parameters))

					else:
						users.set_password(uid, args.getvalue('newpassword'))
						sshttp.send302('/getacc.py?redirect=%2Faccount.py')

			# Change name
			elif 'changename' in args:
				parameters['changename'] = 1
				if 'newname' not in args:
					parameters['noname'] = 1
					sshttp.send302(sshttp.build_uri('/updateacc.py', parameters))
				else:
					user = sessions.get_user()
					users = userstable.SSUsers(DATABASE)

					uid = userstable.USERS_SCHEMA.get(user, 'id')
					users.set_name(uid, args.getvalue('newname'))
					sshttp.send302('/getacc.py?redirect=%2Faccount.py')

			# Unknown
			else:
				shttp.senderror(400)

		else:
			sshttp.senderror(405)
except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

