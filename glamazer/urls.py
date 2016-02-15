from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'glamazer.core.views.home', name='home'),
    url(r'^venues/', 'glamazer.core.views.base', name='venues'),
    url(r'^catering/', 'glamazer.core.views.base', name='catering'),
    url(r'^drinks/', 'glamazer.core.views.base', name='drinks'),
    url(r'^music/', 'glamazer.core.views.base', name='music'),
    url(r'^entertainment/', 'glamazer.core.views.base', name='entertainment'),
    url(r'^equipment/', 'glamazer.core.views.base', name='equipment'),
    url(r'^decoration/', 'glamazer.core.views.base', name='decoration'),
    url(r'^party_goods/', 'glamazer.core.views.base', name='party'),
    url(r'^more/', 'glamazer.core.views.base', name='more'),
    url(r'^contest/', 'glamazer.core.views.base', name='contest'),
    url(r'^leaderboards/', 'glamazer.core.views.base', name='leaderboards'),
    url(r'^result/', 'glamazer.core.views.search', name='result'),
    url(r'^get_notifications/', 'glamazer.notifications.views.get_notifications', name='short_notifications'),
    url(r'^get_notifications_count/', 'glamazer.notifications.views.get_notification_count', name='notification_count'),
    url(r'^autocomplete_tags/', 'glamazer.core.views.autocomplete_tags', name='autocomplete_tags'),
    url(r'^sign_up/', TemplateView.as_view(template_name="sign_up.html"), name='signup'),
    url(r'^calendar/', TemplateView.as_view(template_name="core/calendar.html"), name='calender'),
    url(r'^success/', TemplateView.as_view(template_name="payments/success.html"), name='calender'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include('glamazer.users.urls')),
    url(r'^artists/', include('glamazer.artists.urls')),
    url(r'^listings/', include('glamazer.listings.urls')),
    url(r'^favorites/', include('glamazer.favorites.urls')),
    url(r'^reviews/', include('glamazer.reviews.urls')),
    url(r'^success/', 'glamazer.payments.views.success_payment', name='success'),
    url(r'^error/', 'glamazer.payments.views.error_payment', name='error'),
    url(r'^cancel/', 'glamazer.payments.views.cancel_payment', name='cancel'),
    url(r'^start_payment/', 'glamazer.payments.views.start_payment', name='payment'),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
