''' A window that respects its neighbor's space '''
import textwrap

from abc import ABC, abstractmethod
from collections import namedtuple
from cstyle import cstyle

Dimensions = namedtuple('Dimensions', 'x y width height')

class NiceWindow(ABC):
    ''' A window that respects its neighbor's space '''
    def __init__(self, win):
        self._win = win
        self._x = self._y = self._width = self._height = 0
        self._dimensions_set = False

    def set_dimensions(self, dimensions, lpad=0, rpad=0, tpad=0, bpad=0):
        ''' update the dimensions and write content unless otherwise specified '''
        self._x = dimensions.x
        self._y = dimensions.y
        self._width = dimensions.width
        self._height = dimensions.height

        self._x += lpad
        self._width -= (lpad + rpad)
        self._y += tpad
        self._height -= (tpad + bpad)

        self._dimensions_set = True

        self._on_dimensions_changed()

    def _addstr(self, text, color_pair=None, end_newline=True, wrap=True):
        ''' writes to window within specified borders and returns whether we printed everything we wanted to '''
        if not self._dimensions_set:
            return False
        if color_pair is None:
            color_pair = cstyle()

        cury, curx = self._win.getyx()
        offset = ' '.ljust(curx - self._x)  # adjustment if we're starting from the middle of the window

        if not wrap:
            first_line = (offset + text)[:self._width][len(offset):]
            if len(first_line) < len(text):
                first_line = first_line[:-3] + '...'
            text_lines = [first_line]
        else:
            wrapped_text = textwrap.fill(offset + text, width=self._width, replace_whitespace=False, drop_whitespace=False)
            wrapped_text = wrapped_text[len(offset):]  # remove the offset now that it's done its job
            text_lines = wrapped_text.splitlines()
        max_lines = self._y + self._height - cury
        for index, line in enumerate(text_lines[:max_lines]):
            cury, curx = self._win.getyx()
            # if we're on a newline, start from the right x-coordinate
            if curx == 0:
                self._win.move(cury, self._x)
            if index + 1 < min(len(text_lines), max_lines) or end_newline:
                line += '\n'
            self._win.addstr(line, color_pair)
        return len(text_lines) <= max_lines


    def write_content(self, **kwargs):
        ''' writes its content '''
        if not self._dimensions_set:
            return
        self._win.move(self._y, self._x)
        self.write_content_helper(**kwargs)

    def _on_dimensions_changed(self):
        pass

    # pylint: disable=missing-function-docstring
    @abstractmethod
    def write_content_helper(self, **kwargs):
        pass
