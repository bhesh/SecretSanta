#!/usr/bin/python3
#
# Shows the assigned partner
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from include import makehtml, tools, ssdb

try:
	if tools.is_logged_in():
		HTML = ''

		user = tools.get_user()
		if not user:
			raise ssdb.Error('No user with id `{}`'.format(uid))
		partner = tools.get_partner()
		if partner:
			HTML = '<h3><br/>Welcome, {}</h3><p><br/>Your assigned partner is {} {} (Email={}).</p>'.format(
					tools.escape(user[ssdb.COLUMNS['FirstName']]), tools.escape(partner[ssdb.COLUMNS['FirstName']]),
					tools.escape(partner[ssdb.COLUMNS['LastName']]), tools.escape(partner[ssdb.COLUMNS['Email']]))
		else:
			HTML = '<p><br/>Unfortunately, the partners have not been assigned yet. Please wait for your assignment.</p>'
		print('Status: 200 OK')
		print('Content-Type: text/html')
		print('')
		print(makehtml.makehtml(HTML, makehtml.NAV_BAR['partner']))
	else:
		makehtml.printredirect('/login.py')
except ssdb.Error as e:
	makehtml.printerror('500 Server Error', '<p><br/>Database error: {}</p>'.format(tools.escape(str(e))))
except:
	makehtml.printerror('500 Server Error', '<p><br/>500 Server Error</p>')

