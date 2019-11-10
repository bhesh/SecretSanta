#!/usr/bin/python3
#
# Secret Santa Assigner
#
# Takes all users in the database and randomly
# assigns them a secret santa buddy.
#
# Every user must have someone assigned other
# than themselves.
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import random
import ssdb

def swap(idlist, pos1, pos2):
	tmp = idlist[pos1]
	idlist[pos1] = idlist[pos2]
	idlist[pos2] = tmp

def verify(users, idlist):
	spots = []
	for i in range(len(users)):
		if users[i][ssdb.COLUMNS['id']] == idlist[i]:
			spots.append(i)
	return spots

def assign_partners(dbfile):
	db = ssdb.SSDatabase(dbfile)
	users = db.get_all_users()
	if len(users) <= 1:
		return False
	ids = []
	for user in users:
		ids.append(user[ssdb.COLUMNS['id']])
	random.shuffle(ids)
	while True:
		spots = verify(users, ids)
		if len(spots) == 0:
			break
		elif len(spots) == 1:
			randpos = random.randint(0, len(users) - 1)
			while randpos == spots[0]:
				randpos = random.randint(0, len(users) - 1)
			swap(ids, spots[0], randpos)
		elif len(spots) >= 2:
			swap(ids, spots[0], spots[1])
	for i in range(len(users)):
		db.set_partner(users[i][ssdb.COLUMNS['id']], ids[i])
	return True

##########################################################################
# TESTING
##########################################################################

if __name__ == '__main__':
	dbfile = 'test2.db'
	db = ssdb.SSDatabase(dbfile)
	db.drop_table()
	db.create_table()
	db.create_user('test1@test.com', 'George', 'Washington', 'password')
	db.create_user('test2@test.com', 'John', 'Adams', 'password')
	db.create_user('test3@test.com', 'Thomas', 'Jefferson', 'password')
	db.create_user('test4@test.com', 'James', 'Madison', 'password')
	db.create_user('test5@test.com', 'James', 'Monroe', 'password')
	print('Iterating 5 times...')
	for i in range(5):
		print('='*80)
		print('Assign partners')
		print('='*80)
		if assign_partners(dbfile):
			print('Successfully assigned partners')
		print('='*80)
		print('Print Assignments')
		print('='*80)
		for user in db.get_all_users():
			print(user)

