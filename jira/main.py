#!/usr/bin/env python3

''' Main entry point for jira issue interaction '''
import argparse
import curses
import sys

# from jira_window import JiraWindow
from window_controller import WindowController, InputReader
from cstyle import init_cstyles, cstyle, themes
from singletons import init_query, init_user, Query
from open_file import open_file

LOG_FILE = '/tmp/jira_cli/log'

class LogStream():
    ''' spits out logs right away and prepends time '''
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        ''' write and flush immediately '''
        self.stream.write(data)
        self.stream.flush()
    def writelines(self, datas):
        ''' write and flush immediately '''
        self.stream.writelines(datas)
        self.stream.flush()
    def __getattr__(self, attr):
        return getattr(self.stream, attr)

sys.stdout = LogStream(open_file(LOG_FILE, 'w'))
sys.stderr = LogStream(open_file(LOG_FILE, 'w'))

parser = argparse.ArgumentParser(description='Open up the Jira CLI')
status = parser.add_mutually_exclusive_group()
status.add_argument('-a', '--all', help='display all issues (default)', action='store_const', dest='status', const=Query.STATUS_ALL)
status.add_argument('-o', '--open', help='display open issues', action='store_const', dest='status', const=Query.STATUS_OPEN)
status.add_argument('-d', '--done', help='display done issues', action='store_const', dest='status', const=Query.STATUS_DONE)
status.add_argument('-k', '--kanban', help='display issues in progress', action='store_const', dest='status', const=Query.STATUS_KANBAN)
status.add_argument('-td', '--todo', help='display issues in the backlog', action='store_const', dest='status', const=Query.STATUS_TODO)

scope = parser.add_mutually_exclusive_group()
scope.add_argument('-m', '--me', help='display my issues (default)', action='store_const', dest='scope', const=Query.SCOPE_ME)
scope.add_argument('-t', '--team', help='display my team\'s issues', action='store_const', dest='scope', const=Query.SCOPE_TEAM)
scope.add_argument('-p', '--project', help='display my project\'s issues', action='store_const', dest='scope', const=Query.SCOPE_PROJECT)

args = parser.parse_args()

def main(stdscr):
    ''' main entry point for jira issue interaction '''
    init_cstyles()
    stdscr.bkgd(' ', cstyle())
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    init_user(name='Isaac Wang', id_arg='iwang', email='iwang@atlassian.com', host='hello.atlassian.net', project='CTE', token='mytoken')
    init_query(args.status, args.scope, _get_team_ids())
    window_controller = WindowController(stdscr)
    input_reader = InputReader(window_controller)
    c = stdscr.getch()
    while input_reader.handle_keystroke(c):
        c = stdscr.getch()

TEAM_FILE = '/usr/local/var/jira_cli/team'
def _get_team_ids():
    return open_file(TEAM_FILE).read().strip().split('\n')

curses.wrapper(main)
