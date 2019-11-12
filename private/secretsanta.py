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

import sys, random, re
from enum import Enum

COLUMNS = {
	'uid' : 0,
	'email' : 1
}

class SSRuleType(Enum):
	NONE = 0
	DIFFERS = 1
	MATCHES = 2

class SSMatchType(Enum):
	NONE = 0
	LITERAL = 1
	REGEX = 2

class SSRule(object):

	def __init__(self, ruleType=SSRuleType.NONE, matchType=SSMatchType.NONE, column=None,
				left=None, right=None):
		self.type = ruleType
		self._match_type = matchType
		self._column = column
		self._left = left
		self._right = right

	def __repr__(self):
		return '<{} {} (r"{}", r"{}")>'.format(repr(self._match_type), repr(self.type), self._left, self._right)

	def __str__(self):
		return '{} {} (r"{}", r"{}")'.format(repr(self._match_type), repr(self.type), self._left, self._right)

	def rule_type(self, ruleType):
		self.type = ruleType
		return self

	def match_type(self, matchType):
		self._match_type = matchType
		return self

	def column(self, column):
		"""Name of the column to compare"""
		self._column = column
		return self

	def left(self, left):
		self._left = left
		return self

	def right(self, right):
		self._right = right
		return self

	def _applies(self, left):
		lcol = left[COLUMNS[self._column]]
		if self._match_type == SSMatchType.LITERAL:
			return lcol == self._left
		elif self._match_type == SSMatchType.REGEX:
			return re.fullmatch(self._left, lcol) != None

	def _matches(self, right):
		rcol = right[COLUMNS[self._column]]
		if self._match_type == SSMatchType.LITERAL:
			return rcol == self._right
		elif self._match_type == SSMatchType.REGEX:
			return re.fullmatch(self._right, rcol) != None
		return None

	def is_valid(self, left, right):
		"""Defaults to True"""
		if self.type == SSRuleType.NONE or self._match_type == SSMatchType.NONE:
			return True
		elif not self._left or not self._right:
			return True
		elif not self._applies(left):
			return True
		elif self.type == SSRuleType.MATCHES:
			return self._matches(right)
		elif self.type == SSRuleType.DIFFERS:
			return not self._matches(right)
		return True

def swap(partnerlist, pos1, pos2):
	tmp = partnerlist[pos1]
	partnerlist[pos1] = partnerlist[pos2]
	partnerlist[pos2] = tmp

def verify(users, userlist, partnerlist, rules=[]):
	spots = list()
	for i in range(len(userlist)):
		if userlist[i] == partnerlist[i]:
			spots.append(i)
		else:
			for rule in rules:
				if not rule.is_valid(users[userlist[i]], users[partnerlist[i]]):
					spots.append(i)
	return spots

def create_possibilities(users, rulelist=[]):
	possibilities = {uid : [pid for pid in users.keys() if uid != pid] for uid in users.keys()}
	for rule in rulelist:
		possibilities = {uid : [pid for pid in possibilities[uid] if rule.is_valid(users[uid], users[pid])] for uid in users.keys()}
	return possibilities

def update_possibilities(available, possibilities):
	return {uid : [v for v in possibilities[uid] if v in available] for uid in possibilities.keys()}

def rollback(states):
	assignment, available, possibilities, uid, pid = states.pop()
	# Remove the potential deadend
	possibilities[uid] = [p for p in possibilities[uid] if p != pid]
	return assignment, available, possibilities

def assign_partners(users, rulelist=[]):
	"""userlist = dict({uid : (uid, email)}) :: rulelist = list(SSRule)"""
	if len(users) <= 1:
		return None
	assignment = dict()
	available = list(users.keys())
	states = list()
	possibilities = create_possibilities(users, rulelist)
	while len(available) > 0:
		possibilities = update_possibilities(available, possibilities)
		nextloop = False
		for uid in possibilities.keys():
			if len(possibilities[uid]) == 0:
				if len(states) > 0:
					assignment, available, possibilities = rollback(states)
					nextloop = True
					break
				else:
					print('{} has no possibilities left'.format(uid), file=sys.stderr)
					return None
			elif len(possibilities[uid]) == 1:
				assignment[uid] = possibilities[uid][0]
				available.remove(possibilities[uid][0])
				del possibilities[uid]
				nextloop = True
				break
		if nextloop:
			continue
		uid = list(possibilities.keys())[0]
		pid = random.choice(possibilities[uid])
		states.append((dict(assignment), list(available), dict(possibilities), uid, pid))
		assignment[uid] = pid
		available.remove(pid)
		del possibilities[uid]
	return assignment

##########################################################################
# TESTING
##########################################################################

