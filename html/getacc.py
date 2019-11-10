#!/usr/bin/python3
#
# Gets the account information
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from include import tools, makehtml

try:
	if tools.is_logged_in():
		makehtml.printredirect('/')
	else:
		makehtml.printredirect('/login.py')
except:
	makehtml.printerror('500 Server Error', '<p><br/>500 Server Error</p>')

