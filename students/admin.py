from django.contrib import admin
from .models import Branch, AcademicYear, Skill, Interest, StudentProfile, StudentSkill, Notification


class StudentSkillInline(admin.TabularInline):
    model = StudentSkill
    extra = 1


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'branch', 'year', 'cgpa', 'preferred_mode', 'created_at')
    list_filter = ('branch', 'year', 'preferred_mode', 'availability')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'college')
    inlines = [StudentSkillInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'description')


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'year_number')
    ordering = ('year_number',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
