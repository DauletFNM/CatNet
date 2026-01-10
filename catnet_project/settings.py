import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Твои приложения
    'core',
    
    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # NEW! Добавляем для красивых форм
    'crispy_forms',
    'crispy_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'catnet_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'catnet_project.wsgi.application'

# База данных Supabase
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

# Настройки почты через Resend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend" # Для теста в консоли

# Когда будешь готов отправлять реально:
import resend

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

# Путь к нашему новому классу (замени 'catnet_project' на имя твоей папки с settings)
EMAIL_BACKEND = 'catnet_project.email_backend.ResendApiBackend'

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
# Важно: Resend на бесплатном тарифе требует этот адрес, если домен не привязан:
DEFAULT_FROM_EMAIL = "onboarding@resend.dev"

# Настройки Allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Находишь это в settings.py
ALLOWED_HOSTS = ['*'] # Для начала можно оставить так

# Добавь в конец файла для статических файлов (дизайна)
import os
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# NEW! Современные настройки регистрации для версии 6.0+
ACCOUNT_LOGIN_METHODS = {'username', 'email'}  # Способы входа
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Новый способ управления полями при регистрации
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

# NEW! Настройки Crispy Forms (для красоты)
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import os

# Указываем путь к папке со статикой
STATIC_URL = 'static/'

# Папка, куда Django соберет все файлы дизайна для сервера Render
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Это поможет Django корректно работать с файлами на сервере
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CSP_SCRIPT_SRC = (
    "'self'", 
    "'unsafe-inline'", 
    "'unsafe-eval'",  # Обязательно!
    "https://unpkg.com", 
    "https://cdn.jsdelivr.net"
)