''' Abstractions for Jira Issues '''
# pylint: disable=unused-import
from multiprocessing import Queue
import json
import threading
import requests

from cstyle import cstyle, Cstyle, user_cstyle
from issue import Issue
from nice_window import NiceWindow
from open_file import open_file

from singletons import issues_list, query, Query, user

class IssuesWindow(NiceWindow):
    ''' Displays a list of Jira Issues'''
    _INDEX_WIDTH = 6
    _STATUS_WIDTH = 11
    _KEY_WIDTH = 11
    _ASSIGNEE_WIDTH = 8

    def __init__(self, win, logs_window):
        super().__init__(win)
        self._logs_window = logs_window
        self._selected_index = 0
        self._start_index = 0
        self._search_text = ''
        self._displayed_issues = []

    def write_content_helper(self, **kwargs):
        ''' writes the list of issues to the window '''
        self._update(issues_changed=kwargs['issues_changed'])

        if len(self._displayed_issues[self._start_index:]) == 0:
            self._addstr('No issues to display.')
            return
        for index, issue in enumerate(self._displayed_issues[self._start_index:]):
            if not self._write_issue(index, issue):
                break

    def _write_issue(self, index, issue):
        index_string = '({}) '.format(index + self._start_index).ljust(self._INDEX_WIDTH)
        status_string = issue.get_field('status_name').ljust(self._STATUS_WIDTH) + '  '
        assignee_id = issue.get_field('assignee').id
        assignee_string = assignee_id.ljust(self._ASSIGNEE_WIDTH)[:self._ASSIGNEE_WIDTH] + '  ' if query().scope != Query.SCOPE_ME else ''
        key_string = '[{}]'.format(issue.key).ljust(self._KEY_WIDTH)
        summary_string = issue.get_field('summary').ljust(self._width - len(index_string + status_string  + assignee_string + key_string))

        main_style = cstyle(Cstyle.HIGHLIGHT_1) if index + self._start_index == self._selected_index else None
        status_style = _status_category_style_subtle(issue.get_field('status_category_name'))
        assignee_style = user_cstyle(assignee_id)

        self._addstr(index_string, main_style, wrap=False, end_newline=False)
        self._addstr(status_string, main_style if main_style is not None else status_style, wrap=False, end_newline=False)
        self._addstr(assignee_string, main_style if main_style is not None else assignee_style, wrap=False, end_newline=False)
        self._addstr(key_string, main_style, wrap=False, end_newline=False)
        return self._addstr(summary_string, main_style, wrap=False)

    def _update(self, issues_changed=False, search_text=None, selected_index=None):
        ''' the main entrypoint for when something about the list of issues changes '''

        # if either of these are true, the set of issues to display has to be recalculated
        if issues_changed or search_text is not None:
            issues = issues_list().queried_issues

            # if the search text was changed, re-filter the issues
            if search_text is not None:
                self._search_text = search_text

            issues = list(filter(lambda issue: issue.matches_search(self._search_text), issues))

            self._displayed_issues = issues

        # if an index is specified, switch to that one -- otherwise, remember which issue was originally selected
        originally_selected_key = None
        if selected_index is not None:
            self._selected_index = selected_index
        else:
            selected_issue = self.get_selected_issue()
            if selected_issue is not None:
                originally_selected_key = selected_issue.key

        # restore the originally selected issue if not explicitly set
        if originally_selected_key is not None:
            displayed_keys = [issue.key for issue in self._displayed_issues]
            if originally_selected_key in displayed_keys:
                self._selected_index = displayed_keys.index(originally_selected_key)
            else:
                self._selected_index = 0

        # make sure our selected index is in bounds
        self._fix_selected_index()

        # handle scrolling up / down
        self._fix_start_index()

    def set_search_text(self, search_text=''):
        ''' only display issues matching this search '''
        self._update(search_text=search_text)

    def up(self):
        ''' select the previous issue '''
        self._update(selected_index=self._selected_index - 1)

    def down(self):
        ''' select the next issue '''
        self._update(selected_index=self._selected_index + 1)

    def num(self, n):
        ''' select the nth issue '''
        self._update(selected_index=n)

    def page(self, forward):
        ''' jump to the first issue on the next (or previous) page '''
        if forward:
            next_page_index = max(0, min(self._selected_index + self._height, len(self._displayed_issues) - self._height))
        else:
            next_page_index = max(0, self._selected_index - self._height)
        self._start_index = next_page_index
        if self._selected_index not in range(next_page_index, next_page_index + self._height):
            self.num(next_page_index)

    def get_selected_issue(self):
        ''' get the selected issue '''
        self._fix_selected_index()
        return None if len(self._displayed_issues) == 0 else self._displayed_issues[self._selected_index]

    def get_num_displayed_issues(self):
        ''' number of issues in list that match search'''
        return len(self._displayed_issues)

    def _on_dimensions_changed(self):
        self._fix_start_index()

    def _fix_selected_index(self):
        ''' makes sure the index is in bounds '''
        if self._selected_index < 0:
            self._selected_index = 0
        elif self._selected_index >= len(self._displayed_issues):
            self._selected_index = max(len(self._displayed_issues) - 1, 0)

    def _fix_start_index(self):
        ''' makes sure we can see the selected issue '''
        # we scrolled past the bottom
        if self._selected_index >= self._start_index + self._height:
            self._start_index = self._selected_index - self._height + 1
        # we scrolled past the top
        elif self._selected_index < self._start_index:
            self._start_index = self._selected_index
        # we have extra room in the window
        elif self._start_index + self._height > self.get_num_displayed_issues():
            self._start_index = max(self.get_num_displayed_issues() - self._height, 0)

def _status_category_style_subtle(status_category_name):
    ''' mapping from status category name to the style it should be displayed with '''
    if status_category_name == 'To Do':
        return cstyle(Cstyle.TODO_SUBTLE)
    if status_category_name == 'In Progress':
        return cstyle(Cstyle.IN_PROGRESS_SUBTLE)
    return cstyle(Cstyle.DONE_SUBTLE)
