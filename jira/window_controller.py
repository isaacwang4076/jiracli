''' Displays the UI for the issues screen '''
import curses
import sys
import webbrowser
from threading import Timer

from cstyle import cstyle
from singletons import user, init_issues_list, issues_list
from nice_window import Dimensions
from issues_window import IssuesWindow
from issue_details_window import IssueDetailsWindow
from logs_window import LogsWindow
from input_window import InputWindow, BranchWindow, SearchWindow

# pylint: disable=too-many-instance-attributes
# no sensible way to get around this
class WindowController():
    ''' Displays and controls windows in the issues screen '''
    _LPAD = 2
    _RPAD = 2
    _TPAD = 1

    def __init__(self, win):
        self._win = win
        self._logs_window = LogsWindow(win, self.refresh_display)
        self._issues_window = IssuesWindow(win, self._logs_window)
        self._issue_details_window = IssueDetailsWindow(win, self._issues_window.get_selected_issue)
        self._input_window = InputWindow(win)
        self._command_mode = True

        init_issues_list(lambda: self.refresh_display(issues_changed=True), self._logs_window)
        issues_list().load_cached_issues()
        issues_list().refresh_issues()

        self._enter_command_mode()
        self.refresh_display(issues_changed=True)

    @property
    def command_mode(self):
        ''' as opposed to input mode '''
        return self._command_mode

    def refresh_display(self, issues_changed=False):
        ''' clear and re-write everything '''
        self._win.clear()
        self._move_to_top()
        self._set_dimensions()
        self._issues_window.write_content(issues_changed=issues_changed)
        self._issue_details_window.write_content()
        self._logs_window.write_content()
        if self._command_mode:
            self._write_help()
        else:
            self._input_window.write_content()
        self._win.refresh()

    def open(self):
        ''' open the selected issue in jira '''
        selected_issue = self._issues_window.get_selected_issue()
        if selected_issue is not None:
            webbrowser.open('https://{}/browse/'.format(user().host) + selected_issue.key, new=2)
            return True
        self._logs_window.log('No issue selected')
        return False

    def branch(self):
        ''' prompt the user to create a branch based on this issue '''
        selected_issue = self._issues_window.get_selected_issue()
        if selected_issue is not None:
            self._input_window = BranchWindow(self._win, self._logs_window, selected_issue.key)
            self._enter_input_mode()
        else:
            self._logs_window.log('No issue selected')

    def search(self):
        ''' prompt the user to filter issues '''
        self._issues_window.set_search_text()
        self._input_window = SearchWindow(self._win, self._on_search_change)
        self._enter_input_mode()

    def _on_search_change(self, search_text=''):
        self._issues_window.set_search_text(search_text)
        self.refresh_display()

    def backspace(self):
        ''' delete from the input window '''
        self._input_window.backspace()

    def input_char(self, c):
        ''' add to the input window'''
        self._input_window.input_char(c)

    def end_input(self, canceled=False):
        ''' cancel or submit input '''
        if canceled:
            self._input_window.cancel()
        else:
            self._input_window.submit()
        self._enter_command_mode()

    def clear(self):
        ''' clears the search search '''
        self._issues_window.set_search_text()
        self.refresh_display()

    def up(self):
        ''' navigate up '''
        self._on_navigate()
        self._issues_window.up()
        self.refresh_display()

    def down(self):
        ''' navigate down'''
        self._on_navigate()
        self._issues_window.down()
        self.refresh_display()

    def _on_navigate(self):
        ''' respond to navigation '''
        if not self._command_mode and self._input_window.quit_on_navigate:
            self._enter_command_mode()

    def num(self, n):
        ''' jumps to specified issue '''
        self._issues_window.num(n)
        self.refresh_display()

    def page(self, forward):
        ''' navigates to the next (or previous) the page of issues '''
        self._on_navigate()
        self._issues_window.page(forward)

    def _enter_command_mode(self):
        curses.curs_set(0)
        self._command_mode = True
        self.refresh_display()

    def _enter_input_mode(self):
        curses.curs_set(1)
        self._command_mode = False
        self.refresh_display()

    def _write_help(self):
        self._win.move(self._win.getmaxyx()[0] - 2, 0)
        self._win.addstr(self._LPAD * ' ' + 'o: open, b: branch, s: search, c: clear, r: refresh, q: quit', cstyle())

    def _move_to_top(self):
        self._win.move(1, 0)

    # position and resize all the sub-windows
    def _set_dimensions(self):
        maxy, maxx = self._win.getmaxyx()

        # one line for input, one line for padding
        input_height = 2

        # a quarter of the screen or the number of logs, whichever is less
        logs_height = min(int(round(maxy * .25)), self._logs_window.get_num_lines() + self._TPAD)

        # to be divided between the list of issues and the issue details
        content_height = maxy - input_height - logs_height - 1

        # 65% of the content or the number of issues, whichever is less
        issues_height = min(int(round(content_height * .5)), len(issues_list().queried_issues) + 1 + self._TPAD)
        issues_width = maxx

        # the remaining content
        issue_details_height = content_height - issues_height
        issue_details_width = maxx

        # start just after the list of issues
        issue_details_x = 0
        issue_details_y = issues_height

        # if we don't have enough room to show the issue details, switch to side-by-side
        if issue_details_height < 15:
            issues_height = content_height
            issues_width = int(round(maxx / 2))
            issue_details_height = content_height
            issue_details_width = maxx - issues_width
            issue_details_x = issues_width
            issue_details_y = 0

        self._issues_window.set_dimensions(Dimensions(x=0, y=0, width=issues_width, height=issues_height),
                                           lpad=self._LPAD, tpad=self._TPAD, rpad=self._RPAD)
        self._issue_details_window.set_dimensions(Dimensions(x=issue_details_x, y=issue_details_y, width=issue_details_width, height=issue_details_height),
                                                  lpad=self._LPAD, tpad=self._TPAD, rpad=self._RPAD)
        self._logs_window.set_dimensions(Dimensions(x=0, y=content_height, width=issues_width, height=logs_height),
                                         lpad=self._LPAD, tpad=self._TPAD, rpad=self._RPAD)
        self._input_window.set_dimensions(Dimensions(x=0, y=content_height + logs_height, width=maxx - 1, height=input_height),
                                          lpad=self._LPAD, tpad=self._TPAD, rpad=self._RPAD)

