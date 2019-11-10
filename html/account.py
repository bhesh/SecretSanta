#!/usr/bin/python3
#
# Shows the account page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from include import makehtml, tools, ssdb

try:
	db = ssdb.SSDatabase('db/secretsanta.db')

	if tools.is_logged_in():
		user = tools.get_user()
		if not user:
			raise ssdb.Error('No user with id `{}`'.format(uid))

		email = tools.escape(user[ssdb.COLUMNS['Email']])
		firstname = tools.escape(user[ssdb.COLUMNS['FirstName']])
		lastname = tools.escape(user[ssdb.COLUMNS['LastName']])

		HTML = """<p><br/>Email: {}<br/>Name: {} {}<br/></p>
				<p><br/><a href="/updateacc.py?changepassword=1">Change Password</a> | 
				<a href="/updateacc.py?changename=1">Change Name</a></p>"""

		if db.is_admin(user[ssdb.COLUMNS['id']]):
			HTML += '<p><br/><a href="/admin.py">Admin Page</a></p>'

		print('Status: 200 OK')
		print('Content-Type: text/html')
		print('')
		print(makehtml.makehtml(HTML.format(email, firstname, lastname), makehtml.NAV_BAR['account']))
	else:
		makehtml.printredirect('/login.py')
except ssdb.Error as e:
	makehtml.printerror('500 Server Error', '<p><br/>Database error: {}</p>'.format(tools.escape(str(e))))
except:
	makehtml.printerror('500 Server Error', '<p><br/>500 Server Error</p>')

