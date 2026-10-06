from django.contrib import admin
from .models import MatchResult


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'overall_score', 'match_category', 'is_eligible', 'updated_at')
    list_filter = ('match_category', 'is_eligible')
    search_fields = ('student__user__username', 'opportunity__title')
    readonly_fields = ('overall_score', 'eligibility_score', 'skill_score', 'interest_score', 'preference_score', 'availability_score')
