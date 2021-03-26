''' safely open a file '''
import os
from pathlib import Path

def open_file(file, mode='r'):
    ''' safely open a file '''
    directory = os.path.dirname(file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(file):
        Path(file).touch()

    return open(file, mode)
