"""
Django settings for Field Atlas project.
Generated for the Field Atlas// Placeholder: No changes needed for api.js in this snippetm.
"""
from pathlib import Path
import os
import dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if available
dotenv.load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'field-atlas-dev-secret-key-default-insecure')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

# Validate SECRET_KEY in production mode
if not DEBUG and (not SECRET_KEY or 'insecure' in SECRET_KEY.lower() or 'default' in SECRET_KEY.lower()):
    raise RuntimeError("Production security error: Insecure or default SECRET_KEY detected with DEBUG=False.")

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,.vercel.app').split(',') if host.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'outcomes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = 'backend.asgi.application'

# Database Configuration with MySQL primary and SQLite local fallback
USE_MYSQL = os.getenv('USE_MYSQL', 'False').lower() in ('true', '1', 'yes')

if USE_MYSQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'field_atlas'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
else:
    # On Vercel serverless environment, local filesystem is read-only except /tmp
    db_path = Path('/tmp/db.sqlite3') if os.getenv('VERCEL') else (BASE_DIR / 'db.sqlite3')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_path,
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'outcomes.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

# Internationalization and 11-language support
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('hi', 'हिन्दी (Hindi)'),
    ('mr', 'मराठी (Marathi)'),
    ('bn', 'বাংলা (Bengali)'),
    ('ta', 'தமிழ் (Tamil)'),
    ('te', 'తెలుగు (Telugu)'),
    ('kn', 'ಕನ್ನಡ (Kannada)'),
    ('gu', 'ગુજરાતી (Gujarati)'),
    ('pa', 'ਪੰਜਾਬੀ (Punjabi)'),
    ('ml', 'മലയാളം (Malayalam)'),
    ('ur', 'اردو (Urdu)'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Profile uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email Configuration (Console for development so OTPs appear in terminal; SMTP for production)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '1025'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() in ('true', '1')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Field Atlas <noreply@fieldatlas.in>')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session Cookie and Security Settings
SESSION_COOKIE_AGE = 86400 * 14  # 14 days
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
# Cross-origin deployment (frontend/backend on different Vercel subdomains)
# SameSite=None + Secure=True is required for cross-origin cookie sharing
SESSION_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
CSRF_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'

# Production SSL & Cookie Security
SESSION_COOKIE_SECURE = not DEBUG  # Must be True when SameSite=None
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() in ('true', '1')

# Structured Python Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'field_atlas': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Cross-Origin Resource Sharing (CORS) for decoupled frontend
# CORS_ALLOW_ALL_ORIGINS must be False when CORS_ALLOW_CREDENTIALS=True
# (browsers reject wildcard CORS with credentials)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8080,http://localhost:8000,https://skill-pulse-frontend.vercel.app,https://employee-trackerr.vercel.app,https://skill-pulse-employeetracker.vercel.app,https://skillpulse-employeetrackerr.vercel.app,https://skillpulse-employeetracker.com',
    ).split(',') if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

# CSRF Trusted Origins for cross-origin forms & requests
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.getenv(
        'CSRF_TRUSTED_ORIGINS',
        'http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8080,http://localhost:8000,https://*.vercel.app,https://employee-trackerr.vercel.app,https://skill-pulse-employeetracker.vercel.app,https://skillpulse-employeetrackerr.vercel.app,https://skillpulse-employeetracker.com',
    ).split(',') if origin.strip()
]
