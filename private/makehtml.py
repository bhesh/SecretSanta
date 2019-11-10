#!/usr/bin/python3
#
# Simple dynamic page generator
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import tools, ssdb

NAV_BAR = {'none': -1, 'home': 0, 'partner': 1, 'account': 2, 'about': 3}
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width">
	<meta name="description" content="Hession Secret Santa">
	<meta name="author" content="Brian Hession">
	<link rel="stylesheet" href="/css/style.css" />
	<title>Hession Secret Santa</title>
</head>
<body>
	<header>
		<section id="banner">
			<table><tr>
				<td id="banner-title" style="width: 100%;">
					<h1>Secret Santa</h1>
					<h3>2019 Hession Edition</h3>
				</td>
				<td id="banner-links">
					<a href="/{}">{}</a>
				</td>
			</tr></table>
		</section>
		<section id="nav">
			<ul>
				<li class="{}"><a href="/">HOME</a></li>
				<li class="{}"><a href="/partner.py">PARTNER</a></li>
				<li class="{}"><a href="/account.py">ACCOUNT</a></li>
				<li class="{}"><a href="/about.py">ABOUT</a></li>
			</ul>
		</section>
	</header>
	<section id="data">
		<p style="font-size: 32px">Hession Family Secret Santa</p>
		{}
	</section>
	<footer>
		<section id="credits">
			<p>Created by Brian Hession (c) 2019</p>
		</section>
	</footer>
</body>
</html>
"""

REDIRECT_HTML="""<!DOCTYPE html>
<html>
<head>
	<title>You are about to be redirected</title>
</head>
<body>
	<h1>302 Found</h1>
	<p>You are about to be redirected</p>
</body>
</html>
"""

def makehtml(data, navbar=-1):
	inserts = ['getacc.py', 'login', 'nav-button', 'nav-button', 'nav-button', 'nav-button', data]
	try:
		db = ssdb.SSDatabase('db/secretsanta.db')
		if navbar >= 0 and navbar <= 3:
			inserts[navbar + 2] = 'nav-button-active'
		if tools.is_logged_in():
			inserts[0] = 'logout.py'
			inserts[1] = 'logout'
	except:
		pass
	return HTML_PAGE.format(*inserts)

def printerror(status, message):
	print('Status: {}'.format(status))
	print('Content-Type: text/html')
	print('')
	print(makehtml(message))

def printredirect(location, headers=()):
	print('Status: 302 Found')
	print('Location: {}'.format(location))
	print('Content-Type: text/html')
	for k, v in headers:
		print('{}: {}'.format(k, v))
	print('')
	print(REDIRECT_HTML)

if __name__ == '__main__':
	print(makehtml('<p>Testing</p>'))
	print(makehtml('<p>Testing</p>', NAV_BAR['home']))
	print(makehtml('<p>Testing</p>', NAV_BAR['partner'], True))
	print(makehtml('<p>Testing</p>', NAV_BAR['account']))
	print(makehtml('<p>Testing</p>', NAV_BAR['about'], True))
	print(makehtml('<p>Testing</p>', NAV_BAR['none']))

