from .base import *

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ['localhost', '127.0.0.1', ]

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
]


# Other optional configurations:
# CORS_ALLOW_CREDENTIALS = True
