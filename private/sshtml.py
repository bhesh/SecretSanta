#!/usr/bin/python3
#
# Simple http helpers
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import os, re, html

# Links
LINKS = {
	'Home' : '/',
	'Accout' : '/getacc.py?referer=%2Faccount.py',
	'Groups' : '/getacc.py?referer=%2Fgroups.py',
	'Registry' : '/getacc.py?referer=%2Fregistry.py',
	'Support' : '/support.py',
	'About' : '/about.py'
}
DESKTOP_NAV_LINKS = ['Home', 'Groups', 'Registry', 'Support', 'About']
NAV_LINKS = ['Home', 'About', 'Groups', 'Registry', 'Support', 'About']

# HTML Skeletons
HOME_ICON = '<i class="fas fa-gift"></i>'
BODY = '<div class="row">{data}{rightbanner}</div>'
DATA = '<div class="col-9 col-s-12"><div class="data">{}</div></div>'
RIGHT_BANNER = """
<div class="col-3 col-s-12">
{aside}
{mobile}
	<div class="center">
		<img src="res/secret_santa.png" style="margin: 45px 0 0 0;width: 100%;"/>
		<p class="footnote">Image owned by Pratik Patil</p>
	</div>
</div>
"""
ASIDE = '<div class="aside">{}</div>'
MOBILE = '<div class="mobile">{}</div>'

# Redirect HTTP body
REDIRECT_HTML = """<!DOCTYPE html>
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

def escape(message):
	return html.escape(message)

def unescape(message):
	return html.unescape(message)

def buildPage(htmlfile, replace=None):
	with open(os.path.join(HTML_RES, htmlfile)) as f:
		page = f.read()
		if replace:
			for k in replace.keys():
				page = page.replace('%%{}%%'.format(k), replace[k])
		page = re.sub(r'%%.*%%', '', page) # Remove stragglers
		return page

def buildContainerPage(replace=None):
	return buildPage('container.html', replace)

def buildResources(resources={}):
	res = list()
	for r in resources.keys():
		if resources[r] == 'javascript':
			res.append('<script src="{}"/>'.format(r))
		elif resources[r] == 'stylesheet':
			res.append('<link rel="stylesheet" href="{}"/>'.format(r))
	return '\n'.join(res)

def buildLinks(linklist, active=None, replacehome=False):
	res = '\n'.join(['<a href="{}">{}</a>'.format(k, LINKS[k]) for k in linklist])
	if active:
		res.replace('>{}<'.format(active), ' class="active">{}<'.format(active))
	if replacehome:
		res.replace('Home', HOME_ICON)
	return res

def buildDesktopNavLinks(active=None):
	return buildLinks(DESKTOP_NAV_LINKS, active, True)

def buildNavLinks(active=None):
	return buildLinks(NAV_LINKS, active, False)

def buildAccountLinks(loggedin=False):
	html = """
		<a href="{}" class="icon"><i class="fas fa-user-circle"></i></a>
		<a href="{}">{}</a>
	"""
	if loggedin:
		return html.format('/getacc.py?referer=%2Faccount.py', '/signout.py', 'Sign out')
	else:
		return html.format('/getacc.py?referer=%2Faccount.py', '/signin.py', 'Sign in')

def buildBody(data='', aside='', mobile=''):
	datahtml = DATA.format(data)
	rightbanner = RIGHT_BANNER.format(aside=ASIDE.format(aside), mobile=MOBILE.format(mobile))
	return BODY.format(data=datahtml, rightbanner=rightbanner)

if __name__ == '__main__':
	replace = {
		'desktopNavLinks' : buildDesktopNavLinks('Home'),
		'navLinks' : buildNavLinks('Home'),
		'accountLinks' : buildAccountLinks(),
		'body' : buildBody('<p>Testing</p>', '<p>Testing</p>', '<button>Testing</button>')
	}
	print(buildContainerPage(replace))

