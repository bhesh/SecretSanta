#!/usr/bin/python3
#
# Session management
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import sshttp, userstable, sessionstable

users = userstable.SSUsers(DATABASE)
sessions = sessionstable.SSSessions(DATABASE)

def has_session():
	return sshttp.has_cookie()

def session_is_valid():
	return has_session() and sessions.is_valid(sshttp.get_cookie())

def get_session():
	if session_is_valid():
		session = sessions.get_session(sshttp.get_cookie())
		if session:
			sessions.update_session(sshttp.get_cookie())
		return session
	return None

def get_user():
	session = get_session()
	if session:
		return users.get_user_by_id(sessionstable.SESSIONS_SCHEMA.get(session, 'ssid'))
	return None

def create_session(uid):
	return sessions.create_session(uid)

def delete_session():
	if has_session():
		sessions.delete_session(sshttp.get_cookie())

