from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from . import views
from .views import v1

admin.autodiscover()

handler404 = 'forge.views.handler404'
handler500 = 'forge.views.handler500'

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^modules\.json$',
        v1.modules_json, name='modules_json_v1'),
    url(r'^api/v1/releases\.json$',
        v1.releases_json, name='releases_json_v1'),
    url(r'^(?P<author>\w+)/(?P<module_name>\w+)\.json$',
        v1.module_json, name='module_json_v1'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
            'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
