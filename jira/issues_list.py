''' A list of issues '''
# pylint: disable=unused-import
from multiprocessing import Queue
from threading import Thread
import json
import requests

import singletons
from issue import Issue
from open_file import open_file

class IssuesList():
    ''' The master list of issues '''
    _ISSUE_CACHE_FILE = '/usr/local/var/jira_cli/cache/issues'

    ''' stores a list of issues'''
    def __init__(self, on_issues_received, logs_window):
        self._on_issues_received = on_issues_received
        self._logs_window = logs_window
        self._issue_dicts = {}
        self._queried_issues = []

    @property
    def queried_issues(self):
        ''' returns all issues that match the Query '''
        return self._queried_issues

    def refresh_issues(self):
        ''' request issues and update as needed '''
        self._logs_window.log('Updating issues...')
        Thread(target=self._refresh_issues, daemon=True).start()

    def _refresh_issues(self):
        url = singletons.query().request_url()
        start_index = 0
        max_results = 20
        while True:
            try:
                r = requests.get(url=url + '&startAt={}&maxResults={}'.format(start_index, max_results), auth=(singletons.user().email, singletons.user().token))
                data = r.json()
                num_issues_received = len(data['issues'])
                if num_issues_received == 0:
                    self._logs_window.log('Finished updating issues')
                    break

                ikeys = [issue['key'] for issue in data['issues']]
                ikeys.sort()
                self._process_received_issues(issue_dicts={issue['key']: issue for issue in data['issues']})
                start_index += num_issues_received
                max_results = 100
            except (ConnectionError, KeyError):
                self._logs_window.log('Failed to update issues')
                self._on_issues_received()
                break

    def load_cached_issues(self):
        ''' load cached issues issues and update as needed '''
        self._logs_window.log('Loading cached issues...')
        Thread(target=self._load_cached_issues(), daemon=True).start()

    def _load_cached_issues(self):
        try:
            self._update_issues(json.load(open_file(self._ISSUE_CACHE_FILE)))
            self._logs_window.log('Loaded {} issues from cache'.format(len(self._queried_issues)))
        except (ValueError, KeyError):
            self._logs_window.log('Failed to load cached issues')

    def _update_issues(self, issue_dicts):
        self._issue_dicts.update(issue_dicts)
        self._set_queried_issues()

        # cache the updated issues dict
        with open_file(self._ISSUE_CACHE_FILE, 'w') as outfile:
            outfile.write(json.dumps(self._issue_dicts))

    def _process_received_issues(self, issue_dicts):
        self._update_issues(issue_dicts)
        self._on_issues_received()

    def _set_queried_issues(self):
        all_issues = [Issue(issue_dict) for issue_dict in self._issue_dicts.values()]
        queried_issues = list(filter(singletons.query().filter_issue, all_issues))
        queried_issues.sort()
        self._queried_issues = queried_issues
