from django.urls import path
from .views import analyze_skill_gap

urlpatterns = [
    path('analyze/', analyze_skill_gap, name='skillgap-analyze'),
]
