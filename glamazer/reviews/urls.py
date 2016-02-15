from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<email_token>.*)$', 'glamazer.reviews.views.receive_review', name='receive_review'),
)