@auth.requires_login()
def new_story():
    if auth.user_groups.keys():
      db.Story.team_id.default = auth.user_groups.keys()[0]
    else:
      response.flash = 'NULL USER GROUP, story will NOT save'

    if request.args(0) is not None:
      db.Story.sprint_id.default = request.args(0,cast=int)
      db.Story.backlogged.default = False
    else:
      db.Story.backlogged.default = True

    form = SQLFORM(db.Story, fields=['user_story', 'created_on', 'created_by'])
    if form.process().accepted:
        response.flash = 'story added'
        if request.args(0) is not None:
          redirect(URL('sprint', 'show_sprint', args=request.args(0,cast=int)))
        else:
          redirect(URL('team', 'backlog'))
    elif form.errors:
        response.flash = 'the form is invalid'

    return dict(form=form)

def show_story():
  this_story = db.Story(request.args(0,cast=int)) or redirect(URL('index'))
  db.Task.story_id.default = this_story.id

  form = SQLFORM(db.Task) if auth.user else 'You need to log in'
  if form.process().accepted:
    new_pts = this_story.story_points + int(form.vars.task_points)
    this_story.update_record(story_points = new_pts)
    response.flash = 'task added'

  alltasks = db(db.Task.story_id==this_story.id).select()
  if alltasks is None:
    this_story.update_record(completed='True')

  size=len(alltasks)
  #print size
  for task in alltasks:
    if task.status=="Done":
      size = size - 1
      #print size
  if size == 0:
    #print 'updating'
    this_story.update_record(completed='True')
  else:
    this_story.update_record(completed='False')
  db.Story.backlogged.show_if = (db.Story.backlogged==True)

  if auth.user_groups.keys():
    this_team_sprints = ((auth.user_groups.keys()[0]==db.Team.team_group) & (db.Sprint.team_id==db.Team.id))
    db.Story.sprint_id.requires=IS_EMPTY_OR(IS_IN_DB(db(this_team_sprints), 'Sprint.id', '%(sprint_goal)s'))
  movestory=SQLFORM(db.Story, this_story, showid=False, fields=['backlogged','sprint_id'])
  if movestory.process().accepted:
     response.flash = 'Story moved'

  return dict(story = this_story, tasks=alltasks, form=form, movestory=movestory)

def show_task():
    this_task = db.Task(request.args(0,cast=int)) or redirect(URL('index'))
    task_story = db.Story(this_task.story_id)
    form = SQLFORM(db.Task, this_task, showid=False, fields=['status', 'task_points', 'assigned'])
    if form.process().accepted:
        response.flash = 'task changed'
        redirect(URL('story', 'show_story', args=task_story.id))
    return dict(task=this_task, story=task_story, form=form)

@auth.requires_login()
def upcoming_tasks():
    import datetime
    today = datetime.date.today()
    margin = datetime.timedelta(days = 5)
    tasks=db(db.Task.assigned==auth.user_id).select()
    upcoming=None
    for task in tasks:
        if (today <= task.estimated_completion_time.date() <= today + margin):
            if upcoming is None:
                upcoming=[task.id]
            else:
                upcoming.append(task.id)
    return dict(tasks=upcoming)

@auth.requires_login()
def appointment_read():
    me=auth.user_id
    group=db(db.membership.user_id==me).select().first()
    groupid=group.group_id
    myteam=db(db.Team.team_group==groupid).select().first()
    mytasks=db(db.Task.assigned==me).select()
    mysprints=db(db.Sprint.team_id==myteam).select()
    return dict(mytasks=mytasks,mysprints=mysprints)

@auth.requires_login()
def mycal():
    me=auth.user_id
    group=db(db.auth_membership.user_id==me).select().first()
    groupid=group.group_id
    myteam=db(db.Team.team_group==groupid).select().first()
    mytasks=db(db.Task.assigned==me).select()
    mysprints=db(db.Sprint.team_id==myteam).select()
    return dict(mytasks=mytasks,mysprints=mysprints)
