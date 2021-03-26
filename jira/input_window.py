''' Window for displaying and handling user input '''
import getpass
import subprocess
from cstyle import cstyle, Cstyle
from nice_window import NiceWindow

class InputWindow(NiceWindow):
    ''' Window for displaying and handling user input '''
    def __init__(self, win):
        super().__init__(win)
        self._prompt_text = ''
        self._input_text = ''
        self._quit_on_navigate = False
        self._executes = False

    def write_content_helper(self, **kwargs):
        ''' writes the input to the window '''
        self._addstr(self._prompt_text, cstyle(Cstyle.HIGHLIGHT_2), end_newline=False)
        self._addstr(self._input_text, cstyle(Cstyle.NORMAL), end_newline=False)

    def input_char(self, char):
        ''' add a char to the input '''
        self._input_text += char
        self._on_change()

    def backspace(self):
        ''' remove a char from the input '''
        self._input_text = self._input_text[:-1]
        self._on_change()

    def clear(self):
        ''' clears display and state '''
        self._prompt_text = ''
        self._input_text = ''
        self._on_change()

    def submit(self):
        ''' what to do when the user hits enter '''

    def cancel(self):
        ''' what to do when the user hits escape '''

    def _on_change(self):
        pass

    @property
    def quit_on_navigate(self):
        ''' when the user presses an arrow key, do we quit this input mode? '''
        return self._quit_on_navigate

    @property
    def executes(self):
        ''' do we execute the default command on submit? '''
        return self._executes

class BranchWindow(InputWindow):
    ''' Displays prompt for creating a branch based off of a ticket '''
    def __init__(self, win, logs_window, selected_issue_key):
        super().__init__(win)
        self._logs_window = logs_window
        self._prompt_text = 'Finish the branch name: '
        self._input_text = '{}/{}-'.format(getpass.getuser(), selected_issue_key)
        self._quit_on_navigate = True

    def submit(self):
        ''' Create a branch and log the result '''
        result = subprocess.run(['git', 'checkout', '-b', self._input_text], check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self._logs_window.log_stdout(result)

class SearchWindow(InputWindow):
    ''' Displays prompt for searching for an issue '''
    def __init__(self, win, issues_search):
        super().__init__(win)
        self._issues_search = issues_search
        self._executes = True
        self._prompt_text = 'Search for an issue: '

    def cancel(self):
        self._issues_search()

    def _on_change(self):
        self._issues_search(self._input_text)
