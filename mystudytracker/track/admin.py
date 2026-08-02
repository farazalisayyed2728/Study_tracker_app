from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import StudyGoal, DailyLog

class DailyLogInline(admin.TabularInline):
    """Goal page ke andar hi pure mahine ke daily records dekhne ke liye"""
    model = DailyLog
    extra = 0
    fields = ('date', 'morning_done', 'morning_hours', 'evening_done', 'evening_hours', 'github_pushed', 'github_link')
    readonly_fields = ('date',)
    ordering = ('date',)

@admin.register(StudyGoal)
class StudyGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_date', 'end_date', 'total_hours', 'is_active')
    list_filter = ('is_active', 'user', 'start_date')
    search_fields = ('title', 'user__username')
    inlines = [DailyLogInline]

@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'goal', 'get_user', 'morning_done', 'morning_hours', 'evening_done', 'evening_hours', 'github_pushed')
    list_filter = ('date', 'morning_done', 'evening_done', 'github_pushed', 'goal')
    search_fields = ('goal__title', 'goal__user__username', 'github_link')
    date_hierarchy = 'date'  # Date timeline filter top par show karega
    list_editable = ('morning_done', 'evening_done', 'github_pushed') # Admin table se direct checkmark handle karne ke liye

    def get_user(self, obj):
        return obj.goal.user
    get_user.short_description = 'User'