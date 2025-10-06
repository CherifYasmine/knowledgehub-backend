from .base import *

# Production overrides
DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=["yourdomain.com"])
