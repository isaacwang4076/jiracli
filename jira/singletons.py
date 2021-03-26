''' Global variables '''
from collections import namedtuple

from issues_list import IssuesList

user_singleton = [None]
query_singleton = [None]
issues_list_singleton = [None]

def user():
    ''' Get the shared User object '''
    return user_singleton[0]

def query():
    ''' Get the shared Query object '''
    return query_singleton[0]

def issues_list():
    ''' Get the shared list of issues '''
    return issues_list_singleton[0]

def init_user(name, id_arg, email, host, project, token):
    ''' Initialize shared query '''
    user_singleton[0] = User(UserVars(name, id_arg, email, host, project, token))

def init_query(status, scope, team):
    ''' Initialize shared query '''
    query_singleton[0] = Query(status, scope, team)

def init_issues_list(on_issues_received, logs_window):
    ''' Initialize shared query '''
    issues_list_singleton[0] = IssuesList(on_issues_received, logs_window)

UserVars = namedtuple('UserVars', 'name, id, email, host, project, token')
class User():
    ''' Represents the user of this CLI'''
    def __init__(self, user_vars):
        self._user_vars = user_vars

    #pylint: disable=missing-function-docstring
    @property
    def name(self):
        return self._user_vars.name

    @property
    def id(self):
        return self._user_vars.id

    @property
    def email(self):
        return self._user_vars.email

    @property
    def host(self):
        return self._user_vars.host

    @property
    def project(self):
        return self._user_vars.project

    @property
    def token(self):
        return self._user_vars.token

_jql_list_string = lambda l: ','.join(["'{}'".format(e) for e in l])

class Query():
    ''' Represents the specifications for issues for this runtime, must be initialized after User '''
    STATUS_ALL = 'all'
    STATUS_OPEN = 'open'
    STATUS_DONE = 'done'
    STATUS_TODO = 'todo'
    STATUS_KANBAN = 'kanban'

    SCOPE_ME = 'me'
    SCOPE_TEAM = 'team'
    SCOPE_PROJECT = 'project'

    def __init__(self, status, scope, team=None):
        self._status = status if status is not None else self.STATUS_ALL
        self._scope = scope if scope is not None else self.SCOPE_ME
        self._team = team if team is not None else []
        self._team.insert(0, user().id)

    @property
    def scope(self):
        ''' the scope of assignees we're displaying '''
        return self._scope

    @property
    def team(self):
        ''' a list of the ids of the user's teammates, including the user '''
        return self._team

    def filter_issue(self, issue):
        ''' returns whether an issue fits this query '''

        # filter by status
        if issue.get_field('status_name') not in self._status_list():
            return False

        # filter by scope
        assignee_id = issue.get_field('assignee').id
        if self._scope == self.SCOPE_ME and assignee_id != user().id:
            return False
        if self._scope == self.SCOPE_TEAM and assignee_id not in self._team:
            return False
        if self._scope == self.SCOPE_PROJECT:
            return True
        return True

    def request_url(self):
        ''' get the request url for this query '''
        url_format = 'https://{}/rest/api/2/search?jql=project={}+AND+status+in+({}){}'
        url = url_format.format(user().host,
                                user().project,
                                _jql_list_string(self._status_list()),
                                self._assignee_spec())
        return url

    def _assignee_spec(self):
        assignee_spec_format = '+AND+assignee+in+({})'
        if self._scope == self.SCOPE_ME:
            return assignee_spec_format.format(user().id)
        if self._scope == self.SCOPE_TEAM:
            return assignee_spec_format.format(_jql_list_string(self._team))
        return ''

    def _status_list(self):
        ''' returns the list of statuses this query accepts '''
        if self._status == self.STATUS_OPEN:
            return ['In Review', 'Kick Off', 'In Progress', 'Ready', 'Groomed', 'Backlog']
        if self._status == self.STATUS_DONE:
            return ['Done', 'Invalid']
        if self._status == self.STATUS_TODO:
            return ['Ready', 'Groomed', 'Backlog']
        if self._status == self.STATUS_KANBAN:
            return ['In Review', 'Kick Off', 'In Progress']
        return ['Done', 'Invalid', 'In Review', 'Kick Off', 'In Progress', 'Ready', 'Groomed', 'Backlog']  # default all
