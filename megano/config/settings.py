"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-t43gvn83$n+gh3kt0!v9sj5$du8@o!ci9gb5sv%%q9ft^m6za^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "0.0.0.0",
    "127.0.0.1",
]


# Application definition
AUTH_USER_MODEL = "accountapp.User"
AUTH_EMAIL_VERIFICATION = True

DJANGO_ACCOUNT_SUPERUSER = {"email": "team@skill.box", "pass": "123"}
DJANGO_ACCOUNT_MODERATOR = {"email": "moderator@skill.box", "pass": "123"}
DJANGO_ACCOUNT_SELLER = {"email": "seller@skill.box", "pass": "123"}

EMAIL_FROM = "antonyhunter1001@gmail.com"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465  # 465-SSL 587
EMAIL_HOST_USER = "antonyhunter1001@gmail.com"
EMAIL_HOST_PASSWORD = "ruamhhgnbprtmiyj"
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_jinja',
    'rest_framework',
    'taggit',

    'admin_settings.apps.AdminSettingsConfig',
    'cart_and_orders.apps.CartAndOrdersConfig',
    'paymentapp.apps.PaymentappConfig',
    'shopapp.apps.ShopappConfig',
    'accountapp.apps.AccountappConfig',
    'profileapp.apps.ProfileappConfig',
    'histviewapp.apps.HistviewappConfig',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "shopapp.context_processors.categories_menu",
                "shopapp.context_processors.random_product_banners",
                "shopapp.context_processors.compare_list",
                "django.contrib.messages.context_processors.messages",
                "cart_and_orders.context_processors.cart_context",
            ],
            # django-jinja defaults
            "match_extension": ".jinja2",
            "match_regex": None,
            "app_dirname": "templates",
            "constants": {},
            "globals": {},
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DATE_FORMAT = "d F Y"
TIME_FORMAT = "H:i"
FILE_CHARSET = "utf-8"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Время кэширования в секундах
CATEGORY_MENU_CACHE_TIMEOUT = 86400
BANNER_CACHE_TIMEOUT = 600
PRODUCT_CACHE_TIMEOUT = 86400
TOP_PRODUCTS_CACHE_TIMEOUT = 86400

COMPARE_LIST_SESSION_ID = "compare_list"
CART_SESSION_ID = "cart"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "cache",
    }
}

FIXTURE_DIRS = [
    "fixtures",
]
