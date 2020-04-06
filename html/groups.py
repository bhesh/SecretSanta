#!/usr/bin/python3
#
# Makes the page page
#
# @author Brian Hession
# @email hessionb@gmail.com
#

from env import *
import sshttp

try:
	import sessions, sshtml, userstable, groupstable

	args = sshttp.get_parameters()

	if sessions.session_is_valid():
		user = sessions.get_user()
		uid = userstable.USERS_SCHEMA.get(user, 'id')

		# Get groups...
		groups = groupstable.SSGroups(DATABASE)
		grouplist = groups.get_groups_for(uid)
		groupinfo = dict()
		for group in grouplist:
			gid = groupstable.GROUPMEMBERSHIP_SCHEMA.get(group, 'gid')
			groupname = groups.get_group_by_id(gid, ['name'])[0]
			groupinfo[gid] = groupname

		# Look for requested group
		gid = None
		if 'gid' in args:
			gid = int(args.getvalue('gid'))
		elif len(groupinfo) > 0:
			gid = list(groupinfo.keys())[0]

		# If not in the group
		if gid and gid not in groupinfo.keys():
			sshttp.senderror(403)

		# Make response
		else:
			# Make links
			links = {g : (groupinfo[g], sshttp.build_uri('/groups.py', {'gid' : g})) for g in groupinfo.keys()}
			menu = sshtml.buildMenu('Groups', 'groupItems', buttonLink='/groupctl.py?creategroup=1',
					buttonText='Create Group', items=links, active=gid)

			# Make html
			DATA = ''
			if gid:
				# Get membership level
				level = groups.get_membership_level(gid, uid)
				pid = groups.get_partner(gid, uid)
				users = userstable.SSUsers(DATABASE)

				# Html formats
				GENERAL_MEMBER_DATA = ''
				if level != groupstable.ADMIN:
					GENERAL_MEMBER_DATA = """<hr/>
						<form id="leaveGroup" action="/groupctl.py" method="post">
							<input type="hidden" name="gid" value="{gid}"/>
							<input type="hidden" name="leavegroup" value="1"/>
							<button class="warning"><a href="javascript:void(0);" onclick="document.getElementById('leaveGroup').submit()">Leave Group</a></button>
						</form>""".format(gid=gid)
				MODERATOR_MEMBER_DATA = ''
				if level >= groupstable.MOD:
					ERROR = '<p style="font-size: 14px;margin-top: 0; margin-bottom: 15px;"><font color="#a93226">{}</font><br/></p>'
					error = ''
					if 'noemail' in args:
						error = ERROR.format('Must provide a user\'s email')
					elif 'nouser' in args:
						error = ERROR.format('User does not exist')
					MODERATOR_MEMBER_DATA = """<hr/>
						<form id="addMember" action="/groupctl.py" method="post">
							<input type="text" placeholder="Enter user's email" name="email" required/>
							{error}
							<input type="hidden" name="gid" value="{gid}"/>
							<input type="hidden" name="addmember" value="1"/>
							<button><a href="javascript:void(0);" onclick="document.getElementById('addMember').submit()">Add Member</a></button>
						</form>
						<hr/>
						<form id="runSecretSanta" action="/groupctl.py" method="post">
							<input type="hidden" name="gid" value="{gid}"/>
							<button><a href="{link}">Run Secret Santa Assignment</a></button>
						</form>""".format(gid=gid, error=error, link=sshttp.build_redirect_uri('/getacc.py', '/ssctl.py?gid={}'.format(gid)))
				ADMIN_MEMBER_DATA = ''
				if level >= groupstable.ADMIN:
					ERROR = '<p style="font-size: 14px;margin-top: 0; margin-bottom: 15px;"><font color="#a93226">{}</font><br/></p>'
					error = ''
					if 'nopassword' in args:
						error = ERROR.format('Must provide a password')
					elif 'invalid' in args:
						error = ERROR.format('Invalid password')
					ADMIN_MEMBER_DATA = """<hr/>
						<form id="deleteGroup" action="/groupctl.py" method="post">
							<input type="hidden" name="gid" value="{gid}"/>
							<input type="hidden" name="deletegroup" value="1"/>
							<input type="password" placeholder="Enter your password" name="password"/>
							{error}
							<button class="warning"><a href="javascript:void(0);" onclick="document.getElementById('deleteGroup').submit()">Delete Group</a></button>
						</form>""".format(gid=gid, error=error)
				
				LIST_ITEM = '<div class="listitem">{item}</div>'
				REMOVE_MEMBER = """<form id="member{uid}Delete" action="/groupctl.py" method="post">
						<input type="hidden" name="gid" value="{gid}"/>
						<input type="hidden" name="uid" value="{uid}"/>
						<input type="hidden" name="removemember" value="1"/>
						<a href="javascript:void(0);" onclick="document.getElementById('member{uid}Delete').submit()" class="warning"><i class="fas fa-times-circle"></i></a>
					</form>"""
				SET_MOD = """<form id="member{uid}Elevate" action="/groupctl.py" method="post">
						<input type="hidden" name="gid" value="{gid}"/>
						<input type="hidden" name="uid" value="{uid}"/>
						<input type="hidden" name="setmoderator" value="1"/>
						<a href="javascript:void(0);" onclick="document.getElementById('member{uid}Elevate').submit()"><i class="fas fa-plus-circle"></i></a>
					</form>"""
				REMOVE_MOD = """<form id="member{uid}Elevate" action="/groupctl.py" method="post">
						<input type="hidden" name="gid" value="{gid}"/>
						<input type="hidden" name="uid" value="{uid}"/>
						<input type="hidden" name="setmoderator" value="0"/>
						<a href="javascript:void(0);" onclick="document.getElementById('member{uid}Elevate').submit()" class="warning"><i class="fas fa-minus-circle"></i></a>
					</form>"""
				PARTNER_INFO = 'Targets have not been assigned yet. Please wait for assignment.'
				if pid:
					partner = users.get_user_by_id(pid, cols=['name', 'email'])
					PARTNER_INFO = '<p>Your assigned target is {} (email={})</p>'.format(*partner)

				# Make memberlist
				memberlist = list()
				for m in groups.get_members_for(gid, cols=['uid', 'level']):
					member = users.get_user_by_id(m[0], cols=['name'])
					item = '<p>{name}</p>'
					if level == groupstable.ADMIN:
						if m[1] == groupstable.GENERAL:
							item += REMOVE_MEMBER + SET_MOD
							item = item.format(name=member[0], uid=m[0], gid=gid)
						elif m[1] == groupstable.MOD:
							item += REMOVE_MEMBER + REMOVE_MOD 
							item = item.format(name=member[0], uid=m[0], gid=gid)
						else:
							item = item.format(name=member[0])
					else:
						if level > m[1]:
							item += REMOVE_MEMBER
							item = item.format(name=member[0], uid=m[0], gid=gid)
						else:
							item = item.format(name=member[0])
					memberlist.append(LIST_ITEM.format(item=item))
				
				DATA = """<h1>{groupname}</h1>
					<div class="col-6 col-s-12">
						{partnerinfo}
						{moderatordata}
						{generaldata}
						{admindata}
					</div>
					<div class="col-6 col-s-12 list">
						<div class="listtitle">
							Members
						</div>
						<div class="listitems">
							{listitems}
						</div>
					</div>""".format(groupname=groupinfo[gid], partnerinfo=PARTNER_INFO,
							moderatordata=MODERATOR_MEMBER_DATA, generaldata=GENERAL_MEMBER_DATA,
							admindata=ADMIN_MEMBER_DATA, listitems='\n'.join(memberlist))
			else:
				DATA = '<h3>You have no groups</h3>'
			ASIDE = """<h2>What is it?</h2>
				<p>Your groups are listed here. Whatever shows up are groups you have either created or been invited to.</p>
				<h2 style="margin-top: 15px;">How does it work?</h2>
				<p>Choose a group from the list and it will show you the members and your assigned secret santa target, if they have been assigned. If no group shows up, create one now!</p>
				<p>Only group owners and moderators can assign the targets so wait for one of them to kick it off!</p>
				<p>Moderators can add and remove group members. Only owners can set moderators and delete the group.</p>"""
			MOBILE = '<p align="center"><br/><button><a href="{}">Create a Group Now</a></button></p>'.format(sshttp.build_redirect_uri('/getacc.py', '/groupctl.py?creategroup=1'))
			replace = {
				'desktopNavLinks' : sshtml.buildDesktopNavLinks('Groups'),
				'navLinks' : sshtml.buildNavLinks('Groups'),
				'accountLinks' : sshtml.buildAccountLinks(True),
				'body' : sshtml.buildMenuBody(menu=menu, data=DATA, aside=ASIDE, mobile=MOBILE)
			}
			sshttp.send200(sshtml.buildContainerPage(replace))
	else:
		sshttp.senderror(403)

except:
	sshttp.senderror(500)
	import sys, traceback
	traceback.print_exc(file=sys.stderr)

