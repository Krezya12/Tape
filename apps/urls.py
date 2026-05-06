from django.urls import path
from .views import *

urlpatterns = [
    path('teacher/', teacher_dashboard, name='teacher'),
    path('admin-panel/', admin_dashboard, name='admin'),
    path('student/', student_dashboard, name='student'),
    path('parent/', parent_dashboard, name='parent'),
    path('save-record/', save_record, name='save'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
]