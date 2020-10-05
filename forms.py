from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, \
    FieldList, DateField, validators, ValidationError, FloatField, FileField, \
    MultipleFileField, SelectMultipleField
from flask_wtf.file import FileRequired
from wtforms.validators import DataRequired, Email, Length, EqualTo, AnyOf, \
    IPAddress, HostnameValidation, UUID, NumberRange
import datetime
from uuid import UUID as check_uuid


def check_hostname(form, field, message='Wrong hostname!'):
    check = validators.HostnameValidation(allow_ip=False)
    if not check(field.data):
        raise ValidationError(message)


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = check_uuid(uuid_to_test, version=version)
    except ValueError:
        return False

    return str(uuid_obj) == uuid_to_test


def host_port_validator(form, field, message='Wrong host-port id format!'):
    try:
        m = field.data.split(':')
        if len(m) != 2:
            raise ValueError
        if not is_valid_uuid(m[0]) or not is_valid_uuid(m[1]):
            raise ValueError
    except ValueError:
        raise ValidationError(message)


def ip_host_port_validator(form, field, message='Wrong host-port id format!'):
    if field.data == '0:0':
        return
    try:
        m = field.data.split(':')
        if len(m) != 2:
            raise ValueError
        if not is_valid_uuid(m[0]):
            raise ValueError
        if not is_valid_uuid(m[1]) and m[1] != '0':
            raise ValueError
    except ValueError:
        raise ValidationError(message)


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
    end_date = DateField('end_date', format='%m/%d/%Y',
                         default=datetime.date(3000, 4, 13))
    teams = FieldList(StringField('teams'))
    users = FieldList(StringField('users'))


class NewHost(FlaskForm):
    ip = StringField('ip',
                     validators=[DataRequired(message='IP required!'),
                                 IPAddress(ipv4=True, ipv6=True,
                                           message='Wrong IPv4 or TPv6 format!')])

    description = StringField('description', default='')


class UpdateHostDescription(FlaskForm):
    comment = StringField('comment', default='')
    threats = FieldList(StringField('threats',
                                    validators=[AnyOf(['high',
                                                       'medium',
                                                       'low',
                                                       'check',
                                                       'info',
                                                       'checked'],
                                                      message='Wrong threat type!')]
                                    ), default=[]
                        )


class AddPort(FlaskForm):
    port = StringField('port', default='',
                       validators=[DataRequired(message='Insert port!')])
    service = StringField('other', default='')
    service_text = StringField('service_text', default='')
    description = StringField('description', default='')


class AddHostname(FlaskForm):
    hostname = StringField('hostname',
                           validators=[DataRequired(message='Domain required!'),
                                       check_hostname])
    comment = StringField('comment', default='')


class DeleteHostname(FlaskForm):
    hostname_id = StringField('hostname_id',
                              validators=[DataRequired(
                                  message='Hostname ID required!'),
                                  UUID(message='Wrong hostname-ID format!')])


class NewIssue(FlaskForm):
    name = StringField('name',
                       validators=[DataRequired(message='Name required!')])
    description = StringField('description', default='')
    ip_port = FieldList(StringField('ip_port',
                                    validators=[UUID(message='Wrong port id!')]
                                    ), default=[]
                        )
    host_port = FieldList(StringField('host_port',
                                      validators=[
                                          host_port_validator]
                                      ), default=[]
                          )
    url = StringField('url', default='')
    cve = StringField('cve', default='')
    cvss = FloatField('cvss', default=0.0, validators=[
        validators.NumberRange(min=0, max=10,
                               message="CVSS must be from 0.0 to 10.0!")])
    status = StringField('status', default='Need to check')
    criticality = FloatField('criticality', default=-1, validators=[
        validators.NumberRange(min=-1, max=10,
                               message="criticality must be from 0.0 to 10.0!")])
    fix = StringField('fix', default='')
    param = StringField('param', default='')
    issue_type = StringField('issue_type', default='custom',
                             validators=[AnyOf(
                                 ['custom', 'web', 'credentials', 'service'])])


class UpdateIssue(FlaskForm):
    name = StringField('name',
                       validators=[DataRequired(message='Name required!')])
    description = StringField('description', default='')
    ip_port = FieldList(StringField('ip_port',
                                    validators=[UUID(message='Wrong port id!')]
                                    ), default=[]
                        )
    host_port = FieldList(StringField('host_port',
                                      validators=[
                                          host_port_validator]
                                      ), default=[]
                          )
    url = StringField('url', default='')
    cvss = FloatField('cvss', default=0.0, validators=[
        validators.NumberRange(min=0, max=10,
                               message="CVSS must be from 0.0 to 10.0!")])
    status = StringField('status', default='Need to check')
    cve = StringField('cve', default='')
    cwe = IntegerField('cwe', default=0)
    criticality = FloatField('criticality', default=-1, validators=[
        validators.NumberRange(min=-1, max=10,
                               message="criticality must be from 0.0 to 10.0!")])
    fix = StringField('fix', default='')
    param = StringField('param', default='')
    issue_type = StringField('issue_type', default='custom',
                             validators=[AnyOf(
                                 ['custom', 'web', 'credentials', 'service'])])


