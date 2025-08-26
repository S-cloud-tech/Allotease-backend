import os
from pathlib import Path
from decouple import config
import dj_database_url
from datetime import timedelta  

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Secret key
SECRET_KEY = config('SECRET_KEY')


# Debug
DEBUG = True

# Allowed Hosts
ALLOWED_HOSTS = ['127.0.0.1', '127.0.0.1:8000', 'allotease-backend.onrender.com',]
CSRF_TRUSTED_ORIGINS = ['https://allotease-backend.onrender.com', 'http://127.0.0.1:8000', ]


# KUDA
KUDA_KEY = config('KUDA_KEY')
KUDA_TEST = config('KUDA_TEST')
KUDA_EMAIL = config('KUDA_EMAIL')
KUDA_BASE_URL = config('KUDA_BASE_URL')

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
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'oauth2_provider',
    'social_django',
    'drf_social_oauth2',
    
    # Local apps
    'user',
    'main',
    'wallet',

    # External apps
    'location_field.apps.DefaultConfig',
    'drf_yasg',
    'corsheaders',
    'coreapi',
    'anymail',
]

AUTH_USER_MODEL = 'user.Account'

# Email
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # For development
EMAIL_BACKEND = 'anymail.backends.brevo.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD') 
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
BREVO_API_KEY = config('BREVO_API_KEY')

ANYMAIL = {
    "BREVO_API_KEY": config('BREVO_API_KEY')
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
      'rest_framework.renderers.JSONRenderer',  
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware", 
]


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('client_id'),
            'secret': config('secert'),
            'key': ''
        }
    }
}


# Root URL
ROOT_URLCONF = 'core.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', 
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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES['default'] = dj_database_url.parse(config('External_Database_URL'))

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


