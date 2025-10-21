from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView
from platform.apps.portal import views as portal_views

sign_redirects = [
    re_path(r'^sign/(?P<token>[^/]+)$',
            RedirectView.as_view(url='/api/sign/%(token)s', permanent=False)),
    re_path(r'^sign/?$', RedirectView.as_view(url='/api/sign', permanent=False)),
    re_path(r'^start-sign/?$',
            RedirectView.as_view(url='/api/start-sign/', permanent=False)),
    re_path(r'^sign-pages/(?P<token>[^/]+)$',
            RedirectView.as_view(url='/api/sign-pages/%(token)s', permanent=False)),
    re_path(r'^submit-signature/(?P<token>[^/]+)$',
            RedirectView.as_view(url='/api/submit-signature/%(token)s', permanent=False)),
    re_path(r'^finish-signing/(?P<token>[^/]+)$',
            RedirectView.as_view(url='/api/finish-signing/%(token)s', permanent=False)),
    re_path(r'^signature-result/(?P<token>[^/]+)$',
            RedirectView.as_view(url='/api/signature-result/%(token)s', permanent=False)),
    re_path(r'^store-signed-pdf/(?P<token>[^/]+)$',
            RedirectView.as_view(url='/api/store-signed-pdf/%(token)s', permanent=False)),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('platform.apps.portal.urls')),
    re_path(r'^wiki(?:/(?P<path>.*))?$', portal_views.wiki, name='wiki'),
] + sign_redirects

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

