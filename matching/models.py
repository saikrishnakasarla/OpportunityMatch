from django.db import models
from students.models import StudentProfile
from opportunities.models import Opportunity


class MatchResult(models.Model):
    CATEGORY_CHOICES = [
        ('Excellent Match', 'Excellent Match (90-100%)'),
        ('Strong Match', 'Strong Match (75-89%)'),
        ('Moderate Match', 'Moderate Match (60-74%)'),
        ('Low Match', 'Low Match (40-59%)'),
        ('Poor Match', 'Poor Match (<40%)'),
    ]

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name='match_results'
    )
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name='match_results'
    )
    overall_score = models.FloatField(default=0.0)
    is_eligible = models.BooleanField(default=True)

    # Component scores out of their assigned weights:
    # Eligibility: 30%, Skills: 30%, Interests: 20%, Preferences: 10%, Availability: 10%
    eligibility_score = models.FloatField(default=0.0)
    skill_score = models.FloatField(default=0.0)
    interest_score = models.FloatField(default=0.0)
    preference_score = models.FloatField(default=0.0)
    availability_score = models.FloatField(default=0.0)

    match_category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='Poor Match')

    # Detailed explainability data stored as JSON lists
    matched_skills_data = models.JSONField(default=list, blank=True)
    missing_skills_data = models.JSONField(default=list, blank=True)
    explanation_items = models.JSONField(default=list, blank=True)
    ineligibility_reasons = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'opportunity')
        ordering = ['-overall_score', 'opportunity__deadline']

    def __str__(self):
        return f"{self.student.user.username} - {self.opportunity.title}: {self.overall_score}% ({self.match_category})"

    @property
    def score_int(self):
        return int(round(self.overall_score))

    @property
    def badge_color_class(self):
        if self.overall_score >= 90:
            return "bg-emerald text-white"
        elif self.overall_score >= 75:
            return "bg-teal text-white"
        elif self.overall_score >= 60:
            return "bg-primary text-white"
        elif self.overall_score >= 40:
            return "bg-warning text-dark"
        else:
            return "bg-secondary text-white"
