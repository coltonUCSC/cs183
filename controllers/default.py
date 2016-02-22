def index():
    sprint = db((db.Sprint.team_id==db.Team.id) & (db.Team.team_group==auth.user_groups.keys()[0])
    & (db.Sprint.start_date < request.now) & (db.Sprint.end_date > request.now)).select(db.Sprint.ALL).first()
    stories = db(sprint.id==db.Story.sprint_id).select(db.Story.ALL)
    tasks = db((sprint.id==db.Story.sprint_id) & (db.Task.story_id==db.Story.id)).select(db.Task.ALL)
    return dict(stories=stories, tasks=tasks, sprint=sprint)

def user():
    return dict(form=auth())
