from gluon.contrib.appconfig import AppConfig
myconf = AppConfig(reload=True)

db = DAL("sqlite://storage.sqlite")

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

db.define_table('Team',
    Field('Product_Owner', 'reference auth_user', default=auth.user_id, writable = False),
    Field('Product_Name', requires = IS_NOT_EMPTY()),
    Field('Team_Name', requires = IS_NOT_EMPTY()),
    Field('Team_Leader', 'reference auth_user'), #readable/writable status handled in controller
    Field('Team_Members', 'reference auth_membership'), #readable/writable status handled in controller
    Field('Product_Description', 'text', requires = IS_NOT_EMPTY()))

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

if auth.user_id != None:
    setGroup=auth.user_groups.copy()
elif auth.user_id is None:
    setGroup=["None","You Need to Log In"]
#default=auth.user.id

#row=db((db.currentgroup.userNum==auth.user.id) & (auth.user_id != None)).select().first()
#if row != None:
#    setUser=row.curteam

#elif row is None:
#    setUser="None"
#default=setUser,
db.define_table('story',
  Field('Team', 'reference Team'),
  Field('User_Story','text', requires = IS_NOT_EMPTY()),
  Field('Story_Points','integer',requires=IS_IN_SET(['0','1','2','3','5','8','13','21'])),
  Field('completed', type = 'boolean', default = 'False', readable=False),
  Field('created_on', 'datetime', default=request.now, writable = False),
  Field('created_by', 'reference auth_user', default=auth.user_id),
  )

db.story.Team.readable = False
db.story.completed.readable = False
db.story.created_by.writable = False

db.define_table('task',
  Field('name', requires = IS_NOT_EMPTY()),
  Field('Status','string', requires=IS_IN_SET(["To do", "In progress", "Done"]), default="To do"),
  Field('Assigned', 'reference auth_user', default=auth.user_id),
  Field('Estimated_Completion_Time', 'datetime', requires = IS_DATETIME()),
  Field('story_id', 'reference story')
  )

db.task.story_id.writable = db.task.story_id.readable = False
