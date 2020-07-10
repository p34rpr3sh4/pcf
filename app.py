from flask import Flask, session, render_template, redirect, url_for, request
from flask import Markup
from flask_session import Session
from datetime import timedelta
from system.config_load import config_dict
import json
import calendar
import time
import urllib.parse
from functools import wraps

from system.db import Database

from flask_wtf.csrf import CSRFProtect, CSRFError

from system.crypto_functions import check_hash

from forms import *

db = Database()

csrf = CSRFProtect()

config = config_dict()

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
app.config['SECRET_KEY'] = config['main']['secret']

sess = Session()

sess.init_app(app)

csrf.init_app(app)

import project_routes


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400


def check_session(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if 'id' not in session:
            return redirect(url_for('login'))
        if not db.select_user_by_id(session['id']):
            return redirect(url_for('logout'))
        return fn(*args, **kwargs)
    return decorated_view


def check_team_access(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        team_id = kwargs['team_id']
        user_teams = db.select_user_teams(session['id'])
        current_team = {}
        for found_team in user_teams:
            if found_team['id'] == str(team_id):
                current_team = found_team
        if not current_team:
            return redirect(url_for('create_team'))
        kwargs['current_team'] = current_team
        return fn(*args, **kwargs)
    return decorated_view

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_form():
    form = LoginForm()
    error = None
    if form.validate():
        try:
            data = db.select_user_by_email(form.email.data)[0]
        except IndexError:
            data = []
        if not data:
            error = 'Email does not exist!'
        else:
            if not check_hash(data['password'], form.password.data):
                error = 'Wrong password!'
            else:
                session.update(data)
    return render_template('login.html', form=form, error=error)


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_form():
    form = RegistrationForm()
    error = None
    if form.validate():
        if len(db.select_user_by_email(form.email.data)) > 0:
            error = 'Email already exist!'
        else:
            db.insert_user(form.email.data, form.password1.data)
    return render_template('register.html', form=form, error=error)


@app.route('/profile', methods=['GET'])
@check_session
def profile():
    user_data = db.select_user_by_id(session['id'])[0]
    return render_template('profile.html', user_data=user_data)


@app.route('/profile', methods=['POST'])
@check_session
def profile_form():
    form1 = ChangeProfileInfo()
    form2 = ChangeProfilePassword()

    errors = []
    success_message = ''

    # editing profile data
    if 'change_profile' in request.form:
        form1.validate()
        if form1.errors:
            for field in form1.errors:
                errors += form1.errors[field]
        elif db.select_user_by_email(form1.email.data):
            errors += 'Email connected to another user!'
        else:
            try:
                data = db.select_user_by_id(session['id'])[0]
            except IndexError:
                data = []
            if not data:
                errors.append('User id does not exist!')
            else:
                if not check_hash(data['password'], form1.password.data):
                    errors.append('Wrong password!')
                else:
                    db.update_user_info(session['id'],
                                        fname=form1.fname.data,
                                        lname=form1.lname.data,
                                        email=form1.email.data,
                                        company=form1.company.data)
                    success_message = 'Profile information was updated!'

    # editing profile password
    elif 'change_password' in request.form:
        form2.validate()
        if form2.errors:
            for field in form2.errors:
                errors += form2.errors[field]
        else:
            try:
                data = db.select_user_by_id(session['id'])[0]
            except IndexError:
                data = []
            if not data:
                errors.append('User id does not exist!')
            elif form2.oldpassword.data == form2.password1.data:
                errors.append('New password is equal to old!')
            else:
                if not check_hash(data['password'], form2.oldpassword.data):
                    errors.append('Wrong password!')
                else:
                    db.update_user_password(session['id'], form2.password1.data)
                    success_message = 'Password was updated!'

    user_data = db.select_user_by_id(session['id'])[0]
    print(user_data)
    return render_template('profile.html', user_data=user_data,
                           success_message=success_message, errors=errors)


@app.route('/logout')
def logout():
    try:
        del session['id']
    except:
        pass
    return redirect(url_for('login'))


@app.route('/create_team', methods=['GET'])
@check_session
def create_team():
    return render_template('team-create.html')


@app.route('/create_team', methods=['POST'])
@check_session
def create_team_form():
    form = CreateNewTeam()
    form.validate()
    errors = []

    if form.errors:
        for field in form.errors:
            errors += form.errors[field]
    else:
        db.insert_team(form.name.data, form.description.data, session['id'])
    return render_template('team-create.html')


@app.route('/team/<uuid:team_id>/', methods=['GET'])
@check_session
@check_team_access
def team_page(team_id, current_team):

    edit_error = request.args.get('edit_error', default='', type=str)

    return render_template('teaminfo.html', current_team=current_team,
                           edit_error=edit_error)


@app.route('/team/<uuid:team_id>/', methods=['POST'])
@check_session
@check_team_access
def team_page_form(team_id, current_team):

    current_team_users = json.loads(current_team['users'])

    # forms list

    if session['id'] not in current_team_users:
        return redirect('/team/{}/'.format(current_team['id']))

    team_info_form = EditTeamInfo()
    team_info_form.validate()
    team_user_add_form = AddUserToProject()
    team_user_add_form.validate()

    errors = []
    # team info edit
    if 'change_info' in request.form:
        if team_info_form.errors:
            for field in team_info_form.errors:
                errors += team_info_form.errors[field]
            current_team = db.select_team_by_id(str(team_id))[0]
            return render_template('teaminfo.html', current_team=current_team,
                                   team_info_errors=errors)
        db.update_team_info(str(team_id),
                            team_info_form.name.data,
                            team_info_form.email.data,
                            team_info_form.description.data)
        current_team = db.select_team_by_id(str(team_id))[0]
        db.insert_log(current_team['id'],
                      'Changed team info!',
                      int(time.time()),
                      session['id'])
        return render_template('teaminfo.html', current_team=current_team)

    # team tester add
    elif 'add_user' in request.form:
        errors = []
        if team_user_add_form.errors:
            for field in team_user_add_form.errors:
                errors += team_user_add_form.errors[field]

        else:
            user_to_add = db.select_user_by_email(team_user_add_form.email.data)
            if not user_to_add:
                errors = ['User does not found!']
            elif user_to_add[0]['id'] in current_team_users:
                errors = ['User already added to {} group!'.format(
                    current_team_users[user_to_add[0]['id']])]
            else:
                db.update_new_team_user(current_team['id'],
                                        team_user_add_form.email.data,
                                        role=team_user_add_form.role.data)
                db.insert_log(current_team['id'],
                              'Added {} - {}'.format(
                                  team_user_add_form.role.data,
                                  user_to_add[0]['id']),
                              int(time.time()),
                              session['id'])

        current_team = db.select_team_by_id(str(team_id))[0]
        if team_user_add_form.role.data == 'tester':
            return render_template('teaminfo.html', current_team=current_team,
                                   add_tester_errors=errors)
        else:
            return render_template('teaminfo.html', current_team=current_team,
                                   add_admin_errors=errors)


@app.route('/new_project', methods=['GET'])
@check_session
def new_project():

    team_id = request.args.get('team_id', default='', type=str)
    if team_id != '':
        # team access check
        user_teams = db.select_user_teams(session['id'])
        current_team = {}
        for found_team in user_teams:
            if found_team['id'] == str(team_id):
                current_team = found_team
        if current_team == {}:
            return redirect(url_for('new_project'))

    return render_template('add-project.html', team_id=team_id)


@app.route('/new_project', methods=['POST'])
@check_session
def new_project_form():

    # team access check
    form = AddNewProject()
    form.validate()
    errors = []
    form.users.append_entry()
    form.users.append_entry()
    if form.errors:
        for field in form.errors:
            for err in form.errors[field]:
                errors.append(err)
        return render_template('add-project.html', errors=errors)

    # check teams access
    if not errors:
        for team_id in form.teams.data:
            current_team = db.select_team_by_id(team_id)
            if not current_team:
                errors.append('Team {} does not exist!'.format(team_id))
            elif session['id'] not in current_team[0]['users']:
                errors.append(
                    'User does not have access to team {}!'.format(team_id))

    # check user relationship

    form_users = [user for user in form.users.data if user]
    teams_array = db.select_user_teams(session['id'])
    if not errors:
        for user_id in form_users:
            found = 0
            for team in teams_array:
                if user_id in team['users']:
                    found = 1
            if not found or not db.select_user_by_id(user_id):
                errors.append('User {} not found!'.format(user_id))

    if errors:
        return render_template('add-project.html', errors=errors)

    # creating project
    start_time = calendar.timegm(form.start_date.data.timetuple())
    end_time = calendar.timegm(form.end_date.data.timetuple())

    project_id = db.insert_new_project(form.name.data,
                                       form.description.data,
                                       form.project_type.data,
                                       form.scope.data,
                                       start_time,
                                       end_time,
                                       form.archive.data,
                                       form_users,
                                       form.teams.data,
                                       session['id'])

    for team in form.teams.data:
        db.insert_log(current_team[0]['id'],
                      'Created project {}'.format(project_id),
                      int(time.time()),
                      session['id'])

    return redirect('/project/{}/'.format(project_id))


@app.route('/team/<uuid:team_id>/user/<uuid:user_id>/<action>',
           methods=['POST'])
@check_session
@check_team_access
def team_user_edit(team_id, user_id, action, current_team):

    # check if user admin
    if not db.check_admin_team(str(team_id), session['id']):
        return redirect(url_for('create_team'))

    error = ''

    if action == 'kick':
        error = db.delete_user_from_team(str(team_id), str(user_id))
        db.insert_log(str(team_id),
                      'Kicked user {}'.format(str(user_id)),
                      int(time.time()),
                      session['id'])

    if action == 'devote':
        error = db.devote_user_from_team(str(team_id), str(user_id))
        db.insert_log(str(team_id),
                      'Devoted user {}'.format(str(user_id)),
                      int(time.time()),
                      session['id'])

    if action == 'set_admin':
        error = db.set_admin_team_user(str(team_id), str(user_id))
        db.insert_log(str(team_id),
                      'Set admin for user {}'.format(str(user_id)),
                      int(time.time()),
                      session['id'])

    return redirect('/team/{}/?edit_error={}'.format(str(team_id), error))


@app.route('/profile/<uuid:user_id>/', methods=['GET'])
@check_session
def user_profile(user_id):
    user_data = db.select_user_by_id(str(user_id))[0]

    return render_template('user_profile.html', user_data=user_data)


@app.route('/projects/', methods=['GET'])
@check_session
def list_projects():
    return render_template('projects.html')


# init some global variables
@app.context_processor
def inject_stage_and_region():
    return dict(db=db,
                escape=Markup.escape,
                json_unpack=json.loads,
                format_date=lambda unix_time,
                                   str_format: datetime.datetime.fromtimestamp(
                    int(unix_time)).strftime(str_format),
                urlencode=urllib.parse.quote,
                time=time.time
                )


if __name__ == '__main__':
    if config_dict()['main']['ssl'] == '1':
        app.run(
            ssl_context=(config_dict()['ssl']['cert'],
                         config_dict()['ssl']['priv_key']),
            host=config_dict()['network']['host'],
            port=config_dict()['network']['port'],
            debug=(config_dict()['main']['debug'] == '1'))
    else:
        app.run(
            host=config_dict()['network']['host'],
            port=config_dict()['network']['port'],
            debug=(config_dict()['main']['debug'] == '1'))
