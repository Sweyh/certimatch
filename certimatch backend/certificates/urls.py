from django.urls import path
from .views import CertificateListCreateView, CertificateDetailView, AllSkillsView

urlpatterns = [
    path('',          CertificateListCreateView.as_view(), name='cert-list'),
    path('<int:pk>/', CertificateDetailView.as_view(),     name='cert-detail'),
    path('skills/',   AllSkillsView.as_view(),             name='all-skills'),
]
