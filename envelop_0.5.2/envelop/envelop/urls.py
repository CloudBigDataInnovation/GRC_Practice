"""envelop URL Configuration

"""
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from audits.views import index, LoginView

admin.site.site_header = 'Envelop administration'
admin.AdminSite.site_title = 'Envelop'

urlpatterns = [
    url(r'^repository/', TemplateView.as_view(template_name="not_implemented.html")),
    url(r'^not_implemented/', TemplateView.as_view(template_name="not_implemented.html")),
    url(r'^audits/', include(('audits.urls', 'audits'), namespace="audits")),
    url(r'^admin/', admin.site.urls),
    url(r'^$', login_required(index), name='index'),
    url(r'^login/$', LoginView.as_view(), name='envelope_login'),
#    url(r'^files/', include('db_file_storage.urls')),
    url(r'^planning/', include(('planning.urls', 'planning'), namespace='planning')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
