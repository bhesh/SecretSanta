#!/usr/bin/python3
#
# Makes the register page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import sys, re
import sshttp

try:
	import sessions, sshtml, userstable, groupstable

	args = sshttp.get_parameters()

	# GET method
	if sshttp.is_get():

		# Create group form
		if 'creategroup' in args:

			# Authorized
			if sessions.session_is_valid():
				DATA = """<form id="creategroup" action="/groupctl.py" method="post">
						<div class="register">
							<h1>Create Group</h1>
							<p>Please fill out this form to create a group.</p>
							{}
							<hr/>

							<label for="groupname">Group Name</label>
							<input type="text" placeholder="Enter the group name" name="groupname" required/>
							<hr/>

							<input type="hidden" name="creategroup" value="1"/>
							<button style="margin-bottom: 15px;"><a href="javascript:void(0);" onclick="document.getElementById('creategroup').submit()">Create Group</a></button>
						</div>
					</form> """
				ASIDE = """<h2>What is this?</h2>
				<p>Secret santa group creation.</p>
				<h2 style="margin-top: 15px;">How does it work?</h2>
				<p>Enter whatever name you want. Then invite your friends or family to create an account. Once their account exists, you can add them to the group.</p>"""
				MOBILE = ''

				ERROR = '<p><font color="#a93226">{}</font><br/></p>'

				formatting = ''
				if 'noname' in args:
					formatting = ERROR.format('Must provide a group name')
				elif 'invalid' in args:
					formatting = ERROR.format('Invalid group name')
				replace = {
					'resources' : sshtml.buildResources({'/css/register.css' : 'stylesheet'}),
					'desktopNavLinks' : sshtml.buildDesktopNavLinks(),
					'navLinks' : sshtml.buildNavLinks(),
					'accountLinks' : sshtml.buildAccountLinks(True),
					'body' : sshtml.buildBody(data=DATA.format(formatting), aside=ASIDE, mobile=MOBILE)
				}
				sshttp.send200(sshtml.buildContainerPage(replace))

			# Unauthorized
			else:
				sshttp.send302(sshttp.build_redirect_uri('/getacc.py', '/groupctl.py?creategroup=1'))

		# No function provided
		else:
			sshttp.senderror(400)

	# POST method
	elif sshttp.is_post():
		if sessions.session_is_valid():
			NAME_MATCH = re.compile(r'^[a-zA-Z0-9 .,/<>?-_+"\'\[\]\\|!@#$%^&*()]+$')
			parameters = dict()

			# Create group
			if 'creategroup' in args:
				parameters['creategroup'] = 1
				uid = userstable.USERS_SCHEMA.get(sessions.get_user(), 'id')
				if 'groupname' not in args:
					parameters['noname'] = 1
					sshttp.send302(sshttp.build_uri('/groupctl.py', parameters))
				elif not NAME_MATCH.fullmatch(args.getvalue('groupname')):
					parameters['invalid'] = 1
					sshttp.send302(sshttp.build_uri('/groupctl.py', parameters))
				else:
					gid = groupstable.SSGroups(DATABASE).create_group(uid, args.getvalue('groupname'))
					sshttp.send302(sshttp.build_uri('/groups.py', {'gid' : gid}))

			# Delete group
			elif 'deletegroup' in args:
				user = sessions.get_user()
				uid = userstable.USERS_SCHEMA.get(user, 'id')
				email = userstable.USERS_SCHEMA.get(user, 'email')
				groups = groupstable.SSGroups(DATABASE)
				users = userstable.SSUsers(DATABASE)
				if 'gid' not in args:
					sshttp.senderror(400)
				else:
					level = groups.get_membership_level(args.getvalue('gid'), uid) 
					if level == None or level != groupstable.ADMIN:
						sshttp.senderror(403)
					elif 'password' not in args:
						parameters['gid'] = args.getvalue('gid')
						parameters['nopassword'] = 1
						sshttp.send302(sshttp.build_uri('/groups.py', parameters))
					elif not users.validate_user(email, args.getvalue('password')):
						parameters['gid'] = args.getvalue('gid')
						parameters['invalid'] = 1
						sshttp.send302(sshttp.build_uri('/groups.py', parameters))
					else:
						groups.delete_group(args.getvalue('gid'))
						sshttp.send302('/groups.py')

			# Add member
			elif 'addmember' in args:
				uid = userstable.USERS_SCHEMA.get(sessions.get_user(), 'id')
				groups = groupstable.SSGroups(DATABASE)
				if 'gid' not in args:
					sshttp.senderror(400)
				else:
					level = groups.get_membership_level(args.getvalue('gid'), uid)
					if level == None or level < groupstable.MOD:
						sshttp.senderror(403)
					elif 'email' not in args:
						parameters['gid'] = args.getvalue('gid')
						parameters['noemail'] = 1
						sshttp.send302(sshttp.build_uri('/groups.py', parameters))
					else:
						gid = args.getvalue('gid')
						member = userstable.SSUsers(DATABASE).get_user_by_email(args.getvalue('email').lower(), cols=['id'])
						if not member:
							parameters['gid'] = gid
							parameters['nouser'] = 1
							sshttp.send302(sshttp.build_uri('/groups.py', parameters))
						else:
							groups.add_member(gid, member[0])
							sshttp.send302(sshttp.build_uri('/groups.py', {'gid' : gid}))

			# Leave group
			elif 'leavegroup' in args:
				uid = userstable.USERS_SCHEMA.get(sessions.get_user(), 'id')
				groups = groupstable.SSGroups(DATABASE)
				if 'gid' not in args:
					sshttp.senderror(400)
				else:
					level = groups.get_membership_level(args.getvalue('gid'), uid)
					if level == None or level == groupstable.ADMIN:
						sshttp.senderror(400)
					else:
						groups.remove_member(args.getvalue('gid'), uid)
						sshttp.send302('/groups.py')

			# Kick member
			elif 'removemember' in args:
				uid = userstable.USERS_SCHEMA.get(sessions.get_user(), 'id')
				groups = groupstable.SSGroups(DATABASE)
				if 'gid' not in args or 'uid' not in args:
					sshttp.senderror(400)
				else:
					gid = args.getvalue('gid')
					mid = args.getvalue('uid')
					if uid == mid:
						sshttp.senderror(400)
					else:
						ulevel = groups.get_membership_level(gid, uid)
						mlevel = groups.get_membership_level(gid, mid)
						if ulevel == None or mlevel == None:
							print('Error kicking member (user: {}={}, member: {}={})'.format(uid, ulevel, mid, mlevel),
									file=sys.stderr)
							sshttp.senderror(400)
						elif ulevel <= mlevel:
							sshttp.senderror(403)
						else:
							groups.remove_member(gid, mid)
							sshttp.send302(sshttp.build_uri('/groups.py', {'gid' : gid}))

			# Set moderator
			elif 'setmoderator' in args:
				uid = userstable.USERS_SCHEMA.get(sessions.get_user(), 'id')
				groups = groupstable.SSGroups(DATABASE)
				if 'gid' not in args or 'uid' not in args:
					sshttp.senderror(400)
				else:
					level = groups.get_membership_level(args.getvalue('gid'), uid)
					if level == None or level < groupstable.ADMIN:
						sshttp.senderror(403)
					else:
						gid = args.getvalue('gid')
						mid = args.getvalue('uid')
						value = bool(int(args.getvalue('setmoderator')))
						if value:
							groups.set_membership_level(gid, mid, groupstable.MOD)
						else:
							groups.set_membership_level(args.getvalue('gid'), mid, groupstable.GENERAL)
						sshttp.send302(sshttp.build_uri('/groups.py', {'gid' : gid}))

			# No function provided
			else:
				sshttp.senderror(400)

		# Unauthorized
		else:
			sshttp.senderror(403)

	# Invalid HTTP method
	else:
		sshttp.senderror(405)

except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

