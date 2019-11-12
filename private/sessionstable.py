#!/usr/bin/python3
#
# Secret Santa Database
#
# Interface to the secret santa database
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import sys, random, datetime
import ssdb
from ssdb import Error

SESSIONS_SCHEMA = ssdb.SSTableSchema('sessions')
SESSIONS_SCHEMA.add_column(ssdb.SSColumnSchema('ssid', 'nvarchar[320]', ('PRIMARY KEY',)))
SESSIONS_SCHEMA.add_column(ssdb.SSColumnSchema('uid', 'integer', ('NOT NULL',)))
SESSIONS_SCHEMA.add_column(ssdb.SSColumnSchema('timestamp', 'integer', ('NOT NULL',)))
SESSIONS_SCHEMA.add_column(ssdb.SSColumnSchema('expiration', 'integer', ('NOT NULL',)))

class SSSessions(object):

	def __init__(self, dbfile):
		self.db = ssdb.SSDatabase(dbfile)
		self.create_table()

	def create_table(self):
		self.db.create_table(SESSIONS_SCHEMA)

	def drop_table(self):
		self.db.drop_table(SESSIONS_SCHEMA)

	def __create_ssid(self, length):
		ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
		ssid = list()
		for i in range(length):
			ssid.append(random.choice(ALPHABET))
		return ''.join(ssid)

	def get_all_sessions(self):
		statement = 'SELECT * FROM {}'.format(SESSIONS_SCHEMA.name)
		return self.db.execute(statement)

	def get_session(self, ssid, cols=None):
		columns = '*'
		if cols:
			columns = ','.join(cols)
		statement = 'SELECT {} FROM {} WHERE ssid=?'.format(columns, SESSIONS_SCHEMA.name)
		res = self.db.execute_prepared(statement, ssid)
		if len(res) == 0:
			return None
		if len(res) > 1:
			raise Error('returned more than one session')
		return res[0]

	def update_session(self, ssid):
		self.clean_sessions()
		statement = 'UPDATE {} SET timestamp=? WHERE ssid=?'.format(SESSIONS_SCHEMA.name)
		self.db.execute_prepared(statement, datetime.datetime.utcnow().timestamp(), ssid)

	def create_session(self, uid, ttl=86400):
		self.clean_sessions()

		# Create statement
		cols = SESSIONS_SCHEMA.columns()
		statement = 'INSERT INTO {} ({}) VALUES ({})'.format(SESSIONS_SCHEMA.name,
				','.join(cols), ','.join(['?' for c in cols]))

		# Attempt creating a session (max 5 times)
		ssid = None
		for i in range(5):
			try:
				ssid = self.__create_ssid(32)
				timestamp = datetime.datetime.utcnow().timestamp()
				self.db.execute_prepared(statement, ssid, uid, timestamp, timestamp + ttl)
				break
			except Error as e:
				# Most likely a unique constraint error
				print('Error creating session: {}', e, file=sys.stderr)
				ssid = None

		# Creating a session failed
		if not ssid:
			raise Error('Could not create a session')
		return ssid

	def delete_session(self, ssid):
		session = self.get_session(ssid, ['ssid'])
		if not session:
			return
		statement = 'DELETE FROM {} WHERE ssid=?'.format(SESSIONS_SCHEMA.name)
		self.db.execute_prepared(statement, ssid)

	def clean_sessions(self, time=1800):
		now = datetime.datetime.utcnow().timestamp()
		statement = 'DELETE FROM {} WHERE timestamp<? OR expiration<?'.format(SESSIONS_SCHEMA.name)
		self.db.execute_prepared(statement, now - time, now)

	def is_valid(self, ssid, time=1800):
		self.clean_sessions(time)
		session = self.get_session(ssid)
		return session

##########################################################################
# TESTING
##########################################################################

if __name__ == '__main__':
	import time
	print('='*80)
	print('Create database/table')
	print('='*80)
	print(SESSIONS_SCHEMA)
	sessions = SSSessions(DATABASE)
	print('='*80)
	print('Drop table')
	print('='*80)
	sessions.drop_table()
	print('='*80)
	print('Create table')
	print('='*80)
	sessions.create_table()
	print('='*80)
	print('Create sessions')
	print('='*80)
	ssids = list()
	ssids.append(sessions.create_session(1))
	ssids.append(sessions.create_session(2))
	ssids.append(sessions.create_session(3))
	ssids.append(sessions.create_session(4))
	ssids.append(sessions.create_session(5))
	ssids.append(sessions.create_session(1))
	ssids.append(sessions.create_session(2))
	ssids.append(sessions.create_session(3))
	ssids.append(sessions.create_session(4))
	ssids.append(sessions.create_session(5))
	for ssid in ssids:
		row = sessions.get_session(ssid)
		if not row:
			print('Failed for session `{}`'.format(ssid))
		print(row)
	print('='*80)
	print('Update sessions')
	print('='*80)
	time.sleep(3)
	for ssid in ssids:
		sessions.update_session(ssid)
	for session in sessions.get_all_sessions():
		print(session)
	print('='*80)
	print('Check timeouts')
	print('='*80)
	for ssid in ssids:
		if sessions.is_valid(ssid, 5):
			print('Success for session `{}`'.format(ssid))
		else:
			print('Failed for session `{}`'.format(ssid))
	time.sleep(6)
	for ssid in ssids:
		if not sessions.is_valid(ssid, 5):
			print('Success for session `{}`'.format(ssid))
		else:
			print('Failed for session `{}`'.format(ssid))
	print('='*80)
	print('Check expirations')
	print('='*80)
	ssids.append(sessions.create_session(1, 3))
	ssids.append(sessions.create_session(2, 3))
	ssids.append(sessions.create_session(3, 3))
	ssids.append(sessions.create_session(4, 3))
	ssids.append(sessions.create_session(5, 3))
	time.sleep(4)
	for ssid in ssids:
		if not sessions.is_valid(ssid):
			print('Success for session `{}`'.format(ssid))
		else:
			print('Failed for session `{}`'.format(ssid))
	print('='*80)
	print('Clean sessions')
	print('='*80)
	sessions.clean_sessions(5)
	print(sessions.get_all_sessions())

