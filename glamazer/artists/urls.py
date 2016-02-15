from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^change_password/(?P<email_token>.*)', 'glamazer.users.views.change_password', name='change_password'),
    url(r'^forgotten_password/', 'glamazer.users.views.forgotten_password', name='forgotten_password'),
    url(r'^sign_up/$', 'glamazer.artists.views.sign_up', name='artists_sign_up'),
    url(r'^sign_up/facebook$', 'glamazer.artists.views.facebook_registration', name='artists_sign_up_facebook'),
    url(r'^profile/$', 'glamazer.artists.views.profile', name='artists_profile'),
    url(r'^profile/(?P<artist_id>.*)', 'glamazer.artists.views.profile', name='artists_profile_user'),
    url(r'^settings/profile$', 'glamazer.artists.views.edit', name='edit_artist_profile'),
    url(r'^settings/account$', 'glamazer.artists.views.account', name='edit_artist_account'),
    url(r'^settings/schedule$', 'glamazer.artists.views.schedule', name='artist_schedule'),
    url(r'^settings/policy$', 'glamazer.artists.views.cancellation_policy', name='artist_cancellation_policy'),
    url(r'^settings/payments$', 'glamazer.artists.views.payments', name='artist_payments'),
    url(r'^upload/$', 'glamazer.artists.views.upload', name='upload'),
    url(r'^listings/all/$', 'glamazer.artists.views.all_listings', name='all_listing'),
    url(r'^bookings/$', 'glamazer.artists.views.bookings', name='artists_bookings'),
    url(r'^calendar/$', 'glamazer.artists.views.calendar', name='artists_calendar'),
    url(r'^statistic/$', TemplateView.as_view(template_name="artists/stats.html"), name='artists_statistic'),
    url(r'^wallet/$', 'glamazer.artists.views.wallet', name='artists_wallet'),
    url(r'^withdraw/$', 'glamazer.artists.views.withdraw', name='artists_withdraw'),
    url(r'^notifications/$', 'glamazer.notifications.views.show_notifications', name='artist_notifications'),
    url(r'^get_chart_info/$', 'glamazer.artists.views.get_chart_info', name='get_chart_info'),
)