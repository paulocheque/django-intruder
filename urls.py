from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     url(r'^admin/', include(admin.site.urls)),

     (r'^intruder/', include('intruder.urls', namespace='intruder', app_name='intruder')),

     (r'^example/', include('example.urls', namespace='example', app_name='example')),
)
