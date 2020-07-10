from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, \
    FieldList, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, AnyOf
import datetime


class RegistrationForm(FlaskForm):
    email = StringField('email',
                        validators=[DataRequired(message='Email required!'),
                                    Email(message='Wrong email format!')])
    password1 = PasswordField('password1', [
        EqualTo('password2', message='Passwords must match!'),
        Length(min=8, message='Minimum password len=8!')
    ])
    password2 = StringField('password2',
                            validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = StringField('email',
                        validators=[DataRequired(message='Email required!'),
                                    Email(message='Wrong email format!')])
    password = PasswordField('password',
                             [DataRequired(message='Password required!')])


class ChangeProfileInfo(FlaskForm):
    email = StringField('email',
                        validators=[DataRequired(message='Email required!'),
                                    Email(message='Wrong email format!')])
    fname = StringField('fname', validators=[], default='')
    lname = StringField('lname', validators=[], default='')
    company = StringField('company', validators=[], default='')
    password = PasswordField('password',
                             [Length(min=8, message='Minimum password len=8!')])


class ChangeProfilePassword(FlaskForm):
    oldpassword = PasswordField('oldpassword', [
        Length(min=8, message='Minimum password len=8!')])
    password1 = PasswordField('password1', [
        EqualTo('password2', message='Passwords must match!'),
        Length(min=8, message='Minimum password len=8!')
    ])
    password2 = StringField('password2', validators=[DataRequired()])


class CreateNewTeam(FlaskForm):
    name = StringField('name', validators=[DataRequired('Name required!')])
    description = StringField('description', validators=[], default='')


class EditTeamInfo(FlaskForm):
    name = StringField('name',
                       validators=[DataRequired(message='Name required!')])
    email = StringField('email',
                        validators=[DataRequired(message='Email required!'),
                                    Email(message='Wrong email format!')])
    description = StringField('description', validators=[], default='')


class AddUserToProject(FlaskForm):
    email = StringField('email',
                        validators=[DataRequired(message='Email required!'),
                                    Email(message='Wrong email format!')])
    role = StringField('email',
                       validators=[DataRequired(message='Role required!'),
                                   AnyOf(['tester', 'admin'],
                                         message='Wrong role!')])


class AddNewProject(FlaskForm):
    name = StringField('name',
                       validators=[DataRequired(message='Name required!')])
    description = StringField('description', default='')
    project_type = StringField('type', validators=[
        DataRequired(message='Type required!'),
        AnyOf(['pentest'])], default='pentest')
    scope = StringField('scope', default='')
    archive = IntegerField('archive', default=1)
    start_date = DateField('start_date', format='%m/%d/%Y',
                           default=datetime.date.today())
    end_date = DateField('start_date', format='%m/%d/%Y',
                         default=datetime.date(3000, 4, 13))
    teams = FieldList(StringField('teams'))
    users = FieldList(StringField('users'))



