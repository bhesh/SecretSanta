#!/usr/bin/python3

from env import *
import sys, ssdb, userstable

def main(args):
	if len(args) < 1:
		print_usage_and_exit()

	command = args[0]
	options = args[1:]

	db = ssdb.SSDatabase(DATABASE)
	if command == 'select':
		if len(options) < 1:
			print_usage_and_exit()
		table = options[0]
		matches = options[1:]
		statement = 'SELECT * FROM {}'.format(table)
		if len(matches) > 0:
			statement += 'WHERE {}'.format(' AND '.join(matches))
		for u in db.execute(statement):
			print(u)
	elif command == 'transfer':
		if len(options) < 2:
			print_usage_and_exit()
		db2 = ssdb.SSDatabase(options[0])
		print(userstable.SSUsers(options[1]).get_all_users())
		db3 = ssdb.SSDatabase(options[1])
		statement1 = 'SELECT id,Email,Password,PasswordSalt,FirstName,LastName,Admin FROM users'
		for u in db2.execute(statement1):
			statement2 = 'INSERT INTO users (email,password,salt,name,admin) VALUES (?,?,?,?,?)'
			db3.execute_prepared(statement2, u[1], u[2], u[3], ' '.join([u[4],u[5]]), u[6])
		for u in db3.execute('SELECT * FROM users'):
			print(u)
	else:
		print_usage_and_exit()

def print_usage_and_exit():
	print('Usage: {} <command> [options]'.format(sys.argv[0]))
	print('')
	print('Commands')
	print('select <table> [key=value...]')
	print('transfer <dbfile>')
	sys.exit(0)

if __name__ == '__main__':
	main(sys.argv[1:])

