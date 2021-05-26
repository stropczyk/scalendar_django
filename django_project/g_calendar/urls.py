from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('calendar/', views.calendar, name='calendar'),
    path('new-event/', views.event, name='event'),
    path('github-authorized/', views.github_authorized, name='github'),
    path('login/<event_date>&<event_time>/', views.login, name='login'),
    path('login-with-github/', views.login_with_github, name='login_gh'),
    path('login-with-google/', views.login_with_google, name='login_google'),
]
