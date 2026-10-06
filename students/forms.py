from django import forms
from django.contrib.auth.models import User
from .models import StudentProfile, StudentSkill, Skill, Interest


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'college', 'branch', 'year', 'cgpa', 'phone', 'bio',
            'preferred_mode', 'preferred_type', 'preferred_duration',
            'preferred_location', 'availability'
        ]
        widgets = {
            'college': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Stanford University'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '10'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 555-0199'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of your background and career goals...'}),
            'preferred_mode': forms.Select(attrs={'class': 'form-select'}),
            'preferred_type': forms.Select(attrs={'class': 'form-select'}),
            'preferred_duration': forms.Select(attrs={'class': 'form-select'}),
            'preferred_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Remote, Bangalore, New York'}),
            'availability': forms.Select(attrs={'class': 'form-select'}),
        }


class AddStudentSkillForm(forms.ModelForm):
    class Meta:
        model = StudentSkill
        fields = ['skill', 'skill_level']
        widgets = {
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'skill_level': forms.Select(attrs={'class': 'form-select'}),
        }


class StudentInterestsForm(forms.Form):
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
