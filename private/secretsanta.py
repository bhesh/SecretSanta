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
		return '<{} {} ({}, {})>'.format(repr(self._match_type), repr(self.type), repr(self._left), repr(self._right))

	def __str__(self):
		return '{} {} ({}, {})'.format(repr(self._match_type), repr(self.type), self._left, self._right)

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

	def matches(self, right):
		rcol = right[COLUMNS[self._column]]
		if self._match_type == SSMatchType.LITERAL:
			return rcol == self._right
		elif self._match_type == SSMatchType.REGEX:
			return re.fullmatch(self._right, rcol) != None
		return None

	def applies(self, left):
		lcol = left[COLUMNS[self._column]]
		if self._match_type == SSMatchType.LITERAL:
			return lcol == self._left
		elif self._match_type == SSMatchType.REGEX:
			return re.fullmatch(self._left, lcol) != None

	def is_valid(self, left, right):
		"""Defaults to True"""
		if self.type == SSRuleType.NONE or self._match_type == SSMatchType.NONE:
			return True
		elif not self._left or not self._right:
			return True
		elif self.type == SSRuleType.MATCHES:
			return self.applies(left) and self.matches(right)
		elif self.type == SSRuleType.DIFFERS:
			return not self.applies(left) or not self.matches(right)
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
	possibilities = dict()
	for rule in [r for r in rulelist if r.type == SSRuleType.MATCHES]:
		for uid in [u for u in users.keys() if rule.applies(users[u])]:
			possibilities[uid] = [u for u in users.keys() if u != uid and rule.matches(users[u])]
	for uid in [u for u in users.keys() if u not in possibilities]:
		possibilities[uid] = [u for u in users.keys() if u != uid]
	for rule in [r for r in rulelist if r.type == SSRuleType.DIFFERS]:
		for uid in [u for u in users.keys() if rule.applies(users[u])]:
			possibilities[uid] = [u for u in possibilities[uid] if not rule.matches(users[u])]
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

	# TEST FUNCTIONS
	def create_random_users(num, emailDomains=['test.com', 'gmail.com', 'yahoo.com']):
		emailstring = 'abcdefghijklmnopABCDEFGHIJKLMNOP0123456789'
		users = dict()
		for i in range(num):
			uid = 1
			while uid in users:
				uid = random.randint(2, 100 * num)
			emailname = ''.join([random.choice(emailstring) for i in range(8)])
			users[uid] = (uid, '@'.join([emailname, random.choice(emailDomains)]))
		return users

	def verifyTest(assignment, users, rulelist, expected=True):
		try:
			for u in users.keys():
				assert (u in assignment), 'uid {} is missing from assignment'.format(u)
			for u in assignment.keys():
				assert (u in users), 'invalid uid {} found in assignment'.format(u)
			for u in users.keys():
				assert (u != assignment[u]), 'uid {} is assigned to itself, {}'.format(u, assignment)
			for u in users.keys():
				res = [rule.matches(users[assignment[u]]) for rule in [r for r in rulelist if r.type == SSRuleType.MATCHES and r.applies(users[u])]]
				if len(res) == 0: continue
				assert (True in res), 'assignment fails matching rule ({})'.format(assignment[u])
			for rule in [r for r in rulelist if r.type == SSRuleType.DIFFERS]:
				for uid in [u for u in users.keys() if rule.applies(users[u])]:
					assert rule.is_valid(users[uid], users[assignment[uid]]), 'assignment fails rule {}={} ({})'.format(users[uid], users[assignment[uid]], rule)
			return expected == True
		except AssertionError as e:
			if expected: raise e
			return True

	def run_ntimes(n, users, rulelist=[], expected=True):
		for i in range(n):
			try:
				a = assign_partners(users, rulelist)
				assert (a != None), 'assignment failed on run {}\nusers={}\nrules={}'.format(i + 1, users, rulelist)
				assert verifyTest(a, users, rulelist), 'verification failed on run {}\nassignment={}'.format(i + 1, a)
				assert (expected == True), 'test was expected to fail\nassignment={}'.format(a)
			except AssertionError as e:
				if expected: raise e

	count, passed, failed = 0, 0, 0
	def test(name, testcase=None, *args, **kwargs):
		global count, passed, failed
		if not testcase:
			return
		count += 1
		sys.stdout.write('Testcase {}: {} :: '.format(count, name))
		try:
			testcase(*args, **kwargs)
			print('Successful')
			passed += 1
		except:
			print('Failed')
			failed += 1
			import traceback
			traceback.print_exc(file=sys.stderr)

	def rule_test(rule, left, right, expected=True):
		assert (rule.is_valid(left, right) == expected), 'rule failed for {}={} == {}'.format(left, right, expected)

	# TESTS
	for i in range(10):
		test('Run basic assignment 10 times with random users', run_ntimes, 10, create_random_users(10))
	test('Run a failing test 10 times', run_ntimes, 10, {1:(1,'')}, expected=False)
	rules = list()
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.LITERAL, 'uid', 3, 15))
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.LITERAL, 'uid', 15, 3))
	test('Rule test: 3 != 15 success', rule_test, rules[0], (3,''), (5,''))
	test('Rule test: 3 != 15 fail', rule_test, rules[0], (3,''), (15,''), expected=False)
	test('Rule test: 3 != 15 not applicable', rule_test, rules[0], (15,''), (3,''))
	test('Rule test: 15 != 3 success', rule_test, rules[1], (15,''), (1,''))
	test('Rule test: 15 != 3 fail', rule_test, rules[1], (15,''), (3,''), expected=False)
	test('Rule test: 15 != 3 not applicable', rule_test, rules[1], (3,''), (15,''))
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.LITERAL, 'email', 'test1@test.com', 'test2@test.com'))
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.LITERAL, 'email', 'test2@test.com', 'test1@yahoo.com'))
	test('Rule test: test1@test.com != test2@test.com success', rule_test, rules[2], (1,'test1@test.com'), (2,'test5@test.com'))
	test('Rule test: test1@test.com != test2@test.com fail', rule_test, rules[2], (1,'test1@test.com'), (2,'test2@test.com'), expected=False)
	test('Rule test: test1@test.com != test2@test.com not applicable', rule_test, rules[2], (1,'test1@yahoo.com'), (2,'test1@test.com'))
	test('Rule test: test2@test.com != test1@yahoo.com success', rule_test, rules[3], (1,'test2@test.com'), (2,'test5@test.com'))
	test('Rule test: test2@test.com != test1@yahoo.com fail', rule_test, rules[3], (1,'test2@test.com'), (2,'test1@yahoo.com'), expected=False)
	test('Rule test: test2@test.com != test1@yahoo.com not applicable', rule_test, rules[3], (1,'test2@yahoo.com'), (2,'test2@test.com'))
	emails = ['tests{}@test.com'.format(u+1) for u in range(10)] + ['test{}@yahoo.com'.format(u+1) for u in range(10)]
	users = dict((u+1,(u+1,emails[u])) for u in range(len(emails)))
	test('Assignment 50 times with uid LITERAL DIFFERS rules', run_ntimes, 50, users, rules[:2])
	test('Assignment 50 times with email LITERAL DIFFERS rules', run_ntimes, 50, users, rules[2:])
	test('Assignment 50 times with uid+email LITERAL DIFFERS rules', run_ntimes, 50, users, rules)
	test('Impossible assignment with LITTERAL DIFFERS rules', run_ntimes, 1, {3:(3,''),15:(15,'')}, [rules[0]], expected=False)
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'uid', 1, 2))
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'uid', 1, 3))
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'uid', 1, 4))
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'uid', 2, 1))
	test('Rule test: 1 == 2 success', rule_test, rules[4], (1,''), (2,''))
	test('Rule test: 1 == 2 fail', rule_test, rules[4], (1,''), (3,''), expected=False)
	test('Rule test: 1 == 2 not applicable', rule_test, rules[4], (2,''), (3,''), expected=False)
	test('Rule test: 1 == 3 success', rule_test, rules[5], (1,''), (3,''))
	test('Rule test: 1 == 3 fail', rule_test, rules[5], (1,''), (2,''), expected=False)
	test('Rule test: 1 == 3 not applicable', rule_test, rules[5], (2,''), (3,''), expected=False)
	test('Rule test: 1 == 4 success', rule_test, rules[6], (1,''), (4,''))
	test('Rule test: 1 == 4 fail', rule_test, rules[6], (1,''), (2,''), expected=False)
	test('Rule test: 1 == 4 not applicable', rule_test, rules[6], (2,''), (3,''), expected=False)
	test('Rule test: 2 == 1 success', rule_test, rules[7], (2,''), (1,''))
	test('Rule test: 2 == 1 fail', rule_test, rules[7], (2,''), (3,''), expected=False)
	test('Rule test: 2 == 1 not applicable', rule_test, rules[7], (1,''), (2,''), expected=False)
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'email', 'test1@test.com', 'test2@test.com'))
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'email', 'test1@test.com', 'test3@test.com'))
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'email', 'test1@test.com', 'test4@test.com'))
	test('Rule test: test1@test.com == test2@test.com success', rule_test, rules[8], (1,'test1@test.com'), (2,'test2@test.com'))
	test('Rule test: test1@test.com == test2@test.com fail', rule_test, rules[8], (1,'test1@test.com'), (3,'test3@test.com'), expected=False)
	test('Rule test: test1@test.com == test2@test.com not applicable', rule_test, rules[8], (1,'test2@test.com'), (3,'test4@test.com'), expected=False)
	test('Rule test: test1@test.com == test3@test.com success', rule_test, rules[9], (1,'test1@test.com'), (2,'test3@test.com'))
	test('Rule test: test1@test.com == test3@test.com fail', rule_test, rules[9], (1,'test1@test.com'), (3,'test2@test.com'), expected=False)
	test('Rule test: test1@test.com == test3@test.com not applicable', rule_test, rules[9], (1,'test2@test.com'), (3,'test4@test.com'), expected=False)
	test('Rule test: test1@test.com == test4@test.com success', rule_test, rules[10], (1,'test1@test.com'), (2,'test4@test.com'))
	test('Rule test: test1@test.com == test4@test.com fail', rule_test, rules[10], (1,'test1@test.com'), (3,'test2@test.com'), expected=False)
	test('Rule test: test1@test.com == test4@test.com not applicable', rule_test, rules[10], (1,'test2@test.com'), (3,'test4@test.com'), expected=False)
	test('Assignment 50 times with uid LITERAL MATCHES rules', run_ntimes, 50, users, rules[4:8])
	test('Assignment 50 times with email LITERAL MATCHES rules', run_ntimes, 50, users, rules[8:10])
	test('Assignment 50 times with uid+email LITERAL MATCHES rules', run_ntimes, 50, users, rules[8:])
	test('Impossible assignment 10 times with LITERAL MATCHES rules', run_ntimes, 10, {1:(1,''),2:(2,''),3:(3,'')}, [rules[4], rules[7]], expected=False)
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.REGEX, 'email', '^.*@test.com', '^.*@test.com'))
	rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.REGEX, 'email', '^.*@yahoo.com', '^.*@yahoo.com'))
	test('Rule test: {} != {} success'.format(repr(rules[11]._left), repr(rules[11]._right)), rule_test, rules[11], (1,'test1@test.com'), (2,'test1@yahoo.com'))
	test('Rule test: {} != {} fail'.format(repr(rules[11]._left), repr(rules[11]._right)), rule_test, rules[11], (1,'test1@test.com'), (2,'test2@test.com'), expected=False)
	test('Rule test: {} != {} not applicable'.format(repr(rules[11]._left), repr(rules[11]._right)), rule_test, rules[11], (1,'test1@yahoo.com'), (2,'test2@test.com'))
	test('Rule test: {} != {} success'.format(repr(rules[12]._left), repr(rules[12]._right)), rule_test, rules[12], (1,'test1@yahoo.com'), (2,'test1@test.com'))
	test('Rule test: {} != {} fail'.format(repr(rules[12]._left), repr(rules[12]._right)), rule_test, rules[12], (1,'test1@yahoo.com'), (2,'test2@yahoo.com'), expected=False)
	test('Rule test: {} != {} not applicable'.format(repr(rules[12]._left), repr(rules[12]._right)), rule_test, rules[12], (1,'test1@test.com'), (2,'test2@yahoo.com'))
	test('Assignment 50 times with email REGEX DIFFERS rules', run_ntimes, 50, users, rules[11:])
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.REGEX, 'email', '^.*@test.com', '^.*@test.com'))
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.REGEX, 'email', '^.*@yahoo.com', '^.*@yahoo.com'))
	test('Rule test: {} == {} success'.format(repr(rules[13]._left), repr(rules[13]._right)), rule_test, rules[13], (1,'test1@test.com'), (2,'test2@test.com'))
	test('Rule test: {} == {} fail'.format(repr(rules[13]._left), repr(rules[13]._right)), rule_test, rules[13], (1,'test1@test.com'), (2,'test2@yahoo.com'), expected=False)
	test('Rule test: {} == {} not applicable'.format(repr(rules[13]._left), repr(rules[13]._right)), rule_test, rules[13], (1,'test1@yahoo.com'), (2,'test2@test.com'), expected=False)
	test('Rule test: {} == {} success'.format(repr(rules[14]._left), repr(rules[14]._right)), rule_test, rules[14], (1,'test1@yahoo.com'), (2,'test2@yahoo.com'))
	test('Rule test: {} == {} fail'.format(repr(rules[14]._left), repr(rules[14]._right)), rule_test, rules[14], (1,'test1@yahoo.com'), (2,'test2@test.com'), expected=False)
	test('Rule test: {} == {} not applicable'.format(repr(rules[14]._left), repr(rules[14]._right)), rule_test, rules[14], (1,'test1@test.com'), (2,'test2@yahoo.com'), expected=False)
	test('Assignment 50 times with email REGEX MATCHES rules', run_ntimes, 50, users, rules[13:])
	test('Impossible assignment 10 times with email REGEX rules', run_ntimes, 10, users, [rules[11], rules[13]], expected=False)
	for i in range(5):
		test('Assignment 10 times with 5 random rules', run_ntimes, 50, users, [random.choice(rules[:11]) for i in range(5)])
	rules = list()
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'uid', 1, 2))
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'uid', 2, 3))
	rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'uid', 3, 1))
	test('Assignment 10 times with only a single option per user', run_ntimes, 10, {1:(1,''),2:(2,''),3:(3,'')}, rules)

	# SUMMARY
	print('')
	print('Total tests run: {} :: Tests passed: {} :: Tests failed: {}'.format(count, passed, failed))

