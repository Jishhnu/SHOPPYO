from .settings import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
ROOT_URLCONF = "Page.test_urls"

INSTALLED_APPS = [
    app
    for app in INSTALLED_APPS
    if not app.startswith("allauth")
]

MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE
    if middleware != "allauth.account.middleware.AccountMiddleware"
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
