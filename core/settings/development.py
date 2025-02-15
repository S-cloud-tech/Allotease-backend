from .base import *

DEBUG = True

ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
]


# Other optional configurations:
# CORS_ALLOW_CREDENTIALS = True
