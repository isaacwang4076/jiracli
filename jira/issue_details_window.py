''' Displays details for a single Jira Issue '''
from cstyle import cstyle, Cstyle, user_cstyle
from singletons import user
from nice_window import NiceWindow

class IssueDetailsWindow(NiceWindow):
    ''' Displays details for a single Jira Issue '''
    def __init__(self, win, get_selected_issue):
        super().__init__(win)
        self._issue = None
        self._get_selected_issue = get_selected_issue

    def write_content_helper(self, **kwargs):
        self._issue = self._get_selected_issue()
        if self._issue is None:
            return
        self._addstr('[{}] {}'.format(self._issue.key, self._issue.get_field('summary')), cstyle(bold=True))
        self._write_field('Status', _normalized_status_name(self._issue.get_field('status_name')),
                          value_cstyle=_status_category_style(self._issue.get_field('status_category_name')))
        self._write_name_field('Assignee', 'assignee')
        self._write_name_field('Reporter', 'reporter')
        self._write_field('Updated', self._issue.get_field('updated'))
        self._write_field('Description', self._issue.get_field('description'))

    def _write_field(self, field_name, field_value, value_cstyle=None, write_if_none=False):
        if field_value is not None or write_if_none:
            self._addstr('{}: '.format(field_name), cstyle(bold=True), end_newline=False)
            self._addstr(field_value, value_cstyle)

    def _write_name_field(self, field_name, field_id):
        jira_user = self._issue.get_field(field_id)
        name = jira_user.name
        style = user_cstyle(jira_user.id)
        self._write_field(field_name, ' {} '.format(name), style)

STATUS_NAME_MAX_LENGTH = len('In Progress')
STATUS_NAME_BORDER = 2
def _normalized_status_name(status_name):
    target_length = STATUS_NAME_MAX_LENGTH + 2 * STATUS_NAME_BORDER
    left_pad = int(round((target_length - len(status_name)) / 2))
    return status_name.ljust(left_pad + len(status_name)).rjust(target_length)

def _status_category_style(status_category_name):
    if status_category_name == 'To Do':
        return cstyle(Cstyle.TODO)
    if status_category_name == 'In Progress':
        return cstyle(Cstyle.IN_PROGRESS)
    return cstyle(Cstyle.DONE)
