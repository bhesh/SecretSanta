#!/usr/bin/python3
#
# Secret Santa Database
#
# Interface to the secret santa database
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import sqlite3, random, hashlib, datetime, time
from sqlite3 import Error

COLUMNS = {'id' : 0, 'Email' : 1, 'FirstName' : 2, 'LastName' : 3, 'Password' : 4, 'PasswordSalt' : 5, 'Admin' : 6, 'Partner' : 7}
SESSION_COLS = {'sessionId': 0, 'uid' : 1, 'timestamp' : 2}

class SSDatabase(object):

	def __init__(self, dbfile):
		self.dbfile = dbfile
		self.create_tables()

	def create_tables(self):
		sqlcommand1 = """CREATE TABLE IF NOT EXISTS users (
							id integer PRIMARY KEY AUTOINCREMENT,
							Email nvarchar(320) NOT NULL,
							FirstName text NOT NULL,
							LastName text NOT NULL,
							Password nvarchar(320) NOT NULL,
							PasswordSalt nvarchar(320) NOT NULL,
							Admin BOOLEAN NOT NULL,
							Partner integer
						);"""
		sqlcommand2 = """CREATE TABlE IF NOT EXISTS sessions (
							sessionId nvarchar(32) PRIMARY KEY,
							uid integer NOT NULL,
							timestamp BIGINT NOT NULL
						);"""
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand1)
			c.execute(sqlcommand2)

	def drop_tables(self):
		sqlcommand1 = 'DROP TABLE users;'
		sqlcommand2 = 'DROP TABLE sessions;'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand1)
			c.execute(sqlcommand2)

	def drop_table(self, table):
		if table != 'users' and table != 'sessions':
			raise Error('Invalid table')
		sqlcommand = 'DROP TABLE {};'.format(table)
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand)

	def __create_salt(self, length):
		ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
		salt = list()
		for i in range(length):
			salt.append(random.choice(ALPHABET))
		return ''.join(salt)

	def create_user(self, email, firstname, lastname, password):
		row = self.get_user_by_email(email)
		if len(row) != 0:
			return False

		# Create salt and hash password
		salt = str(self.__create_salt(32))
		phash = str(hashlib.sha256(bytes(password + salt, 'UTF-8')).hexdigest())

		# Insert the values
		sqlcommand = 'INSERT INTO users (Email, FirstName, LastName, Password, PasswordSalt, Admin) VALUES (?,?,?,?,?,?)'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (email, firstname, lastname, phash, salt, False))
		return True

	def set(self, table, uid, key, value):
		if table != 'users' and table != 'sessions':
			raise Error('Invalid table')
		if key not in COLUMNS and key not in SESSION_COLS:
			raise Error('Invalid key')
		sqlcommand = 'UPDATE {} SET {}=? WHERE id=?'.format(table, key)
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (value, uid))

	def set_password(self, uid, password):
		row = self.get_user_by_id(uid)
		if len(row) != 1:
			raise Error('Search by id `{}` did not return exactly 1 entry'.format(uid))

		# Create salt and hash password
		salt = str(self.__create_salt(32))
		phash = str(hashlib.sha256(bytes(password + salt, 'UTF-8')).hexdigest())

		# Insert the values
		sqlcommand = 'UPDATE users SET Password=?, PasswordSalt=? WHERE id=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (phash, salt, uid))

	def is_admin(self, uid):
		user = self.get_user_by_id(uid)
		if len(user) != 1:
			raise Error('Search by id `{}` did not return exactly 1 entry'.format(uid))
		return bool(user[0][COLUMNS['Admin']])

	def set_admin(self, uid):
		user = self.get_user_by_id(uid)
		if len(user) != 1:
			raise Error('Search by id `{}` did not return exactly 1 entry'.format(uid))
		sqlcommand = 'UPDATE users SET Admin=? WHERE id=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (True, uid))

	def remove_admin(self, uid):
		user = self.get_user_by_id(uid)
		if len(user) != 1:
			raise Error('Search by id `{}` did not return exactly 1 entry'.format(uid))
		sqlcommand = 'UPDATE users SET Admin=? WHERE id=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (False, uid))

	def delete_user(self, uid):
		row = self.get_user_by_id(uid)
		if len(row) == 0:
			raise Error('Email does not exist')
		sqlcommand = 'DELETE FROM users WHERE id=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (uid,))

	def get_all_users(self):
		sqlcommand = 'SELECT * FROM users'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand)
			return c.fetchall()

	def get_id(self, email):
		user = self.get_user_by_email(email)
		if len(user) != 1:
			raise Error('Search by email `{}` did not return exactly 1 entry'.format(email))
		return user[0][COLUMNS['id']]

	def get_user_by_id(self, uid):
		sqlcommand = 'SELECT * FROM users WHERE id=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (uid,))
			return c.fetchall()

	def get_user_by_email(self, email):
		sqlcommand = 'SELECT * FROM users WHERE Email=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (email,))
			return c.fetchall()

	def validate_user(self, email, password):
		user = self.get_user_by_email(email)
		if len(user) != 1:
			return None
		salt = str(user[0][COLUMNS['PasswordSalt']])
		phash = str(hashlib.sha256(bytes(password + salt, 'UTF-8')).hexdigest())
		check = str(user[0][COLUMNS['Password']])
		return phash == check

	def set_firstname(self, uid, firstname):
		row = self.get_user_by_id(uid)
		if len(row) != 1:
			raise Error('Search by id `{}` did not return exactly 1 entry'.format(uid))
		sqlcommand = 'UPDATE users SET FirstName=? WHERE id=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (firstname, uid))

	def set_lastname(self, uid, lastname):
		row = self.get_user_by_id(uid)
		if len(row) != 1:
			raise Error('Search by id `{}` did not return exactly 1 entry'.format(uid))
		sqlcommand = 'UPDATE users SET LastName=? WHERE id=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (lastname, uid))

	def set_partner(self, uid, pid):
		row = self.get_user_by_id(uid)
		if len(row) != 1:
			raise Error('Search by id `{}` did not return exactly 1 entry'.format(uid))
		row = self.get_user_by_id(pid)
		if len(row) != 1:
			raise Error('Search by id `{}` did not return exactly 1 entry'.format(pid))
		sqlcommand = 'UPDATE users SET Partner=? WHERE id=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (pid, uid))

	def get_partner(self, uid):
		user = self.get_user_by_id(uid)
		if len(user) != 1:
			raise Error('Search by id `{}` did not return exactly 1 entry'.format(uid))
		pid = user[0][COLUMNS['Partner']]
		if not pid:
			return None
		partner = self.get_user_by_id(pid)
		if len(partner) != 1:
			raise Error('Search by id `{}` did not return exactly 1 entry'.format(pid))
		return (partner[0][COLUMNS['Email']], partner[0][COLUMNS['FirstName']], partner[0][COLUMNS['LastName']])

	def get_all_sessions(self):
		sqlcommand = 'SELECT * FROM sessions'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand)
			return c.fetchall()

	def get_session(self, sessionId):
		sqlcommand = 'SELECT * FROM sessions WHERE sessionId=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (sessionId,))
			return c.fetchall()

	def update_session(self, sessionId):
		sqlcommand = 'UPDATE sessions SET timestamp=? WHERE sessionId=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (datetime.datetime.now().timestamp(), sessionId))

	def create_session(self, uid):
		self.clean_sessions()
		sessionId = None
		while True:
			sessionId = self.__create_salt(32)
			if not sessionId:
				raise Error('Error creating sessionId')
			row = self.get_session(sessionId)
			if len(row) == 0:
				break
		sqlcommand = 'INSERT INTO sessions (sessionId, uid, timestamp) VALUES (?,?,?)'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (sessionId, uid, datetime.datetime.now().timestamp()))
		return sessionId

	def delete_session(self, sessionId):
		session = self.get_session(sessionId)
		if len(session) != 1:
			return
		sqlcommand = 'DELETE FROM sessions WHERE sessionId=?'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(sqlcommand, (sessionId,))

	def clean_sessions(self, time=1800):
		for session in self.get_all_sessions():
			now = datetime.datetime.now().timestamp()
			if now - session[SESSION_COLS['timestamp']] >= time:
				self.delete_session(session[2])

	def is_valid(self, sessionId, time=1800):
		self.clean_sessions()
		session = self.get_session(sessionId)
		if len(session) != 1:
			return False
		return True

