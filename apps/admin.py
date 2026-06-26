from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    ParentStudent,
    Module,
    Group,
    Lesson,
    Exam,
    StudentModuleProgress,
    Grade,
    Attendance,
    Payment,
    StudentRating,
    TeacherSettings,
    Notification, GroupModuleTeacher
)


# ==========================
# USER ADMIN
# ==========================


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "phone",
        "is_active",
    )

    list_filter = (
        "role",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "phone",
    )

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            "PDP Information",
            {
                "fields": (
                    "role",
                    "phone",
                    "avatar",
                    "google_email",
                    "telegram_id",
                    "created_by_admin",
                )
            }
        ),
    )


# ==========================
# PARENT / STUDENT
# ==========================


@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = (
        "parent",
        "student",
        "created_at",
    )

    search_fields = (
        "parent__username",
        "student__username",
    )


# ==========================
# MODULE
# ==========================


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "technology",
        "price",
    )

    ordering = (
        "number",
    )


# ==========================
# GROUP
# ==========================


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "current_module",
        "active",
    )

    list_filter = (
        "active",
        "current_module",
    )

    search_fields = (
        "title",
    )


# ==========================
# LESSON
# ==========================


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "group",
        "number",
        "date",
        "cancelled",
    )

    list_filter = (
        "group",
        "cancelled",
    )

    ordering = (
        "-date",
    )


# ==========================
# EXAMS
# ==========================


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "group",
        "module",
        "date",
        "passing_score",
    )


# ==========================
# PROGRESS
# ==========================


@admin.register(StudentModuleProgress)
class StudentModuleProgressAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "module",
        "exam_score",
        "passed",
    )

    list_filter = (
        "passed",
        "module",
    )


# ==========================
# GRADES
# ==========================


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "lesson",
        "homework_points",
        "classwork_points",
        "total_points",
    )

    search_fields = (
        "student__username",
    )


# ==========================
# ATTENDANCE
# ==========================


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "lesson",
        "status",
    )

    list_filter = (
        "status",
    )


# ==========================
# PAYMENTS
# ==========================


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "module",
        "paid",
        "paid_date",
    )

    list_filter = (
        "paid",
    )


# ==========================
# RATING
# ==========================


@admin.register(StudentRating)
class StudentRatingAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "total_points",
        "updated_at",
    )

    ordering = (
        "-total_points",
    )


# ==========================
# TEACHER SETTINGS
# ==========================


@admin.register(TeacherSettings)
class TeacherSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "hide_student_avatars",
        "hide_group_ratings",
    )


# ==========================
# NOTIFICATIONS
# ==========================


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
    )



@admin.register(GroupModuleTeacher)
class GroupModuleTeacherAdmin(ModelAdmin):
    list_display = (
        "group",
        "module",
        "teacher",
    )

    list_filter = (
        "group",
        "module",
        "teacher",
    )