#!/usr/bin/python3
#
# Makes the index page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import cgi
from include import tools, makehtml, ssdb

try:
	args = cgi.FieldStorage()

	if tools.is_logged_in():
		HTML='<p><br/>You are already logged in. Please logout to continue.</p>'
		print('Content-Type: text/html')
		print('')
		print(makehtml.makehtml(HTML))
	else:
		if tools.is_get():
			HTML=""" <p><br/>Enter your account information</p>
			<form action="/login.py" method="POST">
			<br/>Email<br/><input type="text" name="email"/><br/>{}
			<br/>Password<br/><input type="password" name="password"/><br/>{}
			<br/><input type="submit" value="Submit"/>
			</form>
			<p><br/>Need an account? <a href="/register.py">Register</a></p>"""

			ERROR='<font color="#a93226">{}</font><br/>'

			formatting = ['', '']
			if 'noemail' in args:
				formatting[0] = ERROR.format('Must provide an email')
			if 'nopassword' in args:
				formatting[1] = ERROR.format('Must provide a password')
			if 'invalid' in args:
				formatting[1] = ERROR.format('Invalid username or password')
			print('Status: 200 OK')
			print('Content-Type: text/html')
			print('')
			print(makehtml.makehtml(HTML.format(*formatting)))

		elif tools.is_post():
			db = ssdb.SSDatabase('db/secretsanta.db')

			if tools.is_logged_in():
				makehtml.printredirect('/')
			elif 'email' not in args:
				makehtml.printredirect('/login.py?noemail=1')
			elif 'password' not in args:
				makehtml.printredirect('/login.py?nopassword=1')
			else:
				email = tools.unescape(args.getvalue('email')).lower()
				password = tools.unescape(args.getvalue('password'))
				if not db.validate_user(email, password):
					makehtml.printredirect('/login.py?invalid=1')
				else:
					user = db.get_user_by_email(email)
					if len(user) != 1:
						raise ssdb.Error('Unknown')
					sessionId = db.create_session(user[0][ssdb.COLUMNS['id']])
					makehtml.printredirect('/', (('Set-Cookie', 'session={}; Secure'.format(sessionId)),))

		else:
			makehtml.printerror('405 Invalid Method', '<p><br/>Method not supported</p>')
except ssdb.Error as e:
	makehtml.printerror('500 Server Error', '<p><br/>Database error: {}</p>'.format(tools.escape(str(e))))
except:
	makehtml.printerror('500 Server Error', '<p><br/>500 Server Error</p>')

