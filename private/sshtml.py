#!/usr/bin/python3
#
# Simple http helpers
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import os, re, html, urllib.parse

# Links
LINKS = {
	'Home' : '/',
	'Account' : '/getacc.py?redirect=%2Faccount.py',
	'Groups' : '/getacc.py?redirect=%2Fgroups.py',
	'Registry' : '/getacc.py?redirect=%2Fregistry.py',
	'Support' : '/support.py',
	'About' : '/about.py'
}
DESKTOP_NAV_LINKS = ['Home', 'Groups', 'Registry', 'Support', 'About']
NAV_LINKS = ['Home', 'Account', 'Groups', 'Registry', 'Support', 'About']

# HTML Skeletons
HOME_ICON = '<i class="fas fa-gift"></i>'
BODY = '<div class="row">{data}{rightbanner}</div>'
DATA = '<div class="col-9 col-s-12"><div class="data">{}</div></div>'
MENU_BODY = '<div class="row">{menu}{data}{rightbanner}</div>'
MENU = """
<script>
function %%menuid%%Expand() {
	var x = document.getElementById("%%menuid%%");
	if (x.style.display === "block") {
		x.style.display = "none";
	} else {
		x.style.display = "block";
	}
}
</script>
<div class="col-3 col-s-12 menu">
	<div class="menuheader">
		<div class="menutitle">
			%%menutitle%%
		</div>
		<div class="menubutton">
			<button><a href="%%menubuttonlink%%">%%menubutton%%</a></button>
		</div>
	</div>
	<div class="mobileexpand">
		%%mobileactive%%
	</div>
	<div class="scrollmenu" id="%%menuid%%">
		<div class="menuitems">
			%%items%%
		</div>
	</div>
</div>"""
MENU_DATA = '<div class="col-6 col-s-12"><div class="data">{}</div></div>'
RIGHT_BANNER = """
<div class="col-3 col-s-12">
{aside}
{mobile}
	<div class="center">
		<img src="/res/secret_santa.png" style="margin: 45px 0 0 0;width: 100%;"/>
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

def buildMenu(title, menuId, buttonLink='#', buttonText='Submit', items={}, active=None):
	"""items must be dict{id : (name, link)}"""

	# Make links
	itemstr = '\n'.join(['<a href="{}">{}</a>'.format(items[k][1], items[k][0]) for k in items.keys()])

	# If active is not set
	if not active and len(items) > 0:
		active = list(items.keys())[0]

	# Set active link
	mobileactive = ''
	if len(items) > 0:
		itemstr = itemstr.replace('{}"'.format(items[active][1]), '{}" class="active"'.format(items[active][1]))
		mobileactive = '<a href="javascript:void(0);" onclick="{menuId}Expand()" class="active">{active}</a>'.format(menuId=menuId,
				active=items[active][0])

	# Make menu html
	menu = MENU.replace('%%menuid%%', menuId)
	menu = menu.replace('%%menutitle%%', title)
	menu = menu.replace('%%menubuttonlink%%', buttonLink)
	menu = menu.replace('%%menubutton%%', buttonText)
	menu = menu.replace('%%mobileactive%%', mobileactive)
	return menu.replace('%%items%%', itemstr)

def buildResources(resources={}):
	res = list()
	for r in resources.keys():
		if resources[r] == 'javascript':
			res.append('<script src="{}" type="text/javascript"></script>'.format(r))
		elif resources[r] == 'stylesheet':
			res.append('<link rel="stylesheet" href="{}"/>'.format(r))
	return '\n'.join(res)

def buildLinks(linklist, active=None, replacehome=False):
	res = '\n'.join(['<a href="{}">{}</a>'.format(LINKS[k], k) for k in linklist])
	if active:
		res = res.replace('>{}<'.format(active), ' class="active">{}<'.format(active))
	if replacehome:
		res = res.replace('Home', HOME_ICON)
	return res

def buildDesktopNavLinks(active=None):
	return buildLinks(DESKTOP_NAV_LINKS, active, True)

def buildNavLinks(active=None):
	return buildLinks(NAV_LINKS, active, False)

def buildAccountLinks(loggedin=False, redirect=None):
	html = """
		<a href="/getacc.py?redirect=%2Faccount.py" class="icon"><i class="fas fa-user-circle"></i></a>
		<a href="{}">{}</a>
	"""
	if loggedin:
		if redirect:
			return html.format('/signout.py?redirect={}'.format(urllib.parse.quote_plus(str(redirect), safe='')), 'Sign out')
		else:
			return html.format('/signout.py', 'Sign out')
	elif redirect:
		return html.format('/getacc.py?redirect={}'.format(urllib.parse.quote_plus(str(redirect), safe='')), 'Sign in')
	else:
		return html.format('/getacc.py', 'Sign in')

def buildBody(data='', aside='', mobile=''):
	datahtml = DATA.format(data)
	rightbanner = RIGHT_BANNER.format(aside=ASIDE.format(aside), mobile=MOBILE.format(mobile))
	return BODY.format(data=datahtml, rightbanner=rightbanner)

def buildMenuBody(menu='', data='', aside='', mobile=''):
	datahtml = MENU_DATA.format(data)
	rightbanner = RIGHT_BANNER.format(aside=ASIDE.format(aside), mobile=MOBILE.format(mobile))
	return MENU_BODY.format(menu=menu, data=datahtml, rightbanner=rightbanner)

def buildError(code):
	try:
		with open('error/{}.html'.format(code), 'r') as f:
			return f.read()
	except FileNotFoundError:
		with open('error/50x.html', 'r') as f:
			return f.read()

if __name__ == '__main__':
	print(buildError())

