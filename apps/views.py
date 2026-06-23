from django.contrib.auth import logout
from django.shortcuts import render


def admin_dashboard_view(request):
    return render(request, 'dashboards/admin_dashboard.html')

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
    return render(request, 'login.html')

def notifications_view(request):
    return render(request, 'pages/notifications.html')