from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('calendar/', views.calendar_month, name='calendar'),
    path('calendar/day/', views.calendar_day, name='day'),
    path('friends/', views.friends_view, name='friends'),
    path('testing/', views.testing, name='testing')
]
