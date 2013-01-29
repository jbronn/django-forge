from django.conf import settings
from django.conf.urls import patterns, include
from django.conf.urls import url
from django.contrib import admin

from . import views


admin.autodiscover()

handler404 = 'forge.views.handler404'
handler500 = 'forge.views.handler500'

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^modules\.json$', views.modules_json, name='modules_json'),
    url(r'^api/v1/releases\.json$', views.releases_json, name='releases_json'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
            'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
