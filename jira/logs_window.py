''' Window for displaying logs '''
from time import gmtime, strftime
from nice_window import NiceWindow
from cstyle import cstyle, Cstyle

class LogsWindow(NiceWindow):
    ''' Window for displaying logs '''
    def __init__(self, win, refresh_controller_display):
        super().__init__(win)
        self._logs = []
        self._refresh_controller_display = refresh_controller_display

    def write_content_helper(self, **kwargs):
        ''' writes the logs to the window '''
        for line in self._logs[-self._height:]:
            if not self._addstr(line, cstyle(Cstyle.FAINT), wrap=False):
                break

    def log(self, text, refresh=True):
        ''' log text '''
        self._logs.append(_prepend_time(text))
        if refresh:
            self._refresh_controller_display()

    def log_stdout(self, result, refresh=True):
        ''' log the stdout of a system call '''
        self._logs += _prepend_time(result.stdout.decode("utf-8")).splitlines()
        if refresh:
            self._refresh_controller_display()

    def get_num_lines(self):
        ''' how many lines of logs we have '''
        return len(self._logs)

def _prepend_time(data):
    if not data.startswith('\n'):
        return strftime("%H:%M:%S ", gmtime()) + data
    return data
