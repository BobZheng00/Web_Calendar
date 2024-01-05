from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('calendar/', views.calendar_month, name='calendar'),
    path('calendar/day/', views.calendar_day, name='day'),
    path('calendar/week/', views.calendar_week, name='week'),
    path('friends/', views.friends_view, name='friends'),
    path('testing/', views.testing, name='testing'),
    path('<str:username>/calendar/', views.friend_calendar, name='calendar'),
    path('<str:username>/calendar/week/', views.friend_calendar_week, name='calendar_week'),
    path('<str:username>/calendar/day/', views.friend_calendar_day, name='calendar_day'),
]
