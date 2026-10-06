from django.contrib import admin
from .models import Opportunity, SavedOpportunity, Application


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'opportunity_type', 'mode', 'minimum_cgpa', 'deadline', 'is_active')
    list_filter = ('opportunity_type', 'mode', 'is_active', 'eligible_branches')
    search_fields = ('title', 'organization', 'description', 'domain')
    filter_horizontal = ('eligible_branches', 'eligible_years', 'required_skills', 'interests')
    date_hierarchy = 'deadline'


@admin.register(SavedOpportunity)
class SavedOpportunityAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('student__user__username', 'opportunity__title')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('student__user__username', 'opportunity__title')
