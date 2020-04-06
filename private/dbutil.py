#!/usr/bin/python3

from env import *
import sys, ssdb, hashlib, random

db = ssdb.SSDatabase(DATABASE)

def main(args):
	if len(args) < 1:
		print_usage_and_exit()

	command = args[0]
	options = args[1:]

	if command == 'colnames':
		if len(options) < 1:
			print_usage_and_exit()
		for table in options:
			print(getColumnNames(table))
	elif command == 'select':
		if len(options) < 1:
			print_usage_and_exit()
		criteria = dict((o.split('=', 1)) for o in options[1:])
		print(getColumnNames(options[0]))
		for r in select(options[0], criteria=criteria):
			print(r)
	elif command == 'getprop':
		if len(options) < 2:
			print_usage_and_exit()
		cols = [options[1]]
		criteria = dict((o.split('=', 1)) for o in options[2:])
		for r in select(options[0], criteria=criteria, cols=cols):
			print(r[0])
	elif command == 'insert':
		if len(options) < 2:
			print_usage_and_exit()
		row = dict((o.split('=', 1)) for o in options[1:])
		insert(options[0], row=row)
	elif command == 'update':
		if len(options) < 3:
			print_usage_and_exit()
		criteria = dict((options[1].split('=', 1),))
		newvals = dict((o.split('=', 1)) for o in options[2:])
		update(options[0], criteria=criteria, newvals=newvals)
	elif command == 'delete':
		if len(options) < 2:
			print_usage_and_exit()
		criteria = dict((o.split('=', 1)) for o in options[1:])
		delete(options[0], criteria=criteria)
	elif command == 'salt':
		length = 32
		if len(options) == 1:
			length = int(options[0])
		print(create_salt(length))
	elif command == 'hash':
		if len(options) != 1:
			print_usage_and_exit()
		print(hash(options[0]))
	elif command == 'resetpassword':
		if len(options) != 5:
			print_usage_and_exit()
		criteria = dict((options[1].split('=', 1),))
		newvals = dict()
		newvals[options[3]] = create_salt(32)
		newvals[options[2]] = hash(options[4] + newvals[options[3]])
		update(options[0], criteria=criteria, newvals=newvals)
	elif command == 'verifyassignments':
		if len(options) != 4:
			print_usage_and_exit()
		key, val = options[1].split('=', 1)
		assignments = dict(select(options[0], {key: val}, cols=options[2:]))
		for u in assignments.keys():
			assert (u in assignments.values()), 'failed'
			assert (u != assignments[u]), 'failed'
		for a in assignments.values():
			assert (a in assignments.keys()), 'failed'
		print('successful')
	elif command == 'export':
		if len(options) < 1:
			print_usage_and_exit()
		for table in options:
			print(getTableConstruct(table) + ';')
			cols = getColumnNames(table)
			for obj in select(table):
				row = dict(zip(cols, obj))
				print('INSERT INTO {} ({}) VALUES ({});'.format(table,
					','.join([str(r) for r in row.keys()]),
					','.join([repr(row[r]) for r in row.keys()])))
	elif command == 'import':
		for line in sys.stdin:
			db.execute(line)
	else:
		print_usage_and_exit()

def getTableInfo(table):
	return db.execute('PRAGMA table_info({})'.format(table))

def getColumnNames(table):
	return tuple([r[1] for r in getTableInfo(table)])

def getTableConstruct(table):
	return db.execute_prepared('SELECT sql FROM sqlite_master WHERE type=\'table\' AND name=?', table)[0][0]

def select(table, criteria={}, cols=[]):
	columns = '*'
	if len(cols) > 0:
		columns = ','.join(cols)
	statement = 'SELECT {} FROM {}'.format(columns, table)
	if len(criteria) > 0:
		keys = list(criteria.keys())
		vals = [criteria[k] for k in keys]
		statement += ' WHERE {}'.format(' AND '.join(['{}=?'.format(k) for k in keys]))
		return db.execute_prepared(statement, *vals)
	else:
		return db.execute(statement)

def insert(table, row={}):
	if len(row) == 0:
		return
	keys = list(row.keys())
	vals = [row[k] for k in keys]
	statement = 'INSERT INTO {} ({}) VALUES ({})'.format(table,
		','.join(keys), ','.join(['?' for k in keys]))
	db.execute_prepared(statement, *vals)

def update(table, criteria={}, newvals={}):
	if len(newvals) == 0:
		return
	critkeys, valkeys = list(criteria.keys()), list(newvals.keys())
	critvals, valvals = [criteria[k] for k in critkeys], [newvals[k] for k in valkeys]
	statement = 'UPDATE {} SET {}'.format(table, ','.join(['{}=?'.format(k) for k in valkeys]))
	if len(criteria) > 0:
		statement += ' WHERE {}'.format(' AND '.join(['{}=?'.format(k) for k in critkeys]))
		db.execute_prepared(statement, *valvals, *critvals)
	else:
		db.execute_prepared(statement, *valvals)

def delete(table, criteria={}):
	statement = 'DELETE FROM {}'.format(table)
	if len(criteria) > 0:
		critkeys = list(criteria.keys())
		critvals = [criteria[k] for k in critkeys]
		statement += ' WHERE {}'.format(' AND '.join(['{}=?'.format(k) for k in critkeys]))
		db.execute_prepared(statement, *critvals)
	else:
		db.execute(statement)

def create_salt(length):
	ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	salt = list()
	for i in range(length):
		salt.append(random.choice(ALPHABET))
	return ''.join(salt)

def hash(value):
	return str(hashlib.sha256(bytes(value, 'UTF-8')).hexdigest())

def print_usage_and_exit():
	print('Usage: {} <command> [arguments]'.format(sys.argv[0]))
	print('')
	print('COMMANDS')
	print('colnames <table...>')
	print('select <table> [key=value...]')
	print('getprop <table> <column> [key=value...]')
	print('insert <table> <key=value...>')
	print('update <table> <id=id> <key=newvalue...>')
	print('delete <table> [key=value...]')
	print('salt [length]')
	print('hash <value>')
	print('resetpassword <table> <id=id> <passcol> <saltcol> <password>')
	print('verifyassignments <table> <gid=gid> <uidcol> <targetcol>')
	print('export <table...>')
	print('import - from stdin')
	sys.exit(0)

if __name__ == '__main__':
	main(sys.argv[1:])

