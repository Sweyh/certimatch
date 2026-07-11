from django.urls import path
from .views import (
    JobListView, MLMatchView, SkillGapView,
    SalaryPredictView, ApplyJobView, MyApplicationsView
)

urlpatterns = [
    path('',                JobListView.as_view(),       name='job-list'),
    path('matches/',        MLMatchView.as_view(),        name='ml-matches'),
    path('skillgap/',       SkillGapView.as_view(),       name='skill-gap'),
    path('salary/',         SalaryPredictView.as_view(),  name='salary-predict'),
    path('<int:pk>/apply/', ApplyJobView.as_view(),       name='apply-job'),
    path('applications/',   MyApplicationsView.as_view(), name='my-applications'),
]
