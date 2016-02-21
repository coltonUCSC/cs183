# helper function to be called by the @auth.requires() decorator
def validate_product_owner():
    # Use this query to get the group id of caller
    group_id = auth.user_groups.keys()[0]
    team = db(db.Team.team_group == group_id).select().first()
    if team.product_owner == auth.user.id:
        return True
    else:
        return False

# Queries the database to see if the user exists
def validateuser(form):
    fullname = form.vars.name.split()
    fname = fullname[0]
    lname = fullname[1]
    rows = db((db.auth_user.first_name == fname)&
        (db.auth_user.last_name == lname)).select()
    if len(rows) < 1:
        form.errors = True
        response.flash = 'user does not exist!'

# Use this decorator for product-owner only functions
@auth.requires(lambda: validate_product_owner())
def invitemembers():
    form=FORM('User name:', INPUT(_name='name', requires=IS_NOT_EMPTY()), INPUT(_type='submit'))
    # Use onvalidation= to do custom checking/modifying before form is inserted into database
    if form.process(onvalidation=validateuser).accepted:
        fullname = form.vars.name.split()
        fname = fullname[0]
        lname = fullname[1]
        to = db((db.auth_user.first_name == fname)&
            (db.auth_user.last_name == lname)).select().first().id
        group_id = auth.user_groups.keys()[0]
        db.Invitations.insert(to_user=to, from_user=auth.user.id, from_group=group_id)
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form is invalid'
    return dict(form=form)

def acceptinvite():
    rows = db(db.Invitations.to_user == auth.user.id).select()
    return dict(rows=rows)

def accept():
    invite = db(db.Invitations.to_user == auth.user.id).select().first().from_group.id
    auth.add_membership(invite,auth.user.id)
    db(db.Invitations.to_user == auth.user.id).delete()
    response.flash = 'invites accepted'

def write_group(form):
    group_id = auth.add_group(form.vars.product_name, form.vars.product_description)
    auth.add_membership(group_id, auth.user.id)
    db.Team.team_group.default = group_id

@auth.requires_login()
def createteam():
        form = SQLFORM(db.Team, fields = ['product_owner', 'product_name', 'team_name',
                                          'product_description'])
        if form.process(onvalidation=write_group).accepted:
            response.flash = 'team created'
        elif form.errors:
            response.flash = 'form is invalid'
        return dict(form=form)

@auth.requires(lambda: validate_product_owner())
def manageteam():
    group_id = auth.user_groups.keys()[0]
    team = db(db.Team.team_group == group_id).select().first()
    form = SQLFORM(db.Team, record=team, fields = ['product_name', 'team_name', 'team_leader',
                                                    'product_description'])
    # Use this query to get a list of all team members
    team_members = db((db.auth_membership.user_id == db.auth_user.id)&
        (db.auth_group.id == db.auth_membership.group_id)).select(db.auth_user.ALL)
    db.Team.team_leader.requires = IS_IN_SET(team_members)
    if form.process().accepted:
        response.flash = 'team modified'
    elif form.errors:
        response.flash = 'error modifying team'
    return dict(form=form)

@auth.requires_login()
def viewteam():
    group_id = auth.user_groups.keys()[0]
    tname = db(db.Team.team_group == group_id).select().first().team_name
    rows = db((db.auth_membership.user_id == db.auth_user.id)&
        (db.auth_group.id == db.auth_membership.group_id)).select(db.auth_user.ALL)
    return dict(rows=rows, tname=tname)