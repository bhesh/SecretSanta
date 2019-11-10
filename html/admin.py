#!/usr/bin/python3
#
# Shows the admin page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import cgi
from include import makehtml, tools, ssdb, secretsanta

try:
	args = cgi.FieldStorage()
	db = ssdb.SSDatabase('db/secretsanta.db')

	if tools.is_logged_in():
		user = tools.get_user()
		if not user:
			raise ssdb.Error('No user with id `{}`'.format(uid))
		if db.is_admin(user[ssdb.COLUMNS['id']]):
			if tools.is_get():
				HTML = """<p><br/>Users</p>
						<div style="height:500px;width:100%;border:solid;overflow:auto;">{}</div>
						<form action="/admin.py" method="POST">
						<br/>User ID: <input type="text" name="uid"/>{}
						<input type="hidden" name="deleteuser" value="1"/>
						<input type="submit" value="Delete User"/>
						</form>
						<form action="/admin.py" method="POST">
						<input type="hidden" name="runss" value="1"/>
						<br/><input type="submit" value="Run Secret Santa"/>
						</form>
						"""
				ERROR='<font color="#a93226">{}</font><br/>'
				users = '<table style="width:100%"><tr>'
				users += '<td style="width:25%"><b>ID</b></td>'
				users += '<td style="width:25%"><b>Email</b></td>'
				users += '<td style="width:25%"><b>First Name</b></td>'
				users += '<td style="width:25%"><b>Last Name</b></td>'
				users += '</tr>'
				for user in db.get_all_users():
					users += '<tr><td style="width:25%">{}</td><td style="width:25%">{}</td><td style="width:25%">{}</td><td style="width:25%">{}</td></tr>'.format(
							user[ssdb.COLUMNS['id']], tools.escape(user[ssdb.COLUMNS['Email']]),
							tools.escape(user[ssdb.COLUMNS['FirstName']]), tools.escape(user[ssdb.COLUMNS['LastName']]))
				users += '</table>'
				error = ''
				if 'nouid' in args:
					error = ERROR.format('Must provide a user ID')
				if 'invalid' in args:
					error = ERROR.format('User ID does not exist')
				print('Status: 200 OK')
				print('Content-Type: text/html')
				print('')
				print(makehtml.makehtml(HTML.format(users, error), makehtml.NAV_BAR['account']))
			elif tools.is_post():
				if 'runss' in args:
					secretsanta.assign_partners('db/secretsanta.db')
					makehtml.printredirect('/admin.py')
				elif 'deleteuser' in args:
					if 'uid' not in args:
						makehtml.printredirect('/admin.py?nouid=1')
					else:
						user = db.get_user_by_id(args.getvalue('uid'))
						if len(user) != 1:
							makehtml.printredirect('/admin.py?invalid=1')
						else:
							db.delete_user(user[0][ssdb.COLUMNS['id']])
							makehtml.printredirect('/admin.py')
				else:
					makehtml.printredirect('/admin.py')
			else:
				makehtml.printerror('405 Invalid Method', '<p><br/>Method not supported</p>')
		else:
			makehtml.printerror('403 Unauthorized', '<p><br/>Unauthorized access</p>')
	else:
		makehtml.printerror('403 Unauthorized', '<p><br/>Unauthorized access</p>')
except ssdb.Error as e:
	makehtml.printerror('500 Server Error', '<p><br/>Database error: {}</p>'.format(tools.escape(str(e))))
except:
	makehtml.printerror('500 Server Error', '<p><br/>500 Server Error</p>')

