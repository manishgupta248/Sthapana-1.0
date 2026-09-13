"""
Settings for the "everyday-use" hardened version.
DEBUG=False hides detailed error pages from anyone using the system,
which matters even on a single office PC.
"""

from .base import *  # noqa

DEBUG = False

# ALLOWED_HOSTS will be filled in from .env when we actually deploy this
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])