if __name__ == '__main__':
	users = {
		1 : (1,'test@test.com'),
		3 : (3,'test@test.com'),
		2 : (2,'test@test.com'),
		15 : (15,'test@gmail.com'),
		43 : (43,'test@gmail.com'),
		23 : (23,'test@gmail.com'),
		10 : (10,'test@gmail.com'),
		777 : (777,'test@yahoo.com'),
		90 : (90,'test@yahoo.com'),
		5 : (5,'test@yahoo.com'),
		100 : (100,'test@yahoo.com')
	}
	print('Iterating 5 times...')
	for i in range(5):
		print('='*80)
		print('Assign partners')
		print('='*80)
		assignment = assign_partners(users)
		if assignment:
			print('Successfully assigned partners')
		for user in assignment.keys():
			if user == assignment[user]:
				print('Failed for user {}={}'.format(users[user], users[assignment[user]]))
		print('='*80)
		print('Print Assignments')
		print('='*80)
		for user in assignment.keys():
			print('{}: {}'.format(user, assignment[user]))
	print('='*80)
	print('Make UID match rule (3 != 15, 43 != 777, 1 != 90)')
	print('='*80)
	rules = list()
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.LITERAL, 'uid', 3, 15))
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.LITERAL, 'uid', 15, 3))
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.LITERAL, 'uid', 43, 777))
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.LITERAL, 'uid', 1, 90))
	# 1 : (1,'test@test.com'),
	# 3 : (3,'test@test.com'),
	# 2 : (2,'test@test.com'),
	# 15 : (15,'test@gmail.com'),
	# 43 : (43,'test@gmail.com'),
	# 23 : (23,'test@gmail.com'),
	# 10 : (10,'test@gmail.com'),
	# 777 : (777,'test@yahoo.com'),
	# 90 : (90,'test@yahoo.com'),
	# 5 : (5,'test@yahoo.com'),
	# 100 : (100,'test@yahoo.com')
	good = {uid : users.keys() for uid in [uid for uid in users.keys() if uid not in (3, 15, 43, 1)]}
	good.update({3 : [uid for uid in users.keys() if uid != 15]})
	good.update({15 : [uid for uid in users.keys() if uid != 3]})
	good.update({43 : [uid for uid in users.keys() if uid != 777]})
	good.update({90 : [uid for uid in users.keys() if uid != 90]})
	bad = {3:15,15:3,43:777,1:90}
	for uid in good.keys():
		user = users[uid]
		for p in good[uid]:
			part = users[p]
			if not rules[0].is_valid(user, part) or not rules[1].is_valid(user, part) or not rules[2].is_valid(user, part) or not rules[3].is_valid(user, part):
				print('Failed for user {}={}'.format(user, part))
	for uid in bad.keys():
		user = users[uid]
		part = users[bad[uid]]
		if rules[0].is_valid(user, part) and rules[1].is_valid(user, part) and rules[2].is_valid(user, part) and rules[3].is_valid(user, part):
			print('Failed for {}={}'.format(user, part))
	print('Done')
	print('='*80)
	print('Assign partners 100 times')
	print('='*80)
	for i in range(100):
		assignment = assign_partners(users, rules)
		if assignment:
			for user in assignment.keys():
				if user == assignment[user]:
					print('Failed for user {}={} (run {})'.format(users[user], users[assignment[user]], i + 1))
				else:
					for rule in rules:
						if not rule.is_valid(users[user], users[assignment[user]]):
							print('Failed for user {}={} (run {})'.format(users[user], users[assignment[user]], i + 1))
		else:
			print('Failed assignment (run {})'.format(i + 1))
	print('Done')
	print('='*80)
	print('Make email regex match rule (test.com != test.com, gmail.com != gmail.com, yahoo.com != yahoo.com)')
	print('='*80)
	rules = list()
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.REGEX, 'email', r'^.*@test.com$', r'^.*@test.com$'))
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.REGEX, 'email', r'^.*@gmail.com$', r'^.*@gmail.com$'))
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.REGEX, 'email', r'^.*@yahoo.com$', r'^.*@yahoo.com$'))
	# 1 : (1,'test@test.com'),
	# 3 : (3,'test@test.com'),
	# 2 : (2,'test@test.com'),
	# 15 : (15,'test@gmail.com'),
	# 43 : (43,'test@gmail.com'),
	# 23 : (23,'test@gmail.com'),
	# 10 : (10,'test@gmail.com'),
	# 777 : (777,'test@yahoo.com'),
	# 90 : (90,'test@yahoo.com'),
	# 5 : (5,'test@yahoo.com'),
	# 100 : (100,'test@yahoo.com')
	groups = {'test':[1,2,3],'gmail':[15,43,23,10],'yahoo':[777,90,5,100]}
	bad = {uid : groups['test'] for uid in groups['test']}
	bad.update({uid : groups['gmail'] for uid in groups['gmail']})
	bad.update({uid : groups['yahoo'] for uid in groups['yahoo']})
	good = {uid : groups['gmail'] + groups['yahoo'] for uid in groups['test']}
	good.update({uid : groups['test'] + groups['yahoo'] for uid in groups['gmail']})
	good.update({uid : groups['test'] + groups['gmail'] for uid in groups['yahoo']})
	for uid in good.keys():
		user = users[uid]
		for p in good[uid]:
			part = users[p]
			if not rules[0].is_valid(user, part) or not rules[1].is_valid(user, part) or not rules[2].is_valid(user, part):
				print('Failed for {}={}'.format(user, part))
	for uid in bad.keys():
		user = users[uid]
		for p in bad[uid]:
			part = users[p]
			if rules[0].is_valid(user, part) and rules[1].is_valid(user, part) and rules[2].is_valid(user, part):
				print('Failed for {}={}'.format(user, part))
	print('Done')
	print('='*80)
	print('Assign partners 100 times')
	print('='*80)
	for i in range(100):
		assignment = assign_partners(users, rules)
		if assignment:
			for user in assignment.keys():
				if user == assignment[user]:
					print('Failed for user {}={} (run {})'.format(users[user], users[assignment[user]], i + 1))
				else:
					for rule in rules:
						if not rule.is_valid(users[user], users[assignment[user]]):
							print('Failed for user {}={} (run {})'.format(users[user], users[assignment[user]], i + 1))
		else:
			print('Failed assignment (run {})'.format(i + 1))
	print('Done')
	print('='*80)
	print('Make email regex match rule (test.com == test.com, gmail.com == gmail.com, yahoo.com == yahoo.com)')
	print('='*80)
	rules = list()
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.REGEX, 'email', r'^.*@test.com$', r'^.*@test.com$'))
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.REGEX, 'email', r'^.*@gmail.com$', r'^.*@gmail.com$'))
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.REGEX, 'email', r'^.*@yahoo.com$', r'^.*@yahoo.com$'))
	# 1 : (1,'test@test.com'),
	# 3 : (3,'test@test.com'),
	# 2 : (2,'test@test.com'),
	# 15 : (15,'test@gmail.com'),
	# 43 : (43,'test@gmail.com'),
	# 23 : (23,'test@gmail.com'),
	# 10 : (10,'test@gmail.com'),
	# 777 : (777,'test@yahoo.com'),
	# 90 : (90,'test@yahoo.com'),
	# 5 : (5,'test@yahoo.com'),
	# 100 : (100,'test@yahoo.com')
	groups = {'test':[1,2,3],'gmail':[15,43,23,10],'yahoo':[777,90,5,100]}
	good = {uid : groups['test'] for uid in groups['test']}
	good.update({uid : groups['gmail'] for uid in groups['gmail']})
	good.update({uid : groups['yahoo'] for uid in groups['yahoo']})
	bad  = {uid : groups['gmail'] + groups['yahoo'] for uid in groups['test']}
	bad .update({uid : groups['test'] + groups['yahoo'] for uid in groups['gmail']})
	bad .update({uid : groups['test'] + groups['gmail'] for uid in groups['yahoo']})
	for uid in good.keys():
		user = users[uid]
		for p in good[uid]:
			part = users[p]
			res = False
			for rule in rules:
				res = res or rule.is_valid(user, part)
			if not res:
				print('Failed for {}={}'.format(user, part))
	for uid in bad.keys():
		user = users[uid]
		for p in bad[uid]:
			part = users[p]
			res = True
			for rule in rules:
				res = res and rule.is_valid(user, part)
			if res:
				print('Failed for {}={}'.format(user, part))
	print('Done')
	print('='*80)
	print('Assign partners 100 times')
	print('='*80)
	for i in range(100):
		assignment = assign_partners(users, rules)
		if assignment:
			for user in assignment.keys():
				if user == assignment[user]:
					print('Failed for user {}={} (run {})'.format(users[user], users[assignment[user]], i + 1))
				else:
					for rule in rules:
						if not rule.is_valid(users[user], users[assignment[user]]):
							print('Failed for user {}={} (run {})'.format(users[user], users[assignment[user]], i + 1))
		else:
			print('Failed assignment (run {})'.format(i + 1))
	print('Done')
	users = {
		1 : (1,),
		2 : (2,),
		3 : (3,)
	}
	rules = list()
	rules.append(SSRule(SSRuleType.DIFFERS,SSMatchType.LITERAL,'uid',1,2))
	rules.append(SSRule(SSRuleType.DIFFERS,SSMatchType.LITERAL,'uid',2,3))
	rules.append(SSRule(SSRuleType.DIFFERS,SSMatchType.LITERAL,'uid',3,1))
	assignment = assign_partners(users, rules)
	if assignment:
		print(assignment)
	else:
		print('Failed assignment')