class NewPOC(FlaskForm):
    file = FileField('file',
                     validators=[FileRequired(message='File required!')])
    service = StringField('service', validators=[ip_host_port_validator],
                          default='')
    comment = StringField('comment', default='')


class DeletePOC(FlaskForm):
    poc_id = StringField('poc_id',
                         validators=[DataRequired(message='POC id required!'),
                                     UUID(message='POC id invalid!')])


class NewNetwork(FlaskForm):
    ip = StringField('ip',
                     validators=[DataRequired(message='IP required!'),
                                 IPAddress(ipv4=True, ipv6=True,
                                           message='Wrong IPv4 or TPv6 format!')])
    mask = IntegerField('mask', default=0, validators=[
        validators.NumberRange(min=0, max=128, message="Mask must be 0..128!"),
        DataRequired(message='Mask required!')
    ])
    asn = IntegerField('asn', default=0)
    comment = StringField('comment', default='')


class DeleteNetwork(FlaskForm):
    network_id = StringField('network_id',
                             validators=[
                                 DataRequired(message='Network ID required!'),
                                 UUID(message='Network ID invalid!')])


class NewCredentials(FlaskForm):
    login = StringField('login',
                        validators=[],
                        default='')
    password_hash = StringField('password_hash',
                                validators=[],
                                default='')
    hash_type = StringField('hash_type',
                            validators=[],
                            default='')
    cleartext_password = StringField('cleartext_password',
                                     validators=[],
                                     default='')
    comment = StringField('comment',
                          validators=[],
                          default='')
    info_source = StringField('info_source',
                              validators=[],
                              default='')
    ip_port = FieldList(StringField('ip_port',
                                    validators=[UUID(message='Wrong port id!')]
                                    ), default=[]
                        )
    host_port = FieldList(StringField('host_port',
                                      validators=[
                                          host_port_validator]
                                      ), default=[]
                          )
    check_pwd = StringField('check_pwd',
                            validators=[AnyOf(['', 'top10k'])],
                            default='')


class UpdateCredentials(FlaskForm):
    login = StringField('login',
                        validators=[],
                        default='')
    password_hash = StringField('password_hash',
                                validators=[],
                                default='')
    hash_type = StringField('hash_type',
                            validators=[],
                            default='')
    cleartext_password = StringField('cleartext_password',
                                     validators=[],
                                     default='')
    comment = StringField('comment',
                          validators=[],
                          default='')
    info_source = StringField('info_source',
                              validators=[],
                              default='')
    ip_port = FieldList(StringField('ip_port',
                                    validators=[UUID(message='Wrong port id!')]
                                    ), default=[]
                        )
    host_port = FieldList(StringField('host_port',
                                      validators=[
                                          host_port_validator]
                                      ), default=[]
                          )
    action = StringField('action',
                         validators=[],
                         default='')


class ExportCredsForm(FlaskForm):
    separator = StringField('separator',
                            validators=[],
                            default=';')
    export_type = StringField('export_type',
                              validators=[AnyOf(['passwords',
                                                 'user_pass',
                                                 'user_pass_variations'])],
                              default='')

    empty_passwords = IntegerField('empty_passwords',
                                   validators=[],
                                   default=0)

    login_as_password = IntegerField('login_as_password',
                                     validators=[],
                                     default=0)


class NewNote(FlaskForm):
    name = StringField('name',
                       validators=[
                           DataRequired(message='Note name required!')])


class EditNote(FlaskForm):
    note_id = StringField('note_id',
                          validators=[UUID(message='Wrong note id!')])
    text = StringField('text', validators=[], default='')
    action = StringField('action',
                         validators=[AnyOf(['Update', 'Delete'])],
                         default='Update')


class NewFile(FlaskForm):
    file = FileField('file',
                     validators=[FileRequired(message='File required!')])
    ip_port = FieldList(StringField('ip_port',
                                    validators=[UUID(message='Wrong port id!')]
                                    ), default=[]
                        )
    host_port = FieldList(StringField('host_port',
                                      validators=[
                                          host_port_validator]
                                      ), default=[]
                          )
    description = StringField('description', default='')

    filetype = StringField('filetype',
                           validators=[AnyOf(['binary', 'text', 'image'])],
                           default='')


class EditFile(FlaskForm):
    action = StringField('action',
                         validators=[AnyOf(['delete'])],
                         default='delete')


