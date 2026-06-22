from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from .models import User, Group, StudentProfile, JournalEntry


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'last_name', 'first_name', 'role', 'telegram_id')
    list_filter = ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('Роль и Телеграм', {'fields': ('role', 'telegram_id')}),
    )

class StudentInline(admin.TabularInline):
    model = StudentProfile
    extra = 1

@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ('title', 'teacher')
    inlines = [StudentInline]

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'parent')
    list_filter = ('group',)
    search_fields = ('user__last_name', 'parent__last_name')

@admin.register(JournalEntry)
class JournalAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'grade_class', 'grade_homework', 'is_present')
    list_filter = ('date', 'student__student_profile__group')
    readonly_fields = ('date',)

