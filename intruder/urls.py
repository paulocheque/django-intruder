from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
     url(r'^feature-under-maintenance', 'intruder.views.feature_under_maintenance', name='feature_under_maintenance'),
     url(r'^feature-is-no-longer-available', 'intruder.views.feature_is_no_longer_available', name='feature_is_no_longer_available'),
)
