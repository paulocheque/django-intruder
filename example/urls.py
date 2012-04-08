from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^view-a', 'example.views.view_a', name='view_a'),
    url(r'^view-b', 'example.views.view_b', name='view_b'),
)
