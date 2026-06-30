from datetime import timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Max
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, FormView, TemplateView

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
        # 1. Берем группы текущего учителя
        # 2. Через .annotate(students_count=...) сразу считаем количество студентов в каждой карточке
        return Group.objects.filter(
            module_teachers__teacher=self.request.user,
            active=True
        ).annotate(
            students_count=Count('student_groups')
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user

        teaching_groups = context['groups']

        for group in teaching_groups:
            last_lesson = Lesson.objects.filter(group=group).order_by('-number').first()
            group.last_lesson_number = last_lesson.number if last_lesson else 0

        context['groups_count'] = teaching_groups.count()

        context['total_students_count'] = User.objects.filter(
            role=User.Role.STUDENT,
            student_groups__group__in=teaching_groups
        ).distinct().count()

        selected_group_id = self.request.GET.get('group_id')
        if selected_group_id:
            current_group = get_object_or_404(Group, id=selected_group_id, module_teachers__teacher=teacher)
        else:
            current_group = teaching_groups.first()

        context['current_group'] = current_group

        if current_group:
            context['students_in_group'] = User.objects.filter(
                role=User.Role.STUDENT,
                student_groups__group=current_group
            )
        else:
            context['students_in_group'] = []

        return context


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/student_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Текущая активная группа студента
        current_group = Group.objects.filter(student_groups__student=user, active=True).distinct().first()

        # Базовые дефолтные значения (на случай, если у студента нет группы)
        context.update({
            'current_group': current_group,
            'lessons': [],
            'lc_prct': 0,
            'grades': [],
            'lessons_completed': 0,
            'current_group_students_count': 0,
            'lessons_total': 12,
            'avg_score': 0,
            'attendance_pct': 0,
            'hw_done_pct': 0,
            'last_hw_score': None,
            'last_cw_score': None,
            'rank': None,
        })

        if current_group:
            # 1. Посещенные / Пройденные уроки
            lessons_completed = Lesson.objects.filter(
                group=current_group,
                date__lte=timezone.now().date(),
                cancelled=False
            ).count()

            # 2. Логика расчетов оценок и точного СРЕДНЕГО ПРОЦЕНТА (avg_score)
            grades_qs = Grade.objects.filter(student=user, lesson__group=current_group).order_by('-lesson__number')

            avg_percent = 0
            last_hw_score = None
            last_cw_score = None

            if grades_qs.exists():
                total_percentages = 0
                graded_lessons_count = 0

                for grade in grades_qs:
                    # Ищем максимумы конкретно для этого урока в группе
                    lesson_max = Grade.objects.filter(lesson=grade.lesson).aggregate(
                        max_hw=Max('homework_points'),
                        max_cw=Max('classwork_points')
                    )
                    max_hw = lesson_max['max_hw'] or 0
                    max_cw = lesson_max['max_cw'] or 0
                    total_lesson_max = max_hw + max_cw

                    child_total_lesson = grade.homework_points + grade.classwork_points

                    if total_lesson_max > 0:
                        lesson_percent = (child_total_lesson / total_lesson_max) * 100
                        total_percentages += lesson_percent
                        graded_lessons_count += 1

                if graded_lessons_count > 0:
                    avg_percent = int(total_percentages / graded_lessons_count)

                # Последние оценки для быстрых карточек
                last_grade = grades_qs.first()  # Так как отсортировано по -lesson__number, это самый свежий урок
                last_hw_score = last_grade.homework_points
                last_cw_score = last_grade.classwork_points

            # 3. Количество студентов и процент выполнения курса
            current_group_students_count = current_group.student_groups.count()
            total_lessons = 12
            lc_prct = 8.3334 * lessons_completed


            # --- КОРРЕКТНЫЙ ИНДИВИДУАЛЬНЫЙ РАСЧЕТ ПОРОГОВ ДЛЯ КАЖДОГО УРОКА ---
            for grade in grades_qs:
                # Находим максимальные баллы строго для ЭТОГО конкретного урока в группе
                lesson_max = Grade.objects.filter(lesson=grade.lesson).aggregate(
                    max_hw=Max('homework_points'),
                    max_cw=Max('classwork_points')
                )

                # Защита от None: если оценок на этом уроке ещё нет, ставим дефолт 20
                max_hw_possible = lesson_max['max_hw'] or 20
                max_cw_possible = lesson_max['max_cw'] or 20

                # Вычисляем шаги интервалов именно для этого урока
                hw_step = max_hw_possible / 3
                cw_step = max_cw_possible / 3

                # Динамически выставляем класс для Домашней работы на этом уроке
                if grade.homework_points >= (hw_step * 2):
                    grade.hw_class = "high"
                elif grade.homework_points >= hw_step:
                    grade.hw_class = "mid"
                else:
                    grade.hw_class = "low"

                # Динамически выставляем класс для Классной работы на этом уроке
                if grade.classwork_points >= (cw_step * 2):
                    grade.cw_class = "high"
                elif grade.classwork_points >= cw_step:
                    grade.cw_class = "mid"
                else:
                    grade.cw_class = "low"


            # 5. Процент посещаемости
            attendance_pct = 0
            if total_lessons:
                present = Attendance.objects.filter(student=user, lesson__group=current_group, status='present').count()
                attendance_pct = int((present / total_lessons) * 100)

            # 6. Процент выполнения домашних заданий (сдано больше 0 баллов)
            total_grades_count = grades_qs.count()
            submitted_hw_count = grades_qs.filter(homework_points__gt=0).count()
            hw_done_pct = int((submitted_hw_count / total_grades_count) * 100) if total_grades_count > 0 else 0

            # 7. Список уроков с отметкой посещаемости для таблицы
            lessons = Lesson.objects.filter(group=current_group).order_by('number')
            for lesson in lessons:
                lesson.my_attendance = lesson.attendance.filter(student=user).first()

            group_student_ids = current_group.student_groups.values_list('student_id', flat=True)

            # Считаем сумму баллов для каждого студента этой группы за всё время
            leaderboard = User.objects.filter(id__in=group_student_ids).annotate(
                total_score=Sum('grade__homework_points') + Sum('grade__classwork_points')
            ).order_by('-total_score') # Сортируем: у кого больше баллов, тот первый

            # Ищем, на каком месте в этом списке находится текущий студент
            rank = 1
            for index, student_in_top in enumerate(leaderboard):
                if student_in_top.id == user.id:
                    rank = index + 1
                    break

            # Дополнительно считаем процент места в топе (например, "Топ 15%"), как было на макете
            total_students_in_group = len(group_student_ids)
            if total_students_in_group > 0:
                top_percent = int((rank / total_students_in_group) * 100)
            else:
                top_percent = 100

            # Обновляем контекст просчитанными данными
            context.update({
                'lessons': lessons,
                'lc_pct': lc_prct,
                'grades': grades_qs,
                'lessons_completed': lessons_completed,
                'current_group_students_count': current_group_students_count,
                'avg_score': avg_percent,
                'attendance_pct': attendance_pct,
                'hw_done_pct': hw_done_pct,
                'last_hw_score': last_hw_score,
                'last_cw_score': last_cw_score,
                'rank': rank,
                'top_percent': top_percent,
            })

        return context


class ParentDashboardListView(LoginRequiredMixin, ListView):
    model = ParentStudent
    template_name = 'dashboards/parent_dashboard.html'
    context_object_name = 'children_connections'

    def get_queryset(self):
        # Получаем все связи текущего родителя с детьми
        return ParentStudent.objects.filter(parent=self.request.user).select_related('student')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent = self.request.user

        # 1. Формируем список детей для сайдбара (как у Copilot)
        connections = context['children_connections']
        children = [ps.student for ps in connections]
        context['children'] = children

        # 2. Определяем выбранного ребенка (через GET или берем первого)
        selected_student_id = self.request.GET.get('student_id')
        if selected_student_id:
            child = get_object_or_404(User, id=selected_student_id, parents__parent=parent)
        else:
            child = children[0] if children else None

        context['child'] = child


        if child:
            # Находим текущую группу ребенка через промежуточную таблицу GroupStudent
            child_group = Group.objects.filter(student_groups__student=child).first()

            # --- СТАТИСТИКА 1: ПРОИЗВОДИТЕЛЬНОСТЬ (Perfomance) ---
            MAX_POINTS_PER_LESSON = 40
            grades_summary = Grade.objects.filter(student=child).aggregate(
                total_hw=Sum('homework_points'),
                total_cw=Sum('classwork_points'),
                lessons_count=Count('id')
            )
            total_earned = (grades_summary['total_hw'] or 0) + (grades_summary['total_cw'] or 0)
            total_possible = (grades_summary['lessons_count'] or 0) * MAX_POINTS_PER_LESSON
            context['performance'] = int((total_earned / total_possible) * 100) if total_possible > 0 else 0

            # --- СТАТИСТИКА 2: ПОСЕЩАЕМОСТЬ В ПРОЦЕНТАХ ---
            total_lessons = Attendance.objects.filter(student=child).count()
            present_lessons = Attendance.objects.filter(student=child, status='PRESENT').count()
            context['attendance'] = int((present_lessons / total_lessons) * 100) if total_lessons > 0 else 0

            # Посещаемость за текущий месяц для счетчиков Copilot (переменные lessons и la)
            month_start = timezone.now().date().replace(day=1)
            presents = Attendance.objects.filter(student=child, lesson__date__gte=month_start,
                                                 status=Attendance.Status.PRESENT).count()
            absents = Attendance.objects.filter(student=child, lesson__date__gte=month_start,
                                                status=Attendance.Status.ABSENT).count()

            # --- СТАТИСТИКА 3: ДОМАШНЕЕ ЗАДАНИЕ (Homework) ---
            total_grades = Grade.objects.filter(student=child).count()
            submitted_hw = Grade.objects.filter(student=child, homework_points__gt=0).count()
            context['homework'] = int((submitted_hw / total_grades) * 100) if total_grades > 0 else 0
            context['submitted'] = submitted_hw
            context['missing'] = Grade.objects.filter(student=child, homework_points=0).count()

            # --- ДАННЫЕ ПРЕПОДАВАТЕЛЯ И КУРСА ---
            teacher_obj = GroupModuleTeacher.objects.filter(group=child_group).select_related(
                'teacher').first() if child_group else None
            child_teacher_name = f"{teacher_obj.teacher.first_name} {teacher_obj.teacher.last_name}" if teacher_obj else ''
            child_tech = child_group.technology if child_group else ''
            child_module_number = child_group.current_module.number if child_group and child_group.current_module else ''

            # --- ТАБЛИЦЫ (Уроки, Оценки, Платежи) ---
            if child_group:
                context['gcurrent_lesson'] = Lesson.objects.filter(group=child_group,
                                                                   date=timezone.now().date()).first()
                context['glessons'] = Lesson.objects.filter(group=child_group)
            else:
                context['gcurrent_lesson'] = None
                context['glessons'] = Lesson.objects.none()

            context['grades'] = Grade.objects.filter(student=child).order_by('-created_at')
            context['payments'] = Payment.objects.filter(student=child)

            # Собираем итоговый словарь контекста от Copilot
            context.update({
                'lessons': presents,  # Отрендерится в «0 из 12 посещенных уроков»
                'la': absents,  # Количество пропусков под кругом
                'group': child_group.title if child_group else '',
                'child_teacher_name': child_teacher_name,
                'child_tech': child_tech,
                'children': children,
                'child_module_number': child_module_number,
            })
        else:
            # Заглушки на случай, если у родителя в базе данных вообще нет детей
            context.update({
                'perfomance': 0, 'attendance': 0, 'homework': 0,
                'n1': '', 'n1_pr': 0, 'n2': '', 'n2_pr': 0, 'n3': '', 'n3_pr': 0,
                'lessons': 0, 'la': 0, 'group': '', 'yn': None, 'child_score': 0,
                'child_teacher_name': '', 'child_tech': '', 'child_module_number': '',
                'gcurrent_lesson': None, 'glessons': Lesson.objects.none(),
                'grades': Grade.objects.none(), 'payments': Payment.objects.none()
            })

        return context


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


def add_group_view(request):
    # Если пользователь нажал на кнопку создания (POST-запрос)
    if request.method == 'POST':
        technology = request.POST.get('technology')
        teacher_id = request.POST.get('teacher')

        # 1. Генерируем красивый тайтл (P1, P2, J1...)
        first_letter = technology.upper()[0:1]
        count = Group.objects.filter(technology=technology).count() + 1
        generated_title = f"{first_letter}{count}"

        # 2. Автоматически находим Модуль №1 в базе
        first_module = Module.objects.filter(number=1).first()

        # 3. Создаем саму группу в базе данных
        new_group = Group.objects.create(
            title=generated_title,
            technology=technology,
            current_module=first_module
        )

        # 4. Если учитель выбран и первый модуль существует — связываем их через промежуточную таблицу
        if teacher_id and first_module:
            teacher_user = User.objects.filter(id=teacher_id).first()
            if teacher_user:
                GroupModuleTeacher.objects.create(
                    group=new_group,
                    module=first_module,
                    teacher=teacher_user
                )

        # 5. После успешного создания перенаправляем на админку
        return redirect('admin_dashboard')


def add_user_view(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    phone = request.POST.get('phone')
    role = request.POST.get('role')
    username = request.POST.get('username')
    password = request.POST.get('password')
    group_id = request.POST.get('group')

    # 1. Создаем пользователя (используем модель User)
    new_user = User.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role=role
    )

    # 2. Хэшируем и сохраняем пароль, чтобы пользователь мог авторизоваться
    new_user.set_password(password)
    new_user.save()

    # 3. Если роль — студент и была выбрана группа, связываем их через промежуточную таблицу
    if role == 'STUDENT' and group_id:
        group_obj = Group.objects.filter(id=group_id).first()
        if group_obj:
            GroupStudent.objects.create(
                student=new_user,
                group=group_obj
            )

    # 4. Возвращаем админа обратно на дашборд
    return redirect('admin_dashboard')


def settings_view(request):
    return render(request, 'pages/settings.html')


def materials_view(request):
    return render(request, 'pages/materials.html')


def leaderboard_view(request):
    return render(request, 'pages/leaderboard.html')
