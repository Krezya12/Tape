from django.shortcuts import render


def admin_dashboard_view(request):
    return render(request, 'dashboards/admin_dashboard.html')

def student_dashboard_view(request):
    return render(request, 'dashboards/student_dashboard.html')

def teacher_dashboard_view(request):
    return render(request, 'dashboards/teacher_dashboard.html')

def parent_dashboard_view(request):
    return render(request, 'dashboards/parent_dashboard.html')