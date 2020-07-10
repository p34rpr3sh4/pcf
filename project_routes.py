from __main__ import app
from app import check_session, db, session, redirect, render_template
from functools import wraps


def check_project_access(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        project_id = kwargs['project_id']
        current_project = db.check_user_project_access(str(project_id),
                                                       session['id'])
        if not current_project:
            return redirect('/projects/')
        kwargs['current_project'] = current_project
        return fn(*args, **kwargs)

    return decorated_view


@app.route('/project/<uuid:project_id>/', methods=['GET'])
@check_session
@check_project_access
def project_index(project_id, current_project):
    return render_template('project-pages/stats/statslist.html',
                           current_project=current_project)


@app.route('/project/<uuid:project_id>/hosts/', methods=['GET'])
@check_session
@check_project_access
def hosts(project_id, current_project):
    return render_template('project-pages/ip-list/projectiplist.html',
                           current_project=current_project)
