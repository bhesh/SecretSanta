#!/usr/bin/python3
#
# Logs out the user
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from include import tools, makehtml, ssdb

try:
	db = ssdb.SSDatabase('db/secretsanta.db')

	HTML='<p><br/>You have been logged out. Please close the browser.</p>'

	if tools.is_logged_in():
		db.delete_session(tools.get_cookie())

	print('Content-Type: text/html')
	print('')
	print(makehtml.makehtml(HTML))
except ssdb.Error as e:
	makehtml.printerror('500 Server Error', '<p><br/>Database error: {}</p>'.format(tools.escape(str(e))))
except:
	makehtml.printerror('500 Server Error', '<p><br/>500 Server Error</p>')

