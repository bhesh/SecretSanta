#!/usr/bin/python3
#
# Secret Santa Database
#
# Interface to the secret santa database
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import sqlite3, collections
from sqlite3 import Error

class SSColumnSchema(object):

	def __init__(self, col_name, col_type, col_flags=None):
		self.name = col_name
		self.type = col_type
		self.flags = None
		if col_flags:
			self.flags = list()
			for f in col_flags:
				self.flags.append(f.upper())

	def has_flags(self):
		return self.flags != None and len(self.flags) > 0

	def __str__(self):
		flags = ''
		if self.has_flags():
			flags = ' ' + ' '.join(self.flags)
		return '{} {}{}'.format(self.name, self.type, flags)

class SSTableSchema(object):

	def __init__(self, table_name, table_flags=list()):
		self.name = table_name
		self._cols = collections.OrderedDict()
		self.colmap = dict()
		self.flags = table_flags

	def __contains__(self, col_name):
		return col_name in self._cols

	def has_flags(self):
		return self.flags and len(self.flags) > 0

	def add_flag(self, table_flags):
		self.flags.append(table_flags)

	def columns(self):
		return self._cols.keys()

	def add_column(self, column):
		if column.name not in self:
			self.colmap[column.name] = len(self._cols)
		self._cols[column.name] = column

	def get(self, sqlobj, col_name):
		return sqlobj[self.colmap[col_name]]

	def __iter__(self):
		for k in self._cols.keys():
			yield self._cols[k]

	def validate(self, *cols):
		for c in cols:
			if c not in self:
				return False
		return True

	def __str__(self):
		rowstr = [str(c) for c in self]
		if self.has_flags():
			rowstr += [f for f in self.flags]
		return 'CREATE TABLE IF NOT EXISTS {} ({});'.format(self.name, ', '.join(rowstr))

class SSDatabase(object):

	def __init__(self, dbfile):
		self.dbfile = dbfile

	def execute(self, statement):
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(statement)
			return c.fetchall()

	def execute_prepared(self, statement, *values):
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(statement, (*values,))
			return c.fetchall()

	def insert_and_retrieve(self, table, data):
		keys = data.keys()
		vals = [data[k] for k in keys]
		statement = 'INSERT INTO {} ({}) VALUES ({})'.format(table, ','.join(keys), ','.join(['?' for v in vals]))
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			c.execute(statement, (*vals,))
			c.execute('SELECT last_insert_rowid()')
			return int(c.fetchall()[0][0])

	def batch_update(self, table, search_data, update_data):
		if len(search_data) != len(update_data):
			raise Error('search and update data lengths must match')
		statement_fmt = 'UPDATE {} SET {} WHERE {}'
		with sqlite3.connect(self.dbfile) as conn:
			c = conn.cursor()
			for i in range(len(search_data)):
				vals = [update_data[i][k] for k in update_data[i].keys()]
				vals += [search_data[i][k] for k in search_data[i].keys()]
				statement = statement_fmt.format(table,
						','.join(['{}=?'.format(k) for k in update_data[i].keys()]),
						' AND '.join(['{}=?'.format(k) for k in search_data[i].keys()]))
				c.execute(statement, (*vals,))

	def create_table(self, table_schema):
		if not isinstance(table_schema, SSTableSchema):
			raise Error('invalid table schema')
		return self.execute(str(table_schema))

	def drop_table(self, table_schema):
		if not isinstance(table_schema, SSTableSchema):
			raise Error('invalid table schema')
		return self.execute('DROP TABLE {}'.format(table_schema.name))

##########################################################################
# TESTING
##########################################################################

if __name__ == '__main__':
	print('='*80)
	print('Build schema')
	print('='*80)
	users = SSTableSchema('users')
	users.add_column(SSColumnSchema('id', 'integer', ('PRIMARY KEY', 'AUTOINCREMENT')))
	users.add_column(SSColumnSchema('email', 'nvarchar[320]', ('NOT NULL',)))
	users.add_column(SSColumnSchema('name', 'nvarchar[320]', ('NOT NULL',)))
	users.add_column(SSColumnSchema('password', 'nvarchar[320]', ('NOT NULL',)))
	users.add_column(SSColumnSchema('salt', 'nvarchar[320]', ('NOT NULL',)))
	users.add_column(SSColumnSchema('admin', 'boolean', ('NOT NULL',)))
	for c in users:
		print(c)
	print('='*80)
	print('Create database')
	print('='*80)
	db = SSDatabase('test.db')
	print('='*80)
	print('Create table')
	print('='*80)
	db.create_table(users)

	print('='*80)
	print('Basic tests')
	print('='*80)
	statement = 'INSERT INTO {} ({}) VALUES (?,?,?,?,?)'.format(users.name,
			','.join(list(users.columns())[1:]))
	print(db.execute_prepared(statement, 'test@test.com','George Washington','password','salt',True))
	print(db.execute_prepared(statement, 'test1@test.com','George Washington','password','salt',True))
	print(db.execute_prepared(statement, 'test@test.com','George Washington','password','salt',True))
	print(db.execute_prepared(statement, 'test@test.com','George Washington','password','salt',True))
	print(db.execute_prepared(statement, 'test@test.com','George Washington','password','salt',True))
	print(db.execute('SELECT * FROM {}'.format(users.name)))
	print(db.execute_prepared('SELECT name,password,salt FROM {} WHERE id=?'.format(users.name), 1))
	print('='*80)
	print('SQL Injections')
	print('='*80)
	print(db.execute_prepared('SELECT * FROM {} WHERE id=?'.format(users.name), '1; DROP TABLE users;'))
	print(db.execute('SELECT * FROM {}'.format(users.name)))
	print(db.execute_prepared('DELETE FROM {} WHERE email=?'.format(users.name), 'test@test.com\' OR email=\'test1@test.com\' --'))
	print(db.execute('SELECT * FROM {}'.format(users.name)))
	print('='*80)
	print('Drop table')
	print('='*80)
	print(db.drop_table(users))

