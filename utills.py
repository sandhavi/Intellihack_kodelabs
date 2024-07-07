import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def set_text(value):
    # Convert the value to a string if it is not None
    if value is None:
        return "None"
    else:
        return str(value)
