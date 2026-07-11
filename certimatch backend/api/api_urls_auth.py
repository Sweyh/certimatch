from django.urls import path
from .views import signup, login, logout, me

urlpatterns = [
    path('signup/',  signup, name='signup'),
    path('login/',   login,  name='login'),
    path('logout/',  logout, name='logout'),
    path('me/',      me,     name='me'),
]
