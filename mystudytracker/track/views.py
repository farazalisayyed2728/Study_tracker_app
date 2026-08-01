from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import timedelta
from .models import StudyGoal, DailyLog
from .forms import StudyGoalForm, DailyLogForm

@login_required
def dashboard(views_request):
    goals = StudyGoal.objects.filter(user=views_request.user, is_active=True)
    return render(views_request, 'tracker/dashboard.html', {'goals': goals})

@login_required
def goal_detail(request, goal_id):
    goal = get_object_or_404(StudyGoal, id=goal_id, user=request.user)
    
    # Auto-populate missing days if range exists
    current_date = goal.start_date
    while current_date <= goal.end_date:
        DailyLog.objects.get_or_create(goal=goal, date=current_date)
        current_date += timedelta(days=1)
        
    logs = goal.daily_logs.all().order_by('date')
    return render(request, 'tracker/goal_detail.html', {'goal': goal, 'logs': logs})

@login_required
@require_POST
def update_log(request, log_id):
    log = get_object_or_404(DailyLog, id=log_id, goal__user=request.user)
    form = DailyLogForm(request.POST, instance=log)
    if form.is_valid():
        form.save()
    return redirect('goal_detail', goal_id=log.goal.id)