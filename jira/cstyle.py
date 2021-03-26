''' Different styles for text in curses '''
import curses
from collections import namedtuple
from enum import Enum

BACKGROUND = 231
FOREGROUND = 0
HIGHLIGHT_1 = 2
HIGHLIGHT_2 = 39
TODO = 8
IN_PROGRESS = 27
DONE = 28
FAINT = 241

Theme = namedtuple('Theme', 'bg fg h1 h2 todo in_progress done faint')
DEFAULT_THEME = Theme(231, 0, 2, 39, 8, 27, 28, 241)
DARK_THEME = Theme(0, 231, 41, 45, 7, 38, 35, 253)

Themes = namedtuple('Themes', 'default dark')
themes = Themes(DEFAULT_THEME, DARK_THEME)

class Cstyle(Enum):
    ''' Different style codes for display text with curses '''
    NORMAL = 1
    HIGHLIGHT_1 = 2
    HIGHLIGHT_2 = 3
    IN_PROGRESS = 4
    TODO = 5
    DONE = 6
    FAINT = 7
    IN_PROGRESS_SUBTLE = 8
    TODO_SUBTLE = 9
    DONE_SUBTLE = 10

def init_cstyles(theme=themes.default):
    ''' set up all the color pairs '''
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(Cstyle.NORMAL.value, theme.fg, theme.bg)
    curses.init_pair(Cstyle.HIGHLIGHT_1.value, theme.bg, theme.fg)
    curses.init_pair(Cstyle.HIGHLIGHT_2.value, theme.h2, theme.bg)
    curses.init_pair(Cstyle.IN_PROGRESS.value, theme.bg, theme.in_progress)
    curses.init_pair(Cstyle.TODO.value, theme.bg, theme.todo)
    curses.init_pair(Cstyle.DONE.value, theme.bg, theme.done)
    curses.init_pair(Cstyle.FAINT.value, theme.faint, theme.bg)
    curses.init_pair(Cstyle.IN_PROGRESS_SUBTLE.value, theme.in_progress, theme.bg)
    curses.init_pair(Cstyle.TODO_SUBTLE.value, theme.todo, theme.bg)
    curses.init_pair(Cstyle.DONE_SUBTLE.value, theme.done, theme.bg)
    _init_user_cstyles(theme)


USER_COLORS = [10, 208, 38, 13, 9, 52, 5, 12, 8]
USER_COLORS_START_VALUE = 100

def _init_user_cstyles(theme):
    for index, color in enumerate(USER_COLORS):
        curses.init_pair(USER_COLORS_START_VALUE + index, color, theme.bg)

user_colors_dict = {}
def user_cstyle(user_id):
    ''' how to display the name or id of a particular user '''
    if user_id not in user_colors_dict.keys():
        user_colors_dict[user_id] = curses.color_pair(len(user_colors_dict.keys()) % len(USER_COLORS) + USER_COLORS_START_VALUE)
    return user_colors_dict[user_id]

def cstyle(cs=Cstyle.NORMAL, bold=False):
    ''' easy access to specific color pairs '''
    cp = curses.color_pair(cs.value)
    if bold:
        cp = cp | curses.A_BOLD
    return cp

def see_colors(stdscr):
    ''' for development purposes, see all the colors available '''
    stdscr.clear()
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    stdscr.addstr(0, 0, '{0} colors available'.format(curses.COLORS))
    _, maxx = stdscr.getmaxyx()
    maxx = maxx - maxx % 5
    x = 0
    y = 1
    for i in range(0, curses.COLORS):
        stdscr.addstr(y, x, '{0:5}'.format(i-1), curses.color_pair(i))
        x = (x + 5) % maxx
        if x == 0:
            y += 1
    stdscr.refresh()
    stdscr.getch()
