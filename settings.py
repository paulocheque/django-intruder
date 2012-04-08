DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': ':memory:',
        'NAME': '/tmp/intruder.sqlite.db',
    }
}

INSTALLED_APPS = (
    'django_nose',
    'coverage',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',

    'intruder',

    'example',
)

INTRUDER_DEFAULT_REDIRECT_VIEWS = (
                      ('', '-----'),
                      ('intruder.views.feature_under_maintenance', 'Feature under maintenance'),
                      ('intruder.views.feature_is_no_longer_available', 'Feature is no longer available'))

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
#    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'intruder.middleware.IntruderMiddleware',
)

ROOT_URLCONF = 'urls'
