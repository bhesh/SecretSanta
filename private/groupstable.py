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
import ssdb
from ssdb import Error

# Groups
GROUPS_SCHEMA = ssdb.SSTableSchema('groups')
GROUPS_SCHEMA.add_column(ssdb.SSColumnSchema('id', 'integer', ('PRIMARY KEY', 'AUTOINCREMENT',)))
GROUPS_SCHEMA.add_column(ssdb.SSColumnSchema('name', 'nvarchar[320]', ('NOT NULL',)))

# Membership
GROUPMEMBERSHIP_SCHEMA = ssdb.SSTableSchema('groupMembership')
GROUPMEMBERSHIP_SCHEMA.add_column(ssdb.SSColumnSchema('uid', 'integer', ('NOT NULL',)))
GROUPMEMBERSHIP_SCHEMA.add_column(ssdb.SSColumnSchema('gid', 'integer', ('NOT NULL',)))
GROUPMEMBERSHIP_SCHEMA.add_column(ssdb.SSColumnSchema('level', 'integer', ('NOT NULL',)))
GROUPMEMBERSHIP_SCHEMA.add_column(ssdb.SSColumnSchema('partner', 'integer'))

# Levels
GENERAL = 0
MOD = 1
ADMIN = 2

class SSGroups(object):

	def __init__(self, dbfile):
		self.db = ssdb.SSDatabase(dbfile)
		self.create_tables()

	def create_tables(self):
		self.db.create_table(GROUPS_SCHEMA)
		self.db.create_table(GROUPMEMBERSHIP_SCHEMA)

	def drop_tables(self):
		self.db.drop_table(GROUPS_SCHEMA)
		self.db.drop_table(GROUPMEMBERSHIP_SCHEMA)

	def get_all_groups(self):
		statement = 'SELECT * FROM {}'.format(GROUPS_SCHEMA.name)
		return self.db.execute(statement)

	def get_group_by_id(self, gid, cols=None):
		columns = '*'
		if cols:
			columns = ','.join(cols)
		statement = 'SELECT {} FROM {} WHERE id=?'.format(columns, GROUPS_SCHEMA.name)
		res = self.db.execute_prepared(statement, gid)
		if len(res) == 0:
			return None
		if len(res) > 1:
			raise Error('returned more than one group')
		return res[0]

	def get_all_group_memberships(self):
		statement = 'SELECT * FROM {}'.format(GROUPMEMBERSHIP_SCHEMA.name)
		return self.db.execute(statement)

	def get_groups_for(self, uid, cols=None):
		columns = '*'
		if cols:
			columns = ','.join(cols)
		statement = 'SELECT {} FROM {} WHERE uid=?'.format(columns, GROUPMEMBERSHIP_SCHEMA.name)
		return self.db.execute_prepared(statement, uid)

	def get_members_for(self, gid, cols=None):
		columns = '*'
		if cols:
			columns = ','.join(cols)
		statement = 'SELECT {} FROM {} WHERE gid=?'.format(columns, GROUPMEMBERSHIP_SCHEMA.name)
		return self.db.execute_prepared(statement, gid)

	def create_group(self, uid, name):
		statement = 'INSERT INTO {} (uid,gid,level) VALUES (?,?,?)'.format(GROUPMEMBERSHIP_SCHEMA.name)
		gid = self.db.insert_and_retrieve(GROUPS_SCHEMA.name, {'name' : name})
		self.db.execute_prepared(statement, uid, gid, ADMIN)
		return gid

	def delete_group(self, gid):
		statement1 = 'DELETE FROM {} WHERE id=?'.format(GROUPS_SCHEMA.name)
		statement2 = 'DELETE FROM {} WHERE gid=?'.format(GROUPMEMBERSHIP_SCHEMA.name)
		self.db.execute_prepared(statement1, gid)
		self.db.execute_prepared(statement2, gid)

	def get_membership_level(self, gid, uid):
		statement = 'SELECT level FROM {} WHERE uid=? AND gid=?'.format(GROUPMEMBERSHIP_SCHEMA.name)
		res = self.db.execute_prepared(statement, uid, gid)
		if len(res) == 0:
			return None
		if len(res) > 1:
			raise Error('returned more than one membership')
		return int(res[0][0])

	def set_partner(self, gid, uid, partner):
		statement = 'UPDATE {} SET partner=? WHERE uid=? AND gid=?'.format(GROUPMEMBERSHIP_SCHEMA.name)
		self.db.execute_prepared(statement, partner, uid, gid)

	def set_partners(self, gid, assignment):
		"""assignment = dict({ user : partner })"""
		search_data = list()
		update_data = list()
		for u in assignment.keys():
			search_data.append({'uid' : u, 'gid' : gid})
			update_data.append({'partner' : assignment[u]})
		self.db.batch_update(GROUPMEMBERSHIP_SCHEMA.name, search_data, update_data)

	def get_partner(self, gid, uid):
		statement = 'SELECT partner FROM {} WHERE uid=? AND gid=?'.format(GROUPMEMBERSHIP_SCHEMA.name)
		res = self.db.execute_prepared(statement, uid, gid)
		if len(res) == 0:
			return None
		if len(res) > 1:
			raise Error('returned more than one membership')
		if res[0][0]:
			return int(res[0][0])
		return None

	def add_member(self, gid, uid, level=GENERAL):
		if self.get_membership_level(gid, uid) == None:
			statement = 'INSERT INTO {} (uid,gid,level) VALUES (?,?,?)'.format(GROUPMEMBERSHIP_SCHEMA.name)
			self.db.execute_prepared(statement, uid, gid, level)

	def remove_member(self, gid, uid):
		statement = 'DELETE FROM {} WHERE uid=? AND gid=?'.format(GROUPMEMBERSHIP_SCHEMA.name)
		self.db.execute_prepared(statement, uid, gid)

	def set_membership_level(self, gid, uid, level):
		statement = 'UPDATE {} SET level=? WHERE uid=? AND gid=?'.format(GROUPMEMBERSHIP_SCHEMA.name)
		self.db.execute_prepared(statement, level, uid, gid)

