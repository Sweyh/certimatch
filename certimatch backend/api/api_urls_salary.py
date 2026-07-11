from django.urls import path
from .views import predict_salary_view

urlpatterns = [
    path('predict/', predict_salary_view, name='salary-predict'),
]
