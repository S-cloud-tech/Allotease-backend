import os
from pathlib import Path
from decouple import config
import dj_database_url  

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Secret key
SECRET_KEY = config('SECRET_KEY')

AUTH_USER_MODEL = 'accounts.Account'

# Debug
DEBUG = False

# Allowed Hosts
ALLOWED_HOSTS = []

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # For development
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # For production
EMAIL_HOST = 'smtp.gmail.com'  # email provider's SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD') 
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')


# Installed Apps
INSTALLED_APPS = [
    # Default Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Authentication
    'rest_framework',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Local apps
    'accounts',
    'main',

    # External apps
    'location_field.apps.DefaultConfig',
    'drf_yasg',
    'corsheaders',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', #whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', #corsheaders
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware", #allauth
]

# Root URL
ROOT_URLCONF = 'core.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Global templates
        # 'DIRS': [BASE_DIR / 'templates'],  # Global templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Default processors
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required by allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Change to PostgreSQL or others in production
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}


# Password Validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # Add more validators as needed
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default Auto Field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MapBox Map settings
LOCATION_FIELD = {
    'provider.mapbox.access_token': config('MAPBOX_TOKEN'),
    'provider.mapbox.max_zoom': 18,
    'provider.mapbox.id': 'mapbox.streets',
}
