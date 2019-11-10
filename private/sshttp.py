#!/usr/bin/python3
#
# Simple http helpers
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import os, sys
from http import HTTPStatus
import sshtml

def is_get():
	return os.environ.get('REQUEST_METHOD', '') == 'GET'

def is_post():
	return os.environ.get('REQUEST_METHOD', '') == 'POST'

def has_cookies():
	return 'HTTP_COOKIE' in os.environ

def has_referer():
	return 'HTTP_REFERER' in os.environ

def get_referer():
	if has_referer():
		return os.environ['HTTP_REFERER']
	return None

def has_cookie():
	return has_cookies() and 'ssid' in get_cookies()

def get_cookies():
	if has_cookies():
		clist = str(os.environ['HTTP_COOKIE']).split(';')
		cookies = dict()
		for c in clist:
			if '=' in c:
				key, val = c.strip().split('=', 1)
				cookies[key] = val
			else:
				cookies[''] = c.strip()
			return cookies
	else:
		return None

def get_cookie():
	cookies = get_cookies()
	if 'ssid' in cookies:
		return cookies['ssid']
	return None

def sendresponse(code, content_type, headers={}, body=None):
	status = HTTPStatus(code)
	print('Status: {} {}'.format(status.value, status.phrase))
	print('Content-Type: {}'.format(content_type))
	for k in headers:
		print('{}: {}'.format(k, headers[k]))
	print('')
	if body:
		print(body)

def senderror(code):
	sendresponse(code, 'text/html', body=sshtml.buildPage('error.html'))

def send200(html, headers={}):
	sendresponse(200, 'text/html', headers, html)

def send302(location, referer=None, headers={}):
	sendheaders = headers
	if referer:
		sendheaders['Referer'] = referer
	sendresponse(302, 'text/html', sendheaders, sshtml.REDIRECT_HTML)

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print('Usage: {} <status code> <htmlpage> [headerkey=headerval...]')
	else:
		code = sys.argv[1]
		page = sys.argv[2]
		headers = {}
		for s in sys.argv[3:]:
			k, v = s.split('=', 1)
			headers[k] = v
		sendresponse(int(code), 'text/html', headers, sshtml.buildPage(page))

