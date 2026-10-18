from django import forms
from .models import StudyGoal, DailyLog


class StudyGoalForm(forms.ModelForm):
    class Meta:
        model = StudyGoal

        fields = [
            'title',
            'start_date',
            'end_date'
        ]

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Backend - Start'
                }
            ),

            'start_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'end_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date must be on or after the start date.')

        return cleaned_data


class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog

        fields = [
            'morning_done',
            'morning_not_studied',
            'morning_hours',
            'evening_done',
            'evening_not_studied',
            'evening_hours',
            'github_pushed',
            'github_link'
        ]

        widgets = {
            'morning_done': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input study-checkbox'
                }
            ),

            'morning_hours': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.5',
                    'min': '0'
                }
            ),

            'morning_not_studied': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),

            'evening_done': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input study-checkbox'
                }
            ),

            'evening_hours': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.5',
                    'min': '0'
                }
            ),

            'evening_not_studied': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),

            'github_pushed': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),

            'github_link': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://github.com/...'
                }
            ),
        }
