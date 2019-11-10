#!/usr/bin/python3

from env import *
import sys, ssdb

def main(args):
	if len(args) < 1:
		print_usage_and_exit()

	command = args[0]
	options = args[1:]

	db = ssdb.SSDatabase('../db/secretsanta.db')
	if command == 'listusers':
		for user in db.get_all_users():
			print(user)
	elif command == 'createuser':
		if len(options) != 4:
			print_usage_and_exit()
		db.create_user(options[0], options[1], options[2], options[3])
	elif command == 'setadmin':
		if len(options) < 1:
			print_usage_and_exit()
		for uid in options:
			db.set_admin(uid)
	elif command == 'checkadmin':
		if len(options) < 1:
			print_usage_and_exit()
		for uid in options:
			print(uid, db.is_admin(uid))
	elif command == 'removeadmin':
		if len(options) < 1:
			print_usage_and_exit()
		for uid in options:
			db.remove_admin(uid)
	elif command == 'deleteuser':
		if len(options) < 1:
			print_usage_and_exit()
		for uid in options:
			db.delete_user(uid)
	elif command == 'listsessions':
		for session in db.get_all_sessions():
			print(session)
	elif command == 'deletesession':
		if len(options) < 1:
			print_usage_and_exit()
		for sid in options:
			db.delete_session(options[0])
	elif command == 'cleansessions':
		db.clean_sessions()
	elif command == 'drop':
		if len(options) != 1 and options[0] != 'sessions':
			print_usage_and_exit()
		db.drop_table(options[0])
	elif command == 'set':
		if len(options) != 4:
			print_usage_and_exit()
		db.set(options[0], options[1], options[2], options[3])
def print_usage_and_exit():
	print('Usage: {} <command> [options]'.format(sys.argv[0]))
	print('')
	print('Commands')
	print('listusers')
	print('createuser email firstname lastname password')
	print('setadmin [uid...]')
	print('checkadmin [uid...]')
	print('removeadmin [uid...]')
	print('deleteuser [uid...]')
	print('listsessions')
	print('deletesession [sid...]')
	print('set table u/sid key value')
	print('drop table')
	sys.exit(0)

if __name__ == '__main__':
	main(sys.argv[1:])

