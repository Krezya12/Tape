from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('admin', admin_dashboard_view, name='admin_dashboard'),
    path('teacher', teacher_dashboard_view, name='teacher_dashboard'),
    path('parent', parent_dashboard_view, name='parent_dashboard'),
    path('student', student_dashboard_view, name='student_dashboard'),
    path('settings', student_dashboard_view, name='settings'),
    path('profile', student_dashboard_view, name='profile'),
    path('logout', student_dashboard_view, name='logout'),
    path('', index_view, name='index'),
    path('login', login_view, name='login'),
    path('admin/notifications', notifications_view, name='notifications'),
    path('teacher/notifications', notifications_view, name='notifications'),
    path('parent/notifications', notifications_view, name='notifications'),
    path('student/notifications', notifications_view, name='notifications'),
]
