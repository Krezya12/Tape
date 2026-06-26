from datetime import timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, FormView

from apps.forms import *
from apps.models import *


def test_view(request):
    return render(request, 'tests.html')


class AdminListView(ListView):
    model = User
    template_name = 'dashboards/admin_dashboard.html'
    context_object_name = 'users'

    def get_queryset(self, **kwargs):
        return User.objects.all().order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        lmd = timezone.now() - timedelta(days=30)

        context['groups'] = Group.objects.all()
        context['teachers'] = User.objects.filter(role='TEACHER')

        context['active_groups'] = Group.objects.filter(active=True).count()
        context['students_count'] = User.objects.filter(role='STUDENT').count()
        context['teachers_count'] = User.objects.filter(role='TEACHER').count()
        context['sim'] = User.objects.filter(role='STUDENT').filter(date_joined__gte=lmd).count()
        context['tim'] = User.objects.filter(role='TEACHER').filter(date_joined__gte=lmd).count()
        context['gim'] = Group.objects.filter(created_at__gte=lmd).count()

        return context


class TeacherDashboardListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'dashboards/teacher_dashboard.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return Group.objects.filter(module_teachers__teacher=self.request.user, active=True).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user

        teacher_groups = self.get_queryset()

        context['groups_count'] = teacher_groups.count()

        context['total_students_count'] = User.objects.filter(
            role=User.Role.STUDENT,
            student_groups__group__in=teacher_groups
        ).distinct().count()

        selected_group_id = self.request.GET.get('group_id')

        if selected_group_id:
            current_group = get_object_or_404(Group, id=selected_group_id, module_teachers__teacher=teacher)
        else:
            current_group = teacher_groups.first()

        context['current_group'] = current_group

        context['current_lesson'] = current_group.get_current_lesson()

        if current_group:
            context['students_in_group'] = User.objects.filter(
                role=User.Role.STUDENT,
                student_groups__group=current_group
            )
        else:
            context['students_in_group'] = []

        return context


def student_dashboard_view(request):
    return render(request, 'dashboards/student_dashboard.html')


def teacher_dashboard_view(request):
    return render(request, 'dashboards/teacher_dashboard.html')


def parent_dashboard_view(request):
    return render(request, 'dashboards/parent_dashboard.html')


def logout_view(request):
    logout(request)
    return render(request, 'login.html')


def index_view(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role == 'ADMIN':
                login(request, user)
                return redirect("admin_dashboard")
            if user.role == 'TEACHER':
                login(request, user)
                return redirect("teacher_dashboard")
            if user.role == 'PARENT':
                login(request, user)
                return redirect("parent_dashboard")
            if user.role == 'STUDENT':
                login(request, user)
                return redirect("student_dashboard")
        else:
            return ValidationError('Invalid username or password.')

    return render(request, 'login.html')


def notifications_view(request):
    return render(request, 'pages/notifications.html')


def profile_view(request):
    return render(request, 'pages/profile.html')


class GroupCreateView(CreateView):
    queryset = Group.objects.all()
    form_class = GroupModelForm
    success_url = reverse_lazy('teacher_dashboard')
    template_name = 'dashboards/admin_dashboard.html'


class UserCreateView(CreateView):
    queryset = User.objects.all()
    form_class = UserModelForm
    success_url = reverse_lazy('admin_dashboard')
    template_name = 'dashboards/admin_dashboard.html'


def settings_view(request):
    return render(request, 'pages/settings.html')

def materials_view(request):
    return render(request, 'pages/materials.html')

def leaderboard_view(request):
    return render(request, 'pages/leaderboard.html')