class EditProjectSettings(FlaskForm):
    name = StringField('name',
                       validators=[DataRequired(message='Name required!')])
    description = StringField('description', default='')
    project_type = StringField('type', validators=[
        DataRequired(message='Type required!'),
        AnyOf(['pentest'])], default='pentest')
    scope = StringField('scope', default='')
    archive = IntegerField('archive', default=0)
    start_date = DateField('start_date', format='%m/%d/%Y',
                           default=datetime.date.today())
    end_date = DateField('end_date', format='%m/%d/%Y',
                         default=datetime.date(3000, 4, 13))
    teams = FieldList(StringField('teams'))
    users = FieldList(StringField('users'))
    action = StringField('action',
                         validators=[AnyOf(['Update', 'Archive', 'Activate'])],
                         default='Update')


class NmapForm(FlaskForm):
    files = MultipleFileField('files')
    add_no_open = IntegerField('add_no_open', default=0)
    rule = StringField('rule',
                       validators=[AnyOf(['open', 'filtered', 'closed'])],
                       default='open')


class NessusForm(FlaskForm):
    xml_files = MultipleFileField('xml_files')
    add_info_issues = IntegerField('add_info_issues', default=0)


class DeleteHostIssue(FlaskForm):
    issue_id = StringField('issue_id',
                           validators=[UUID(message='Wrong issue id!')]
                           )


class DeletePort(FlaskForm):
    port_id = StringField('port_id',
                          validators=[UUID(message='Wrong port id!')]
                          )


class NiktoForm(FlaskForm):
    xml_files = MultipleFileField('xml_files')
    csv_files = MultipleFileField('csv_files')
    json_files = MultipleFileField('json_files')


class AcunetixForm(FlaskForm):
    files = MultipleFileField('files')
    auto_resolve = IntegerField('auto_resolve', default=0)
    host = StringField('host', default='')


class MultiplePortHosts(FlaskForm):
    port = StringField('port',
                       validators=[DataRequired(message='Port required!')])
    service = StringField('service', default='other')
    description = StringField('description', default='')
    host = FieldList(
        StringField('host', validators=[UUID(message='Wrong host id!')],
                    default=''))


class NewChat(FlaskForm):
    name = StringField('name',
                       validators=[
                           DataRequired(message='Chat name required!')])


class NewMessage(FlaskForm):
    message = StringField('host', validators=[
        DataRequired(message='Does not allow empty messages!')])


class ExportHosts(FlaskForm):
    network = StringField('network', default='')
    port = StringField('port', default='')
    ip_hostname = StringField('ip_hostname', default='')
    service = StringField('service', default='')
    issue_name = StringField('issue_name', default='')
    comment = StringField('comment', default='')
    threat = SelectMultipleField('threat', choices=[('high', 'high'),
                                                    ('medium', 'medium'),
                                                    ('low', 'low'),
                                                    ('info', 'info'),
                                                    ('check', 'check'),
                                                    ('checked', 'checked')])
    separator = StringField('separator', default='[newline]')
    filename = StringField('filename', default='export')
    filetype = StringField('filetype',
                           validators=[AnyOf(['txt', 'xml', 'csv', 'json'])])
    hosts_export = StringField('hosts_export',
                               validators=[AnyOf(['ip&hostname',
                                                  'ip',
                                                  'hostname',
                                                  'ip&hostname_unique'])])
    add_ports = IntegerField('add_ports', default=0)
    open_in_browser = IntegerField('open_in_browser', default=0)


class NewHTTPSniffer(FlaskForm):
    name = StringField('name', validators=[
        DataRequired(message='Does not allow empty name!')])


class EditHTTPSniffer(FlaskForm):
    status = IntegerField('status', default=200, validators=[
        validators.NumberRange(min=100, max=526,
                               message="Status must be from 100 to 526!")])
    location = StringField('location', default='')
    body = StringField('body', default='')
    submit = StringField('submit', default='Update',
                         validators=[AnyOf(['Update', 'Clear'])])


class AddConfig(FlaskForm):
    config_name = StringField('config_name',
                              validators=[AnyOf(['shodan', 'zeneye'])])
    config_value = StringField('config_value',
                               validators=[
                                   DataRequired(message='Data required!')])
    action = StringField('action',
                         validators=[AnyOf(['Add', 'Delete'])])


class AddReportTemplate(FlaskForm):
    template_name = StringField('template_name',
                                validators=[
                                    DataRequired(message='Data required!')])
    file = FileField('file',
                     validators=[FileRequired(message='Template required!')])


class DeleteReportTemplate(FlaskForm):
    template_id = StringField('template_id',
                              validators=[UUID(message='Wrong template id!')],
                              default='')


class ReportGenerate(FlaskForm):
    template_id = StringField('template_id',
                              validators=[],
                              default='')
    file = FileField('file',
                     validators=[])
    extentions = StringField('extentions',
                             validators=[],
                             default='')
