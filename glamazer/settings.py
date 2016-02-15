"""
Django settings for glamazer project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from production_settings import *
from os.path import abspath, dirname, join

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


HOURS = ['8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM', '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM', '8:00 PM']
STYLE_INDEXES = (('1', 'Venues',), ('2', 'Catering',),('3', 'Drinks',), ('4', 'Music',), ('5', 'Entertainment',), ('6', 'Equipment',), ('7', 'Decoration',), ('8', 'Party',))
DURATION = (('1800', '00:30',), ('3600', '1:00',),('5400', '1:30',), ('7200', '2:00',), ('9000', '2:30',), ('10800', '3:00',), ('12600', '3:30',), ('14400', '4:00',))
STATUS = ['PENDING', 'APPROVED', 'REJECTED']
LISTING_STATUS = ((0, 'Pending',), (1, 'Active',),(2, 'Not active',), (3, 'Forbidden',))
CANCELLED_BY = ['Not cancelled', 'Cancelled by artist', 'Cancelled by user']
NOTIFICATIONS_SHORT = [
     '{user} sent you a booking request ',
     '{artist} accepted your booking request. ',
     '{artist} declined your booking request. ', 
     '{artist} cancelled your appointment. ', 
     '{user} cancelled an appointment. ', 
     'We just transferred $ {amount} to your bank account. ', 
     '{user} started following you. ', 
     '{user} added a listing of yours in whishlist. ', 
     '{user} reviewed your listing. ', 
     '{user} commented on your listing. ', 
     '{artist} uploaded new listing ',
    ]

NOTIFICATIONS_LONG = [
     '<a href="/users/profile/{user_id}">{user}</a> sent you a booking request for <a href="/listings/{metadata}">{listing}</a>. Manage your booking requests from <a href="/artists/bookings">here</a> ',
     '<a href="/artists/profile/{user_id}">{artist}</a> accepted your booking request for <a href="/listings/{metadata}">{listing}</a>. View all your appointments <a href="/users/bookings">here</a>. ',
     '<a href="/artists/profile/{user_id}">{artist}</a> declined your booking request for <a href="/listings/{metadata}">{listing}</a>. Click <a href="/listings/{metadata}">here</a> to schedule appointment for a different hour. ',
     'Bad news! <a href="/artists/profile/{user_id}">{artist}</a> cancelled your appointment for <a href="/listings/{metadata}">{listing}</a>. Your money will be refunded in 24 hours. As a little compensation from our side, your next booking will be with 5% discount from the regular price.',
     'We are sorry to bring bad news! <a href="/users/profile/{user_id}">{user}</a> cancelled the appointment for <a href="/listings/{metadata}">{listing}</a>.  As a compensation, in 24 hours you will receive 50% of the price of the booking. ',
     'Hey, <a href="/artists/profile/{user_id}">{artist}</a>! Good news! We just transferred $ {amount} to your bank account. View your wallet here. ',
     '<a href="{link_1}">{user}</a> started following you. View all your followers <a href="">here</a>. ',
     '<a href="/users/profile/{user_id}">{user}</a> added a listing of yours in whishlist – <a href="/listings/{metadata}">{listing}</a>. ',
     '<a href="/users/profile/{user_id}">{user}</a> reviewed your listing – <a href="/listings/{metadata}">{listing}</a>. ',
     '<a href="/users/profile/{user_id}">{user}</a> commented on your listing – <a href="/listings/{metadata}">{listing}</a>. Click here to read the comment. ',
     '<a href="/artists/profile/{user_id}">{artist}</a> uploaded new listing – <a href="/listings/{metadata}">{listing}</a>. Click <a href="/listings/{metadata}">here</a> to check the listing. ',
    ]

SUBJECTS = [
    'Welcome to Partytask!',
    'Forgotten Password!',
    'Hey. {username}, we miss you!',
    'Hey. {username}, we miss you even more!',
    'Don’t forget us!',
    '{username} started following you!',
    '{username} started following {artistname}!',
    'Booking request for {title}',
    '{username} started following you!',
    'Your booking request has been approved!',
    'Your booking request has been declined!',
    'Appointment for {when} has been cancelled!',
    'We hope your appointment went well ',
    '{username} posted a review of {title}',
    '{amaunt} was transferred to your bank account ',
    ]

SENDER = 'team@partytask.com'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# Min Withdraw
MIN_WITHDRAW = 30

SECRET_KEY = '@0enryuhp0r0_b-5i&u4&huer-k%)j+jo4!8-0j#j_k$wozhs+'

# Email
# social@partytask.com
# pass: party123
FACEBOOK_APP_ID = '1438154329789867'
FACEBOOK_API_SECRET = '13ba155bd9648587d821987988a08ea8'

# Mandrill information
# Email: team@partytask.com
# Password: party123123
MANDRILL_API_KEY = "fXoeJhGmhEE6BAml5A89RQ"

# PAYPAL ID
# Email: paypal@itworks.bg
# Password: ivoivo123
PAYPAL_API_KEY = "6S8D3DVM79PFN"
PAYPAL_MODE = 'sandbox'
PAYPAL_CLIENT_ID = 'ARjVfRCqo0Al3sVe1Xp3J4DbGK252clnY-b-MAF6nXIqVQEEx2ET1PZLD9yk'
PAYPAL_CLIENT_SECRET = 'ELtWPRA2esNpnQyfdC9wblyRFMMj7pByyQ034-dQlgDj0sEpMT0d5QNBvGA2'

# Payment methods
PAYMENTS_METHOD = ['Bank Transfer', 'PayPal']

# Withdraw status
WITHDRAW_STATUS = ((0, 'Pending',), (1, 'Accepted',),(2, 'Rejected',), (3, 'Warning',))


ALLOWED_HOSTS = ['partytask.com', 'm.partytask.com', 'www.partytask.com', 'localhost', '127.0.0.1', '172.25.0.150']

PROJECT_ROOT = abspath(dirname(dirname(__file__)))

TEMPLATE_URL = join(PROJECT_ROOT, 'templates/')

DESKTOP_TEMPLATE_DIRS = (
    PROJECT_ROOT + '/templates',
)

MOBILE_TEMPLATE_DIRS = (
    PROJECT_ROOT + '/mobile_templates',
) + DESKTOP_TEMPLATE_DIRS

TEMPLATE_DIRS = DESKTOP_TEMPLATE_DIRS


CRON_CLASSES = [
    "glamazer.core.cron.SendFeedbackForm",
]

# Application definition
INSTALLED_APPS = (
    'suit',
    'django_cron',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'sorl.thumbnail',
    'glamazer.core',
    'glamazer.users',
    'glamazer.artists',
    'glamazer.listings',
    'glamazer.followers',
    'glamazer.favorites',
    'glamazer.booking',
    'glamazer.notifications',
    'glamazer.payments',
    'glamazer.reviews',
    'django_extensions',
    'south',
    'haystack',
    # 'announce',
    # 'sslserver',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'glamazer.core.middleware.MobileMiddleware'
)

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    INSTALLED_APPS += ('debug_toolbar',)

    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

else:
    DATABASES = {
        'default': {
            'NAME': 'partytask',
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': '172.25.0.150',
            'PORT': '5432',
            'USER': 'partytask',
            'PASSWORD': 'party123',
        }
    }
    
    INSTALLED_APPS += ('raven.contrib.django.raven_compat',)
    # GetSentry configuration
    # Email: zhuhov@gmail.com
    # Pass: 9210224526
    RAVEN_CONFIG = {
        'dsn': 'https://5d2393c5d8094c1992724d65b57a7603:d091603bd0b044c6ba197e63255adc74@app.getsentry.com/27091',
    }


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}

ELASTIC_SEARCH_URL = 'http://127.0.0.1:9200/'
MEDIA_URL = '/media/'


HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

AUTHENTICATION_BACKENDS = (
    'backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'glamazer.urls'

WSGI_APPLICATION = 'glamazer.wsgi.application'

CONN_MAX_AGE = 60


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


STATIC_ROOT = os.path.abspath(PROJECT_ROOT+'/static_server')
STATIC_URL = '/static/'


MEDIA_ROOT = join(PROJECT_ROOT, 'media/')


STATICFILES_DIRS = ( join(PROJECT_ROOT,'static/'), )

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

EMAIL_CASES = {
    0: 'User welcome message',
    1: 'Artist welcome message',
    3: 'Facebook welcome message',
    4: 'Forgotten password message',
    5: 'If not logged in after 3 days',
    6: 'If not logged in after 7 days',
    7: 'If not logged in after 14 days',
    8: 'Email to artist, in case of new follower',
    10: 'Email artist when he have new booking request',
    12: 'Email to the user, if the booking is approved',
    13: 'If booking request is rejected by artist',
    14: 'If booking request is declined by user, no charge',
    15: 'If booking request is declined by user, with charge',
    16: 'If booking request is cancelled by the artist, after was approved',
    17: 'User welcome message',
    18: 'User welcome message',
}


SUIT_CONFIG = {
    'ADMIN_NAME': 'Partytask',
    # 'HEADER_DATE_FORMAT': 'l, j. F Y',
    # 'HEADER_TIME_FORMAT': 'H:i',

    # menu
    # 'SEARCH_URL': '/admin/auth/user/',
    # 'MENU_ICONS': {
    #    'sites': 'icon-leaf',
    #    'auth': 'icon-lock',
    # },
    # 'MENU_OPEN_FIRST_CHILD': True, # Default True
    # 'MENU_EXCLUDE': ('auth.group',),
    # 'MENU': (
    #     'sites',
    #     {'app': 'auth', 'icon':'icon-lock', 'models': ('user', 'group')},
    #     {'label': 'Settings', 'icon':'icon-cog', 'models': ('auth.user', 'auth.group')},
    #     {'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},
    # ),

    # misc
    # 'LIST_PER_PAGE': 15
}

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'