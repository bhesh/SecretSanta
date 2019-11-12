#!/usr/bin/python3
#
# Users Table
#
# Interface to the secret santa database
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import random, hashlib
import ssdb
from ssdb import Error

USERS_SCHEMA = ssdb.SSTableSchema('users')
USERS_SCHEMA.add_column(ssdb.SSColumnSchema('id', 'integer', ('PRIMARY KEY', 'AUTOINCREMENT')))
USERS_SCHEMA.add_column(ssdb.SSColumnSchema('email', 'nvarchar[320]', ('UNIQUE', 'NOT NULL',)))
USERS_SCHEMA.add_column(ssdb.SSColumnSchema('name', 'nvarchar[320]', ('NOT NULL',)))
USERS_SCHEMA.add_column(ssdb.SSColumnSchema('password', 'nvarchar[320]', ('NOT NULL',)))
USERS_SCHEMA.add_column(ssdb.SSColumnSchema('salt', 'nvarchar[320]', ('NOT NULL',)))
USERS_SCHEMA.add_column(ssdb.SSColumnSchema('admin', 'boolean', ('NOT NULL',)))

class SSUsers(object):

	def __init__(self, dbfile):
		self.db = ssdb.SSDatabase(dbfile)
		self.create_table()

	def create_table(self):
		self.db.create_table(USERS_SCHEMA)

	def drop_table(self):
		self.db.drop_table(USERS_SCHEMA)

	def __create_salt(self, length):
		ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
		salt = list()
		for i in range(length):
			salt.append(random.choice(ALPHABET))
		return ''.join(salt)

	def get_all_users(self):
		return self.db.execute('SELECT * FROM {}'.format(USERS_SCHEMA.name))

	def get_user_by_email(self, email, cols=None):
		columns = '*'
		if cols:
			columns = ','.join(cols)
		statement = 'SELECT {} FROM {} WHERE email=?'.format(columns, USERS_SCHEMA.name)
		res = self.db.execute_prepared(statement, email)
		if len(res) == 0:
			return None
		elif len(res) > 1:
			raise Error('returned more than one user')
		return res[0]

	def get_user_by_id(self, uid, cols=None):
		columns = '*'
		if cols:
			columns = ','.join(cols)
		statement = 'SELECT {} FROM {} WHERE id=?'.format(columns, USERS_SCHEMA.name)
		res = self.db.execute_prepared(statement, uid)
		if len(res) == 0:
			return None
		elif len(res) > 1:
			raise Error('returned more than one user')
		return res[0]

	def create_user(self, email, name, password, admin=False):
		# Create salt and hash password
		salt = str(self.__create_salt(32))
		phash = str(hashlib.sha256(bytes(password + salt, 'UTF-8')).hexdigest())

		# Insert the values
		data = {
			'email' : email,
			'name' : name,
			'password' : phash,
			'salt' : salt,
			'admin' : False
		}
		return self.db.insert_and_retrieve(USERS_SCHEMA.name, data)

	def delete_user(self, uid):
		statement = 'DELETE FROM {} WHERE id=?'.format(USERS_SCHEMA.name)
		self.db.execute_prepared(statement, uid)

	def set_password(self, uid, password):
		# Create salt and hash password
		salt = str(self.__create_salt(32))
		phash = str(hashlib.sha256(bytes(password + salt, 'UTF-8')).hexdigest())

		# Insert the values
		statement = 'UPDATE {} SET password=?, salt=? WHERE id=?'.format(USERS_SCHEMA.name)
		self.db.execute_prepared(statement, phash, salt, uid)

	def get_id(self, email):
		user = self.get_user_by_email(email, ['id'])
		if not user:
			raise Error('user does not exist')
		return user[0]

	def validate_user(self, email, password):
		user = self.get_user_by_email(email, ['password', 'salt'])
		if not user:
			return None
		salt = str(user[1])
		phash = str(hashlib.sha256(bytes(password + salt, 'UTF-8')).hexdigest())
		check = str(user[0])
		return phash == check

	def set_name(self, uid, name):
		statement = 'UPDATE {} SET name=? WHERE id=?'.format(USERS_SCHEMA.name)
		self.db.execute_prepared(statement, name, uid)

	def is_admin(self, uid):
		user = self.get_user_by_id(uid, ['admin'])
		if not user:
			raise Error('user does not exist')
		return bool(user[0])

	def set_admin(self, uid, value=False):
		statement = 'UPDATE {} SET admin=? WHERE id=?'.format(USERS_SCHEMA.name)
		self.db.execute_prepared(statement, value, uid)