if __name__ == '__main__':
	print('='*80)
	print('Create database/tables')
	print('='*80)
	print(GROUPS_SCHEMA)
	print(GROUPMEMBERSHIP_SCHEMA)
	groups = SSGroups(DATABASE)
	print('='*80)
	print('Drop tables')
	print('='*80)
	groups.drop_tables()
	print('='*80)
	print('Create tables')
	print('='*80)
	groups.create_tables()
	print('='*80)
	print('Create groups')
	print('='*80)
	gids = list()
	gids.append(groups.create_group(1, 'test1'))
	gids.append(groups.create_group(2, 'test2'))
	gids.append(groups.create_group(3, 'test3'))
	gids.append(groups.create_group(4, 'test4'))
	gids.append(groups.create_group(5, 'test5'))
	print('gids: {}'.format(gids))
	for group in groups.get_all_groups():
		print(group)
	for gm in groups.get_all_group_memberships():
		print(gm)
	print('='*80)
	print('Add members')
	print('='*80)
	groups.add_member(1, 2)
	groups.add_member(2, 3)
	groups.add_member(3, 4)
	groups.add_member(4, 5)
	groups.add_member(5, 1)
	groups.add_member(1, 3)
	groups.add_member(2, 4)
	groups.add_member(3, 5)
	groups.add_member(4, 1)
	groups.add_member(5, 2)
	for gm in groups.get_all_group_memberships():
		print(gm)
	print('='*80)
	print('List members')
	print('='*80)
	for group in groups.get_all_groups():
		print(GROUPS_SCHEMA.get(group, 'name'))
		for user in groups.get_members_for(GROUPS_SCHEMA.get(group, 'id')):
			print(user)
	print('='*80)
	print('List groups')
	print('='*80)
	for user in [1, 2, 3, 4, 5]:
		print('User:', user)
		for group in groups.get_groups_for(user):
			print(group)
	print('='*80)
	print('Add all members to 1')
	print('='*80)
	groups.add_member(1, 4)
	groups.add_member(1, 5)
	for user in groups.get_members_for(1):
		print(user)
	print('='*80)
	print('Set partners for group 1')
	print('='*80)
	assignment = {
		1 : 2,
		2 : 3,
		3 : 4,
		4 : 5,
		5 : 1
	}
	groups.set_partners(1, assignment)
	for user in groups.get_members_for(1):
		print(user)
	print('='*80)
	print('Remove member')
	print('='*80)
	groups.remove_member(1, 2)
	groups.remove_member(2, 3)
	groups.remove_member(3, 4)
	groups.remove_member(4, 5)
	groups.remove_member(5, 1)
	for user in [1, 2, 3, 4, 5]:
		print('User:', user)
		for group in groups.get_groups_for(user):
			print(group)
	print('='*80)
	print('Elevate member')
	print('='*80)
	groups.set_membership_level(1, 3, MOD)
	print('User: 3')
	for group in groups.get_groups_for(3):
		print(group)
	print('='*80)
	print('Add duplicate member')
	print('='*80)
	groups.add_member(1, 3)
	for group in groups.get_groups_for(3):
		print(group)
	print('='*80)
	print('Add to non-existent group')
	print('='*80)
	try:
		groups.add_member(6, 1)
		print('Failed')
	except:
		print('Successful')
	print('='*80)
	print('Delete group 1')
	print('='*80)
	groups.delete_group(1)
	for group in groups.get_all_groups():
		print(group)
	for gm in groups.get_all_group_memberships():
		print(gm)
	print('='*80)
	print('Delete groups 2 and 3')
	print('='*80)
	groups.delete_group(2)
	groups.delete_group(3)
	for group in groups.get_all_groups():
		print(group)
	for gm in groups.get_all_group_memberships():
		print(gm)
	print('='*80)
	print('Delete groups 4 and 5')
	print('='*80)
	groups.delete_group(4)
	groups.delete_group(5)
	print(groups.get_all_groups())
	print(groups.get_all_group_memberships())
	print('='*80)
	print('Create another group')
	print('='*80)
	print('gid: {}'.format(groups.create_group(1, 'Works!')))

