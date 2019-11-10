#!/usr/bin/python3
#
# Makes the register page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import cgi, re
from include import makehtml, tools, ssdb

try:
	args = cgi.FieldStorage()

	if tools.is_logged_in():
		HTML='<p><br/>You are already logged in. Please logout to continue.</p>'
		print('Content-Type: text/html')
		print('')
		print(makehtml.makehtml(HTML))
	else:
		if tools.is_get():
			HTML="""<p><br/>Registration</p>
			<form action="/register.py" method="POST">
			<br/>Email:<br/><input type="text" name="email"/><br/>{}
			<br/>Password:<br/><input type="password" name="password"/><br/>{}
			<br/>Retype Password:<br/><input type="password" name="retype"/><br/>{}
			<br/>First Name:<br/><input type="text" name="firstname"/><br/>{}
			<br/>Last Name:<br/><input type="text" name="lastname"/><br/>{}
			<br/><input type="submit" value="Submit"/>
			</form>"""

			ERROR='<font color="#a93226">{}</font><br/>'

			print('Status: 200 OK')
			print('Content-Type: text/html')
			print('')

			args = cgi.FieldStorage()
			formatting = ['', '', '', '', '']
			if 'noemail' in args:
				formatting[0] = ERROR.format('Must provide an email')
			if 'nopassword' in args:
				formatting[1] = ERROR.format('Must provide a password')
			if 'noretype' in args:
				formatting[2] = ERROR.format('Must retype the password')
			if 'nofirstname' in args:
				formatting[3] = ERROR.format('Must provide a first name')
			if 'nolastname' in args:
				formatting[4] = ERROR.format('Must provide a last name')
			if 'bademail' in args:
				formatting[0] = ERROR.format('Please provide a real email')
			if 'passwordmismatch' in args:
				formatting[2] = ERROR.format('Passwords did not match')
			if 'emailinuse' in args:
				formatting[0] = ERROR.format('Email is already in use')
			print(makehtml.makehtml(HTML.format(*formatting)))

		elif tools.is_post():
			EMAIL_MATCH = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

			if 'email' not in args:
				makehtml.printredirect('/register.py?noemail=1')
			elif 'password' not in args:
				makehtml.printredirect('/register.py?nopassword=1')
			elif 'retype' not in args:
				makehtml.printredirect('/register.py?noretype=1')
			elif 'firstname' not in args:
				makehtml.printredirect('/register.py?nofirstname=1')
			elif 'lastname' not in args:
				makehtml.printredirect('/register.py?nolastname=1')
			elif not EMAIL_MATCH.fullmatch(tools.unescape(args.getvalue('email'))):
				makehtml.printredirect('/register.py?bademail=1')
			elif args.getvalue('password') != args.getvalue('retype'):
				makehtml.printredirect('/register.py?passwordmismatch=1')
			else:
				db = ssdb.SSDatabase('db/secretsanta.db')
				if not db.create_user(tools.unescape(args.getvalue('email')).lower(),
						tools.unescape(args.getvalue('firstname')),
						tools.unescape(args.getvalue('lastname')),
						tools.unescape(args.getvalue('password'))):
					makehtml.printredirect('/register.py?emailinuse=1')
				HTML='<p><br/>Registration successful. Click <a href="/login.py">here</a> to login.</p>'
				print('Content-Type: text/html')
				print('')
				print(makehtml.makehtml(HTML))

		else:
			makehtml.printerror('405 Invalid Method', '<p><br/>Method not supported</p>')
except ssdb.Error as e:
	makehtml.printerror('500 Server Error', '<p><br/>Database error: {}</p>'.format(tools.escape(str(e))))
except:
	makehtml.printerror('500 Server Error', '<p><br/>500 Server Error</p>')

