#!/usr/bin/python3
#
# Makes the secret santa runner page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import sshttp
import sys

try:
	import sessions, sshtml, groupstable, userstable

	args = sshttp.get_parameters()

	# Authorized
	if sessions.session_is_valid():
		if 'gid' in args:

			# Make resources
			gid = args.getvalue('gid')
			uid = userstable.USERS_SCHEMA.get(sessions.get_user(), 'id')
			usersdb = userstable.SSUsers(DATABASE)
			groupsdb = groupstable.SSGroups(DATABASE)

			# Build html
			if sshttp.is_get():

				# Verify permissions
				level = groupsdb.get_membership_level(gid, uid)
				if level == None or level < groupstable.MOD:
					sshttp.senderror(403)

				# All good
				else:
					DATA = """<div class="secretsanta">
							<h1>Secret Santa</h1>
							<p>Please assign any rules you may need.</p>
							{error}
							<form id="ruleList" action="/ssctl.py" method="post" class="rulelist">
								<input type="hidden" name="gid" value="{gid}"/>
							</form>
							<form id="ruleMaker">
								<select id="userList1">
									{userlist}
								</select>
								<select id="matchType">
									<option value="0">NEVER GETS</option>
									<option value="1">ALWAYS GETS</option>
								</select>
								<select id="userList2">
									{userlist}
								</select>
								<button><a href="javascript:void(0)" onclick="addRule()">Add Rule</a></button>
							</form>
							<hr/>
							<button><a href="javascript:void(0)" onclick="document.getElementById('ruleList').submit()">Run</a></button>
						</div>"""
					ASIDE = """<h2>What is it?</h2>
						<p>Secret santa target assignment.</p>
						<h2 style="margin-top: 15px;">How does it work?</h2>
						<p>Click run to randomly assign targets. Apply any rules or restrictions you see fit. The assignment will fail if not everyone can be assigned a target.</p>"""
					MOBILE = ''
					LIST_ITEM = '<option value="{uid}">{name}</option>'

					ERROR = '<p><font color="#a93226">{}</font><br/></p>'
					formatting = ''
					if 'failed' in args:
						formatting = ERROR.format('No combination of partners existed with the privided rules.')

					# Populate list
					userlist = list()
					for row in groupsdb.get_members_for(gid, ['uid']):
						user = usersdb.get_user_by_id(row[0], cols=['id', 'name'])
						if user:
							userlist.append(LIST_ITEM.format(uid=user[0], name=user[1]))

					replace = {
						'resources' : sshtml.buildResources({
							'/css/secretsanta.css' : 'stylesheet',
							'/js/secretsanta.js' : 'javascript'
						}),
						'desktopNavLinks' : sshtml.buildDesktopNavLinks(),
						'navLinks' : sshtml.buildNavLinks(),
						'accountLinks' : sshtml.buildAccountLinks(True),
						'body' : sshtml.buildBody(data=DATA.format(gid=gid, userlist=userlist, error=formatting), aside=ASIDE, mobile=MOBILE)
					}
					sshttp.send200(sshtml.buildContainerPage(replace))

			# Run secretsanta
			elif sshttp.is_post():

				# Verify permissions
				level = groupsdb.get_membership_level(gid, uid)
				if level == None or level < groupstable.MOD:
					sshttp.senderror(403)

				# All good
				else:
					users = dict()
					for row in groupsdb.get_members_for(gid, ['uid']):
						user = usersdb.get_user_by_id(row[0], cols=['id', 'email', 'name'])
						if user:
							users[user[0]] = user
					import json, secretsanta
					from secretsanta import SSRule, SSRuleType, SSMatchType
					rules = list()
					if 'rules[]' in args:
						for rulejson in args.getlist('rules[]'):
							rule = json.loads(rulejson)
							if 'left' in rule and 'match' in rule and 'right' in rule:
								if rule['match'] == 0:
									rules.append(SSRule(SSRuleType.DIFFERS, SSMatchType.LITERAL, 'uid', rule['left'], rule['right']))
								if rule['match'] == 1:
									rules.append(SSRule(SSRuleType.MATCHES, SSMatchType.LITERAL, 'uid', rule['left'], rule['right']))
					assignment = secretsanta.assign_partners(users, rules)
					if assignment:
						groupsdb.set_partners(gid, assignment)
						sshttp.send302(sshttp.build_uri('/groups.py', {'gid' : gid}))
					else:
						parameters = dict()
						parameters['gid'] = gid
						parameters['failed'] = 1
						sshttp.send302(sshttp.build_uri('/ssctl.py', parameters))

			# Invalid http method
			else:
				sshttp.senderror(405);

		# Invalid request (no gid)
		else:
			sshttp.senderror(400)

	# Unauthorized
	else:
		parameters = dict()
		if 'gid' in args:
			parameters['redirect'] = sshttp.build_uri('/groups.py', {'gid' : args.getvalue('gid')})
		else:
			parameters['redirect'] = '/groups.py'
		sshttp.send302(sshttp.build_uri('/getacc.py', parameters))
except:
	sshttp.senderror(500)
	import traceback
	traceback.print_exc(file=sys.stderr)

