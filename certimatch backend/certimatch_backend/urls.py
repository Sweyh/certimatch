from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/',     admin.site.urls),
    path('api/',       include('api.urls')),
    path('',           TemplateView.as_view(template_name='index.html'),    name='home'),
    path('login/',     TemplateView.as_view(template_name='login.html'),    name='login'),
    path('signup/',    TemplateView.as_view(template_name='signup.html'),   name='signup'),
    path('admin-users/', TemplateView.as_view(template_name='admin-users.html'), name='admin-users'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'),name='dashboard'),
    path('upload/',    TemplateView.as_view(template_name='upload.html'),   name='upload'),
    path('jobs/',      TemplateView.as_view(template_name='jobs.html'),     name='jobs'),
    path('salary/',    TemplateView.as_view(template_name='salary.html'),   name='salary'),
    path('skillgap/',  TemplateView.as_view(template_name='skillgap.html'), name='skillgap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.BASE_DIR.parent / 'frontend')
