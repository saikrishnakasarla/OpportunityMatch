from django.db import models
from django.utils import timezone
from students.models import Branch, AcademicYear, Skill, Interest, StudentProfile


class Opportunity(models.Model):
    TYPE_CHOICES = [
        ('Internship', 'Internship'),
        ('Hackathon', 'Hackathon'),
        ('Scholarship', 'Scholarship'),
        ('Competition', 'Competition'),
        ('Workshop', 'Workshop'),
        ('Research', 'Research'),
        ('Fellowship', 'Fellowship'),
        ('Certification', 'Certification'),
        ('Training', 'Training'),
    ]

    MODE_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
        ('Hybrid', 'Hybrid'),
    ]

    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    description = models.TextField()
    opportunity_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    domain = models.CharField(max_length=100, help_text="e.g. AI/ML, Web Development, Cloud Computing")
    location = models.CharField(max_length=150, default='Remote')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='Online')
    duration = models.CharField(max_length=100, default='3 Months')
    minimum_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    maximum_age = models.PositiveSmallIntegerField(null=True, blank=True)
    deadline = models.DateField()
    application_url = models.URLField(max_length=500)
    is_active = models.BooleanField(default=True)

    # Relational eligibility & matching fields
    eligible_branches = models.ManyToManyField(
        Branch, blank=True, related_name='eligible_opportunities',
        help_text="If empty, open to all branches"
    )
    eligible_years = models.ManyToManyField(
        AcademicYear, blank=True, related_name='eligible_opportunities',
        help_text="If empty, open to all academic years"
    )
    required_skills = models.ManyToManyField(
        Skill, blank=True, related_name='required_for_opportunities'
    )
    interests = models.ManyToManyField(
        Interest, blank=True, related_name='opportunities'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline', '-created_at']
        verbose_name_plural = "Opportunities"

    def __str__(self):
        return f"{self.title} - {self.organization} ({self.opportunity_type})"

    @property
    def is_expired(self):
        return self.deadline < timezone.now().date()

    @property
    def days_remaining(self):
        delta = (self.deadline - timezone.now().date()).days
        return max(0, delta)


class SavedOpportunity(models.Model):
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name='saved_opportunities'
    )
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name='saved_by_students'
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'opportunity')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.student.user.username} saved {self.opportunity.title}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('Saved', 'Saved'),
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name='applications'
    )
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name='applications'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Applied')
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'opportunity')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student.user.username} -> {self.opportunity.title} [{self.status}]"
