import sqlite3
from system.config_load import config_dict
from system.crypto_functions import *
import json


class Database:
    db_path = config_dict()['database']['path']
    cursor = None
    conn = None

    def __init__(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        return

    def return_arr_dict(self):
        ncols = len(self.cursor.description)
        colnames = [self.cursor.description[i][0] for i in range(ncols)]
        results = []
        for row in self.cursor.fetchall():
            res = {}
            for i in range(ncols):
                res[colnames[i]] = row[i]
            results.append(res)
        return results

    def insert_user(self, email, password):
        password_hash = hash_password(password)
        self.cursor.execute(
            "INSERT INTO Users(`id`,`email`,`password`) VALUES (?,?,?)",
            (gen_uuid(), email, password_hash)
        )
        self.conn.commit()
        return

    def select_user_by_email(self, email):
        self.cursor.execute('SELECT * FROM Users WHERE email=?', (email,))
        result = self.return_arr_dict()
        return result

    def select_user_by_id(self, user_id):
        self.cursor.execute('SELECT * FROM Users WHERE id=?', (user_id,))
        result = self.return_arr_dict()
        return result

    def update_user_info(self, user_id, fname, lname, email, company):
        self.cursor.execute('''UPDATE Users SET fname=?, 
                                                lname=?, 
                                                email=?, 
                                                company=? 
                               WHERE id=?''',
                            (fname, lname, email, company, user_id))
        self.conn.commit()
        return

    def update_user_password(self, id, password):
        password_hash = hash_password(password)
        self.cursor.execute('''UPDATE Users SET password=? WHERE id=?''',
                            (password_hash, id))
        self.conn.commit()
        return

    def insert_team(self, name, description, user_id):
        self.cursor.execute(
            "INSERT INTO Teams(`id`,`admin_id`,`name`,`description`,`admin_email`,`users`) "
            "VALUES (?,?,?,?,(SELECT `email` FROM Users WHERE `id`=? LIMIT 1),?)",
            (gen_uuid(),
             user_id,
             name,
             description,
             user_id,
             '{{"{}":"admin"}}'.format(user_id))  # initiation of json dict
        )
        self.conn.commit()
        return

    def select_user_teams(self, user_id):
        self.cursor.execute(
            'SELECT * FROM Teams WHERE '
            '`admin_id`=? OR '
            '`users` LIKE \'%\' || ? ||\'%\' ',
            (user_id, user_id))
        result = self.return_arr_dict()
        return result

    def update_team_info(self, team_id, name, admin_email, description):
        self.cursor.execute(
            '''UPDATE Teams SET name=?,admin_email=?,description=? WHERE id=?''',
            (name, admin_email, description, team_id))
        self.conn.commit()
        return

    def select_team_by_id(self, team_id):
        self.cursor.execute('SELECT * FROM Teams WHERE id=?', (team_id,))
        result = self.return_arr_dict()
        return result

    def update_new_team_user(self, team_id, user_email, role='tester'):
        curr_users_data = json.loads(
            self.select_team_by_id(team_id)[0]['users'])
        curr_user = self.select_user_by_email(user_email)[0]
        curr_users_data[curr_user['id']] = role
        self.cursor.execute(
            '''UPDATE Teams SET users=? WHERE id=?''',
            (json.dumps(curr_users_data), team_id))
        self.conn.commit()
        return

    def get_log_by_team_id(self, team_id):
        self.cursor.execute('SELECT * FROM Logs WHERE team_id=?', (team_id,))
        result = self.return_arr_dict()
        return result

    def insert_log(self, team_id, description, date, user_id):
        self.cursor.execute(
            '''INSERT INTO Logs(`id`,`team_id`,`description`,`date`,`user_id`) 
               VALUES (?,?,?,?,?)''',
            (gen_uuid(), team_id, description, date, user_id)
        )
        self.conn.commit()
        return

    def select_user_teams(self, user_id):
        self.cursor.execute(
            'SELECT * FROM Teams WHERE admin_id=? or users like "%" || ? || "%" ',
            (user_id, user_id))
        result = self.return_arr_dict()
        return result

    def select_user_team_members(self, user_id):
        teams = self.select_user_teams(user_id)
        members = []
        for team in teams:
            current_team = self.select_team_by_id(team['id'])[0]
            users = json.loads(current_team['users'])
            members += [user for user in users]
        members = list(set(members))

        members_info = []
        for member in members:
            members_info += self.select_user_by_id(member)
        return members_info

    def insert_new_project(self, name, description, project_type, scope,
                           start_date, end_date, auto_archive, testers,
                           teams, admin_id):
        project_id = gen_uuid()
        self.cursor.execute(
            "INSERT INTO Projects(`id`,`name`,`description`,`type`,`scope`,`start_date`,"
            "`end_date`,`auto_archive`,`status`,`testers`,`teams`,`admin_id`) "
            "VALUES (?,?,?,?,?,?,?,?,1,?,?,?)",
            (project_id,
             name,
             description,
             project_type,
             scope,
             int(start_date),
             int(end_date),
             int(auto_archive),
             json.dumps(testers),
             json.dumps(teams),
             admin_id)  # initiation of json dict
        )
        self.conn.commit()
        return project_id

    def check_admin_team(self, team_id, user_id):
        team = self.select_team_by_id(team_id)
        if not team:
            return False
        team = team[0]
        users = json.loads(team['users'])
        return team['admin_id'] == user_id or (
                user_id in users and users[user_id] == 'admin')

    def delete_user_from_team(self, team_id, user_id):
        self.cursor.execute('SELECT * FROM Teams WHERE id=?', (team_id,))
        team = self.return_arr_dict()
        if not team:
            return 'Team does not exist.'
        team = team[0]
        if team['admin_id'] == user_id:
            return 'Can\'t kick team creator.'
        users = json.loads(team['users'])
        if user_id not in users:
            return 'User is not in team'
        del users[user_id]

        self.cursor.execute(
            "UPDATE Teams set `users`=? WHERE id=?",
            (json.dumps(users), team_id)
        )
        self.conn.commit()

        return ''

    def devote_user_from_team(self, team_id, user_id):

        self.cursor.execute('SELECT * FROM Teams WHERE id=?', (team_id,))
        team = self.return_arr_dict()
        if not team:
            return 'Team does not exist.'
        team = team[0]
        if team['admin_id'] == user_id:
            return 'Can\'t devote team creator.'
        users = json.loads(team['users'])
        if user_id not in users:
            return 'User is not in team'
        if users[user_id] != 'admin':
            return 'User is not team administrator.'

        users[user_id] = 'tester'

        self.cursor.execute(
            "UPDATE Teams set `users`=? WHERE id=?",
            (json.dumps(users), team_id)
        )
        self.conn.commit()

        return ''

    def set_admin_team_user(self, team_id, user_id):

        self.cursor.execute('SELECT * FROM Teams WHERE id=?', (team_id,))
        team = self.return_arr_dict()
        if not team:
            return 'Team does not exist.'
        team = team[0]
        if team['admin_id'] == user_id:
            return 'Can\'t devote team creator.'
        users = json.loads(team['users'])
        if user_id not in users:
            return 'User is not in team'
        if users[user_id] != 'tester':
            return 'User is not team tester.'

        if users[user_id] == 'admin':
            return 'User is already admin.'

        users[user_id] = 'admin'

        self.cursor.execute(
            "UPDATE Teams set `users`=? WHERE id=?",
            (json.dumps(users), team_id)
        )
        self.conn.commit()
        return ''

    def select_team_projects(self, team_id):
        self.cursor.execute(
            '''SELECT * FROM Projects WHERE teams LIKE '%' || ? || '%' ''',
            (team_id,))
        result = self.return_arr_dict()
        return result

    def select_user_projects(self, user_id):
        projects = []
        user_teams = self.select_user_teams(user_id)
        for team in user_teams:
            team_projects = self.select_team_projects(team['id'])
            for team_project in team_projects:
                found = 0
                for added_project in projects:
                    if added_project['id'] == team_project['id']:
                        found = 1
                if not found:
                    projects.append(team_project)
        self.cursor.execute(
            '''SELECT * FROM Projects WHERE testers LIKE '%' || ? || '%' ''',
            (user_id,))
        user_projects = self.return_arr_dict()
        for user_project in user_projects:
            found = 0
            for added_project in projects:
                if added_project['id'] == user_project['id']:
                    found = 1
            if not found:
                projects.append(user_project)
        return projects

    def check_user_project_access(self, project_id, user_id):
        user_projects = self.select_user_projects(user_id)
        for user_project in user_projects:
            if user_project['id'] == project_id:
                return user_project
        return None

    def select_project_hosts(self, project_id):
        self.cursor.execute(
            '''SELECT * FROM Hosts WHERE project_id=?''',
            (project_id,))
        result = self.return_arr_dict()
        return result

    def select_ip_hostnames(self, host_id):
        self.cursor.execute(
            '''SELECT * FROM Hostnames WHERE host_id=?''',
            (host_id,))
        result = self.return_arr_dict()
        return result
