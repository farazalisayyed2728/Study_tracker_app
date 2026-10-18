from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class StudyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_goals')
    title = models.CharField(max_length=200, help_text="e.g., Backend - Start")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def total_hours(self):
        logs = self.daily_logs.all()
        return sum(log.morning_hours + log.evening_hours for log in logs)


class DailyLog(models.Model):
    goal = models.ForeignKey(
        StudyGoal,
        on_delete=models.CASCADE,
        related_name='daily_logs'
    )
    date = models.DateField()

    # Morning Session
    morning_done = models.BooleanField(default=False)
    morning_not_studied = models.BooleanField(default=False)
    morning_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(24.0)
        ]
    )

    # Evening Session
    evening_done = models.BooleanField(default=False)
    evening_not_studied = models.BooleanField(default=False)
    evening_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(24.0)
        ]
    )

    # Integration / Tracking
    github_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="GitHub commit/repo link"
    )
    github_pushed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('goal', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.goal.title} - {self.date}"

    def clean(self):
        super().clean()
        for session in ('morning', 'evening'):
            if getattr(self, f'{session}_done') and getattr(
                self, f'{session}_not_studied'
            ):
                raise ValidationError({
                    f'{session}_not_studied':
                    'A session cannot be marked both studied and not studied.'
                })