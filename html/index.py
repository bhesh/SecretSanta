#!/usr/bin/python3
#
# Makes the index page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from include import makehtml, tools

try:
	HTML="""<p><br/><img src="/res/secretsanta.png" alt="Secret Santa" width="50%"/></p>
	<p>Click <a href="/register.py">here</a> to register</p>"""

	print('Status: 200 OK')
	print('Content-Type: text/html')
	print('')
	print(makehtml.makehtml(HTML, makehtml.NAV_BAR['home']))
except:
	makehtml.printerror('500 Server Error', '<p><br/>500 Server Error</p>')

