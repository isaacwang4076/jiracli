''' A representation of a Jira Issue '''
from collections import namedtuple
from dateutil import parser

JiraUser = namedtuple("JiraUser", "name id email")
def _jira_user(user_dict):
    if user_dict is None:
        return JiraUser('unknown', 'unknown', 'unknown')
    return JiraUser(name=user_dict.get('displayName', None), id=user_dict.get('key', None), email=user_dict.get('emailAddress', None))

def _parse_jira_time_string(time_string):
    return parser.parse(time_string).strftime('%Y-%m-%d %H:%M')

class Issue():
    ''' A representation of a Jira Issue '''
    SEARCH_OR = '|'
    SEARCH_AND = '&'
    _STATUS_ORDER = [status.lower() for status in ['In Review', 'Kick Off', 'In Progress', 'Ready', 'Groomed', 'Backlog', 'Done', 'Invalid']]  # from most to least interesting

    # keeps track of non-obvious paths to things in issue_dict['fields']
    _FIELD_LAMBDAS = {
        'status_name': lambda fields: fields['status']['name'],
        'status_category_name': lambda fields: fields['status']['statusCategory']['name'],
        'priority_id': lambda fields: fields['priority']['id'],
        'priority_name': lambda fields: fields['priority']['name'],
        'assignee': lambda fields: _jira_user(fields['assignee']),
        'creator': lambda fields: _jira_user(fields['creator']),
        'reporter': lambda fields: _jira_user(fields['reporter']),
        'updated': lambda fields: _parse_jira_time_string(fields['updated']),
    }

    def __init__(self, issue_dict):
        self.key = issue_dict['key']
        self._fields = issue_dict['fields']
        self._status_priority = self._STATUS_ORDER.index(self.get_field('status_name').lower())

    def get_field(self, name):
        ''' returns value for specified field'''
        return self._FIELD_LAMBDAS.get(name, lambda fields: fields[name])(self._fields)

    def matches_search(self, search):
        ''' returns whether this issue matches the search '''
        field_values = [self.get_field(field) for field in ['summary', 'description', 'status_name', 'status_category_name']] + \
                             [self.get_field(field).name for field in ['assignee', 'reporter', 'creator']] + \
                             [self.get_field(field).id for field in ['assignee', 'reporter', 'creator']]
        field_values_string = self.key + ''.join([value if value is not None else '' for value in field_values])
        search = search.rstrip(self.SEARCH_OR)
        search = search.rstrip(self.SEARCH_AND)
        return any(all(q in field_values_string.lower() for q in q.split(self.SEARCH_AND)) for q in search.lower().split(self.SEARCH_OR))

    def __gt__(self, other_issue):
        ''' greater than means LESS interesting '''
        if self._status_priority != other_issue._status_priority:
            return self._status_priority > other_issue._status_priority
        return self.get_field('updated') < other_issue.get_field('updated')

    def __str__(self):
        return '{0}   {1}   [{2}] {3}'.format(self.get_field('status_name').ljust(11), self.get_field('assignee').id.ljust(8)[:8], self.key.ljust(8), self.get_field('summary'))
