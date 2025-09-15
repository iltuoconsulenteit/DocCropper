from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from platform.apps.portal import views as portal_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('platform.apps.portal.urls')),
    re_path(r'^wiki(?:/(?P<path>.*))?$', portal_views.wiki, name='wiki'),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

