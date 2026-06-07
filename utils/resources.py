import os
import sys

def resource_path(*parts):
    """Return an absolute path to a resource, working for development and when frozen by PyInstaller.

    Usage: resource_path('assets', 'fonts', 'MyFont.ttf')
    """
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base = os.path.dirname(current_dir)
    return os.path.join(base, *parts)
