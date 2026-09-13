"""
Settings used ONLY when developing on your own PC.
DEBUG=True here means Django shows detailed error pages - very helpful
while building, but NEVER safe to use on a real deployed system.
"""

from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']