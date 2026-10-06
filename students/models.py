from django.db import models
from django.contrib.auth.models import User


class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Branches"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class AcademicYear(models.Model):
    year_number = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['year_number']

    def __str__(self):
        return self.name


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('Programming Languages', 'Programming Languages'),
        ('Web & Mobile Development', 'Web & Mobile Development'),
        ('AI & Data Science', 'AI & Data Science'),
        ('Cloud & DevOps', 'Cloud & DevOps'),
        ('Databases', 'Databases'),
        ('Tools & Methodologies', 'Tools & Methodologies'),
        ('Cybersecurity', 'Cybersecurity'),
        ('UI/UX Design', 'UI/UX Design'),
        ('Core Engineering', 'Core Engineering'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Programming Languages')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    MODE_PREFERENCE_CHOICES = [
        ('Any', 'Any Mode'),
        ('Online', 'Online / Remote'),
        ('Offline', 'Offline / In-person'),
        ('Hybrid', 'Hybrid'),
    ]

    TYPE_PREFERENCE_CHOICES = [
        ('Any', 'Any Opportunity Type'),
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

    DURATION_PREFERENCE_CHOICES = [
        ('Any', 'Any Duration'),
        ('1-2 Months', 'Short Term (1-2 Months)'),
        ('3-6 Months', 'Medium Term (3-6 Months)'),
        ('6+ Months', 'Long Term (6+ Months)'),
    ]

    AVAILABILITY_CHOICES = [
        ('Immediate', 'Immediate (Ready to start)'),
        ('Within 1 Month', 'Within 1 Month'),
        ('Summer Break', 'Summer Break'),
        ('Flexible', 'Flexible / Part-time'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    college = models.CharField(max_length=200, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Preferences
    preferred_mode = models.CharField(max_length=20, choices=MODE_PREFERENCE_CHOICES, default='Any')
    preferred_type = models.CharField(max_length=30, choices=TYPE_PREFERENCE_CHOICES, default='Any')
    preferred_duration = models.CharField(max_length=30, choices=DURATION_PREFERENCE_CHOICES, default='Any')
    preferred_location = models.CharField(max_length=100, blank=True)
    availability = models.CharField(max_length=30, choices=AVAILABILITY_CHOICES, default='Immediate')

    interests = models.ManyToManyField(Interest, blank=True, related_name='students')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.college or 'Student'})"

    @property
    def full_name(self):
        name = self.user.get_full_name()
        return name if name.strip() else self.user.username

    @property
    def skills(self):
        return Skill.objects.filter(studentskill__student=self)

    @property
    def completion_percentage(self):
        points = 0
        total = 8

        if self.college:
            points += 1
        if self.branch:
            points += 1
        if self.year:
            points += 1
        if self.cgpa and self.cgpa > 0:
            points += 1
        if self.student_skills.exists():
            points += 1
        if self.interests.exists():
            points += 1
        if self.bio:
            points += 1
        if self.preferred_location or self.preferred_mode != 'Any':
            points += 1

        return int((points / total) * 100)


class StudentSkill(models.Model):
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='student_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    skill_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Intermediate')

    class Meta:
        unique_together = ('student', 'skill')
        ordering = ['skill__name']

    def __str__(self):
        return f"{self.student.user.username} - {self.skill.name} ({self.skill_level})"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('match', 'New Match'),
        ('deadline', 'Deadline Alert'),
        ('skill', 'Skill Recommendation'),
        ('general', 'General Notification'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.username} - {self.title}"
