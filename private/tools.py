#!/usr/bin/python3
#
# Common tools
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import os, html
from include import ssdb

def is_get():
	return os.environ.get('REQUEST_METHOD', '') == 'GET'

def is_post():
	return os.environ.get('REQUEST_METHOD', '') == 'POST'

def has_cookies():
	return 'HTTP_COOKIE' in os.environ

def has_cookie():
	return has_cookies() and 'session' in get_cookies()

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
	if 'session' in cookies:
		return cookies['session']
	return None

def is_logged_in():
	db = ssdb.SSDatabase('db/secretsanta.db')
	if has_cookie() and db.is_valid(get_cookie()):
		db.update_session(get_cookie())
		return True
	return False

def get_session():
	if is_logged_in():
		db = ssdb.SSDatabase('db/secretsanta.db')
		session = db.get_session(get_cookie())
		if len(session) != 1:
			raise ssdb.Error('No session')
		return session[0]
	return None

def get_user():
	session = get_session()
	if session:
		db = ssdb.SSDatabase('db/secretsanta.db')
		user = db.get_user_by_id(session[ssdb.SESSION_COLS['uid']])
		if len(user) != 1:
			raise ssdb.Error('No user')
		return user[0]
	return None

def get_partner():
	user = get_user()
	if user:
		pid = user[ssdb.COLUMNS['Partner']]
		if pid:
			db = ssdb.SSDatabase('db/secretsanta.db')
			partner = db.get_user_by_id(pid)
			if len(partner) != 1:
				raise ssdb.Error('No partner')
			return partner[0]
	return None

def escape(message):
	return html.escape(message)

def unescape(message):
	return html.unescape(message)

