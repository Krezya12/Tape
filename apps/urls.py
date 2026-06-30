from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    # path('test', test_view, name='test'),

    path('admin', AdminListView.as_view(), name='admin_dashboard'),
    path('admin/add-group', add_group_view, name='add-group'),
    path('admin/add-user', add_user_view, name='add-user'),
    path('teacher', TeacherDashboardListView.as_view(), name='teacher_dashboard'),
    path('parent', ParentDashboardListView.as_view(), name='parent_dashboard'),
    path('student', StudentDashboardView.as_view(), name='student_dashboard'),
    path('admin/settings', settings_view, name='settings'),
    path('teacher/settings', settings_view, name='settings'),
    path('teacher/materials', materials_view, name='materials'),
    path('parent/settings', settings_view, name='settings'),
    path('student/settings', settings_view, name='settings'),
    path('profile', profile_view, name='profile'),
    path('logout', logout_view, name='logout'),
    path('', index_view, name='index'),
    path('login', login_view, name='login'),
    path('admin/notifications', notifications_view, name='notifications'),
    path('teacher/notifications', notifications_view, name='notifications'),
    path('teacher/profile', profile_view, name='profile'),
    path('parent/notifications', notifications_view, name='notifications'),
    path('student/notifications', notifications_view, name='notifications'),
    path('student/leaderboard', leaderboard_view, name='leaderboard'),
    path('teacher/leaderboard', leaderboard_view, name='leaderboard'),
    path('parent/leaderboard', leaderboard_view, name='leaderboard'),
    path('admin/leaderboard', leaderboard_view, name='leaderboard'),

]
