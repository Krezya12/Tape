from django.urls import path
from .views import *

urlpatterns = [
    path('teacher/journal/<int:group_id>/', teacher_journal_view, name='teacher_journal'),
    path('my-profile/', student_dashboard_view, name='student_dashboard'),

]
