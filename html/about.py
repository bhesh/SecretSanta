#!/usr/bin/python3
#
# Makes the about page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from include import makehtml, tools

try:
	HTML="""<p><br/>This website was designed to make Secret Santa easy and fair. No one will know each other's target and no one will be assigned to themselves.</p>
	<p><br/>Designed by Brian Hession</p>"""

	print('Status: 200 OK')
	print('Content-Type: text/html')
	print('')
	print(makehtml.makehtml(HTML, makehtml.NAV_BAR['about']))
except:
	makehtml.printerror('500 Server Error', '<p><br/>500 Server Error</p>')

