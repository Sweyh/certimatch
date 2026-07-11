from django.urls import path
from .views import upload_certificate, list_certificates, certificate_detail

urlpatterns = [
    path('upload/',   upload_certificate,  name='cert-upload'),
    path('',          list_certificates,   name='cert-list'),
    path('<int:pk>/', certificate_detail,  name='cert-detail'),
]
