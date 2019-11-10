#!/usr/bin/python3
#
# Updates user account information
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import cgi
from include import tools, makehtml, ssdb

try:
	args = cgi.FieldStorage()

	if tools.is_logged_in():
		user = tools.get_user()
		if not user:
			raise ssdb.Error('No user')

		if tools.is_get():
			HTML = ''
			ERROR = '<font color="#a93226">{}</font><br/>'
			formatting = []
			if 'changepassword' in args:
				HTML = """<p><br/>Change password</p>
				<form action="/updateacc.py" method="POST">
				<br/>Current Password:<br/><input type="password" name="curpass"/><br/>{}
				<br/>New Password:<br/><input type="password" name="newpass"/><br/>{}
				<br/>Retype Password:<br/><input type="password" name="retype"/><br/>{}
				<input type="hidden" name="changepassword" value="1"/>
				<br/><input type="submit" value="Submit"/>
				</form>"""
				formatting = ['', '', '']
				if 'nopassword' in args:
					formatting[0] = ERROR.format('Must provide your password')
				if 'nonewpass' in args:
					formatting[1] = ERROR.format('Must provide a new password')
				if 'noretype' in args:
					formatting[2] = ERROR.format('Must retype the password')
				if 'passwordmismatch' in args:
					formatting[2] = ERROR.format('Passwords do not match')
				if 'invalid' in args:
					formatting[0] = ERROR.format('Incorrect password')
			elif 'changename' in args:
				HTML = """<p><br/>Change name</p>
				<form action="/updateacc.py" method="POST">
				<br/>New First Name:<br/><input type="text" name="firstname"/><br/>{}
				<br/>New Last Name:<br/><input type="text" name="lastname"/><br/>{}
				<input type="hidden" name="changename" value="1"/>
				<br/><input type="submit" value="Submit"/>
				</form>"""
				formatting = ['', '']
				if 'nofirstname' in args:
					formatting[0] = ERROR.format('Must provide a first name')
				if 'nolastname' in args:
					formatting[1] = ERROR.format('Must provide a last name')
			print('Content-Type: text/html')
			print('')
			print(makehtml.makehtml(HTML.format(*formatting)))

		elif tools.is_post():
			db = ssdb.SSDatabase('db/secretsanta.db')
			HTML = ''
			if 'changepassword' in args:
				if 'curpass' not in args:
					makehtml.printredirect('/updateacc.py?changepassword=1&nopassword=1')
				elif 'newpass' not in args:
					makehtml.printredirect('/updateacc.py?changepassword=1&nonewpass=1')
				elif 'retype' not in args:
					makehtml.printredirect('/updateacc.py?changepassword=1&noretype=1')
				elif args.getvalue('newpass') != args.getvalue('retype'):
					makehtml.printredirect('/updateacc.py?changepassword=1&passwordmismatch=1')
				else:
					if not db.validate_user(user[ssdb.COLUMNS['Email']], tools.unescape(args.getvalue('curpass'))):
						makehtml.printredirect('/updateacc.py?changepassword=1&invalid=1')
					else:
						db.set_password(user[ssdb.COLUMNS['id']], tools.unescape(args.getvalue('newpass')))
						makehtml.printredirect('/account.py')

			elif 'changename' in args:
				if 'firstname' not in args:
					makehtml.printredirect('/updateacc.py?changename=1&nofirstname=1')
				elif 'lastname' not in args:
					makehtml.printredirect('/updateacc.py?changename=1&nolastname=1')
				else:
					db.set_firstname(user[ssdb.COLUMNS['id']], tools.unescape(args.getvalue('firstname')))
					db.set_lastname(user[ssdb.COLUMNS['id']], tools.unescape(args.getvalue('lastname')))
					makehtml.printredirect('/account.py')

			else:
				makehtml.printredirect('/account.py')

		else:
			makehtml.printerror('405 Invalid Method', '<p><br/>Method not supported</p>')
	else:
		makehtml.printredirect('/login.py')
except ssdb.Error as e:
	makehtml.printerror('500 Server Error', '<p><br/>Database error: {}</p>'.format(tools.escape(str(e))))
except:
	makehtml.printerror('500 Server Error', '<p><br/>500 Server Error</p>')

