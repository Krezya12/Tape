from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('admin', admin_dashboard_view, name='admin_dashboard'),
    path('teacher', teacher_dashboard_view, name='teacher_dashboard'),
    path('parent', parent_dashboard_view, name='parent_dashboard'),
    path('student', student_dashboard_view, name='student_dashboard'),
]
