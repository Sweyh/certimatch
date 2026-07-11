from django.urls import path
from .views import list_jobs, recommended_jobs, apply_job, my_applications

urlpatterns = [
    path('',                list_jobs,          name='job-list'),
    path('recommendations/',recommended_jobs,   name='job-recommendations'),
    path('<int:pk>/apply/', apply_job,          name='job-apply'),
    path('applications/',   my_applications,    name='my-applications'),
]