class InputReader():
    ''' Reads input and delegates accordingly '''
    def __init__(self, wc):
        self._wc = wc
        self._num_reader = NumReader(wc)

    def parse_options(self, args):
        ''' parses options'''

    def handle_keystroke(self, c):
        ''' respond to user keystroke and return whether we should continue looping '''
        if c == curses.KEY_RESIZE:
            self._wc.refresh_display()
        elif c == curses.KEY_UP:
            self._wc.up()
        elif c == curses.KEY_DOWN:
            self._wc.down()
        elif self._wc.command_mode:
            if not self._handle_command(c):
                return False
        else:
            self._handle_input(c)
        self._wc.refresh_display()
        return True

    def _handle_command(self, c):
        if c == ord('q'):
            return False
        if c == ord('o'):
            self._wc.open()
        elif c == ord('b'):
            self._wc.branch()
        elif c == ord('s'):
            self._wc.search()
        elif c == ord('r'):
            issues_list().refresh_issues()
        elif c == ord('c'):
            self._wc.clear()
        elif c == ord(' '):
            self._wc.page(True)
        elif c in range(48, 58): # key codes for 0...9
            n = c - 48
            self._num_reader.read_num(n)
        elif c == 10:  # enter
            if self._wc.open():
                sys.exit()
        elif c == curses.KEY_RIGHT:
            self._wc.page(True)
        elif c == curses.KEY_LEFT:
            self._wc.page(False)
        return True

    def _handle_input(self, c):
        if c == 27:  # escape
            self._wc.end_input(True)
        elif c == 10:  # enter
            self._wc.end_input()
        elif c == 127:  # backspace
            self._wc.backspace()
        elif c in range(32, 127):
            self._wc.input_char(curses.unctrl(c).decode("utf-8"))

class NumReader():
    ''' Helps differentiate between someone typing '1' and then '0' and someone typing '10' '''
    _CACHE_SECONDS = 1.2  # how long we'll keep a typed digit (to allow people to input multiple digits)

    def __init__(self, wc):
        self._wc = wc
        self._cached_num = 0

    def read_num(self, new_digit):
        ''' update the cached number and schedule jumping to it '''
        self._cached_num = self._cached_num * 10 + new_digit
        self._wc.num(self._cached_num)
        Timer(self._CACHE_SECONDS, self._flush, [self._cached_num]).start()

    def _flush(self, old_cached_num):
        # if a number hasn't been input since
        if old_cached_num == self._cached_num:
            self._cached_num = 0