##########################################################################
# TESTING
##########################################################################

if __name__ == '__main__':
	print('='*80)
	print('Create database')
	print('='*80)
	db = SSDatabase('test.db')
	print('='*80)
	print('Drop table')
	print('='*80)
	db.drop_tables()
	print('='*80)
	print('Create table')
	print('='*80)
	db.create_tables()
	print('='*80)
	print('Create users')
	print('='*80)
	db.create_user('test1@test.com', 'George', 'Washington', 'password')
	db.create_user('test2@test.com', 'John', 'Adams', 'password')
	db.create_user('test3@test.com', 'Thomas', 'Jefferson', 'password')
	db.create_user('test4@test.com', 'James', 'Madison', 'password')
	db.create_user('test5@test.com', 'James', 'Monroe', 'password')
	print('='*80)
	print('Check admin')
	print('='*80)
	for user in db.get_all_users():
		if db.is_admin(user[COLUMNS['id']]):
			print('Failed for user `{}`'.format(user))
		else:
			print('Successful for user `{}`'.format(user))
	print('='*80)
	print('Set admin')
	print('='*80)
	for user in db.get_all_users():
		db.set_admin(user[COLUMNS['id']])
	for user in db.get_all_users():
		print(user)
	print('='*80)
	print('Check admin')
	print('='*80)
	for user in db.get_all_users():
		if not db.is_admin(user[COLUMNS['id']]):
			print('Failed for user `{}`'.format(user))
		else:
			print('Successful for user `{}`'.format(user))
	print('='*80)
	print('Remove admin')
	print('='*80)
	for user in db.get_all_users():
		db.remove_admin(user[COLUMNS['id']])
	for user in db.get_all_users():
		print(user)
	print('='*80)
	print('Set partners')
	print('='*80)
	db.set_partner(1, 2)
	db.set_partner(2, 3)
	db.set_partner(3, 4)
	db.set_partner(4, 5)
	db.set_partner(5, 1)
	for user in db.get_all_users():
		print(user)
	print('='*80)
	print('SQL Injection Test')
	print('='*80)
	try:
		print(db.get_user_by_id('1; DROP TABLE users; --'))
	except:
		pass
	try:
		print(db.get_user_by_email('test@test.com\'; DROP TABLE users; --'))
	except:
		pass
	try:
		print(db.get_user_by_id('1; UPDATE users SET Admin=1; --'))
	except:
		pass
	try:
		print(db.get_user_by_email('test@test.com\'; UPDATE users SET Admin=1; --'))
	except:
		pass
	for user in db.get_all_users():
		print(user)
	print('='*80)
	print('Change passwords')
	print('='*80)
	for user in db.get_all_users():
		db.set_password(user[COLUMNS['id']], 'newpassword')
	for user in db.get_all_users():
		print(user)
	print('='*80)
	print('Validate users')
	print('='*80)
	for user in db.get_all_users():
		if db.validate_user(user[COLUMNS['Email']], 'password') != True:
			print('Verification failed for `{}`'.format(user))
			continue
		if db.validate_user(user[COLUMNS['Email']], 'bad') != False:
			print('Verification failed for `{}`'.format(user))
			continue
		print('Verification successful for `{}`'.format(user))
	print('='*80)
	print('Getting partners')
	print('='*80)
	for user in db.get_all_users():
		partner = db.get_partner(user[COLUMNS['id']])
		print('User `{}` has partner `{}`'.format(user, partner))
	print('='*80)
	print('Insert duplicates')
	print('='*80)
	for user in db.get_all_users():
		try:
			db.create_user(user[COLUMNS['Email']], 'test', 'test', 'test')
			print('Failed for email `{}`'.format(user[COLUMNS['Email']]))
		except:
			print('Successful error for email `{}`'.format(user[COLUMNS['Email']]))
	print('='*80)
	print('Delete users')
	print('='*80)
	for user in db.get_all_users():
		db.delete_user(user[COLUMNS['id']])
	print(db.get_all_users())
	print('='*80)
	print('Delete unknown user')
	print('='*80)
	try:
		db.delete_user(1)
		print('Failed')
	except:
		print('Successful error')
	print('='*80)
	print('Create sessions')
	print('='*80)
	sessions = list()
	sessions.append(db.create_session(1))
	sessions.append(db.create_session(2))
	sessions.append(db.create_session(3))
	sessions.append(db.create_session(4))
	sessions.append(db.create_session(5))
	sessions.append(db.create_session(1))
	sessions.append(db.create_session(2))
	sessions.append(db.create_session(3))
	sessions.append(db.create_session(4))
	sessions.append(db.create_session(5))
	for session in sessions:
		row = db.get_session(session)
		if len(row) != 1:
			print('Failed for session `{}`'.format(session))
		print(row[0])
	print('='*80)
	print('Update sessions')
	print('='*80)
	time.sleep(3)
	for session in sessions:
		db.update_session(session)
	for session in db.get_all_sessions():
		print(session)
	print('='*80)
	print('Check expirations')
	print('='*80)
	for session in sessions:
		if db.is_valid(session, 5):
			print('Failed for session `{}`'.format(session))
		else:
			print('Success for session `{}`'.format(session))
	time.sleep(6)
	for session in sessions:
		if not db.is_valid(session, 5):
			print('Failed for session `{}`'.format(session))
		else:
			print('Success for session `{}`'.format(session))
	print('='*80)
	print('Clean sessions')
	print('='*80)
	db.clean_sessions(5)
	print(db.get_all_sessions())

