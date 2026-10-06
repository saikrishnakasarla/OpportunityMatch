from django import forms
from .models import Opportunity, Application
from students.models import Branch, AcademicYear, Skill, Interest


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            'title', 'organization', 'description', 'opportunity_type',
            'domain', 'location', 'mode', 'duration', 'minimum_cgpa',
            'maximum_age', 'deadline', 'application_url', 'is_active',
            'eligible_branches', 'eligible_years', 'required_skills', 'interests'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AI Research Internship'}),
            'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Google Research'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed description of the opportunity...'}),
            'opportunity_type': forms.Select(attrs={'class': 'form-select'}),
            'domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Artificial Intelligence'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Remote or San Francisco'}),
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 3 Months'}),
            'minimum_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '10'}),
            'maximum_age': forms.NumberInput(attrs={'class': 'form-control', 'min': '15', 'max': '50'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'application_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'eligible_branches': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'eligible_years': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 4}),
            'required_skills': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
            'interests': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        }


class ApplicationUpdateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Your notes or application reference number...'}),
        }
