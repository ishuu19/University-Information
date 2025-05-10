from django import forms
from .models import AcademicBackground

class AcademicBackgroundForm(forms.ModelForm):
    class Meta:
        model = AcademicBackground
        fields = [
            'school_name',
            'level_completed',
            'field_of_study',
            'result_type',
            'result_value',
            'completion_year',
            'start_year',
            'additional_info'
        ]
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter school name'}),
            'level_completed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Bachelor\'s Degree'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Science'}),
            'result_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., GPA, Percentage'}),
            'result_value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3.8, 85%'}),
            'completion_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2100'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2100'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional information about your education'})
        }

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        completion_year = cleaned_data.get('completion_year')

        if start_year and completion_year and start_year > completion_year:
            raise forms.ValidationError("Start year cannot be later than completion year")

        return cleaned_data 