##########################################################################
# TESTING
##########################################################################

if __name__ == '__main__':
	print('='*80)
	print('Create database/table')
	print('='*80)
	print(USERS_SCHEMA)
	users = SSUsers(DATABASE)
	print('='*80)
	print('Drop table')
	print('='*80)
	users.drop_table()
	print('='*80)
	print('Create table')
	print('='*80)
	users.create_table()
	print('='*80)
	print('Create users')
	print('='*80)
	users.create_user('test1@test.com', 'George Washington', 'password')
	users.create_user('test2@test.com', 'John Adams', 'password')
	users.create_user('test3@test.com', 'Thomas Jefferson', 'password')
	users.create_user('test4@test.com', 'James Madison', 'password')
	users.create_user('test5@test.com', 'James Monroe', 'password')
	print('='*80)
	print('Check admin')
	print('='*80)
	for user in users.get_all_users():
		if users.is_admin(USERS_SCHEMA.get(user, 'id')):
			print('Failed for user `{}`'.format(user))
		else:
			print('Successful for user `{}`'.format(user))
	print('='*80)
	print('Set admin')
	print('='*80)
	for user in users.get_all_users():
		users.set_admin(USERS_SCHEMA.get(user, 'id'), True)
	for user in users.get_all_users():
		print(user)
	print('='*80)
	print('Check admin')
	print('='*80)
	for user in users.get_all_users():
		if not users.is_admin(USERS_SCHEMA.get(user, 'id')):
			print('Failed for user `{}`'.format(user))
		else:
			print('Successful for user `{}`'.format(user))
	print('='*80)
	print('Remove admin')
	print('='*80)
	for user in users.get_all_users():
		users.set_admin(USERS_SCHEMA.get(user, 'id'), False)
	for user in users.get_all_users():
		print(user)
	print('='*80)
	print('Validate users')
	print('='*80)
	for user in users.get_all_users():
		if users.validate_user(USERS_SCHEMA.get(user, 'email'), 'password') != True:
			print('Verification failed for `{}`'.format(user))
			continue
		if users.validate_user(USERS_SCHEMA.get(user, 'email'), 'bad') != False:
			print('Verification failed for `{}`'.format(user))
			continue
		print('Verification successful for `{}`'.format(user))
	print('='*80)
	print('Change passwords')
	print('='*80)
	for user in users.get_all_users():
		users.set_password(USERS_SCHEMA.get(user, 'id'), 'newpassword')
	for user in users.get_all_users():
		print(user)
	print('='*80)
	print('Insert duplicates')
	print('='*80)
	for user in users.get_all_users():
		try:
			users.create_user(USERS_SCHEMA.get(user, 'email'), 'test', 'test', 'test')
			print('Failed for email `{}`'.format(user[COLUMNS['Email']]))
		except Error as e:
			print('Error: {}'.format(e))
			print('Successful error for email `{}`'.format(USERS_SCHEMA.get(user, 'email')))
	print('='*80)
	print('Delete users')
	print('='*80)
	for user in users.get_all_users():
		users.delete_user(USERS_SCHEMA.get(user, 'id'))
	print(users.get_all_users())
	print('='*80)
	print('Delete unknown user')
	print('='*80)
	users.delete_user(1)

