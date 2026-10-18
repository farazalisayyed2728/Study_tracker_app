from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse

from datetime import timedelta
import json

from .models import StudyGoal, DailyLog
from .forms import StudyGoalForm, DailyLogForm


@login_required
def dashboard(request):
    goals = StudyGoal.objects.filter(
        user=request.user,
        is_active=True
    ).prefetch_related('daily_logs')

    return render(
        request,
        'track/dashboard.html',
        {'goals': goals}
    )


@login_required
def goal_detail(request, goal_id):
    goal = get_object_or_404(
        StudyGoal,
        id=goal_id,
        user=request.user
    )

    # Auto-populate missing days
    current_date = goal.start_date

    while current_date <= goal.end_date:
        DailyLog.objects.get_or_create(
            goal=goal,
            date=current_date
        )

        current_date += timedelta(days=1)

    logs = goal.daily_logs.all().order_by('date')

    return render(
        request,
        'track/goal_detail.html',
        {
            'goal': goal,
            'logs': logs
        }
    )


@login_required
@require_POST
def update_log(request, log_id):
    log = get_object_or_404(
        DailyLog,
        id=log_id,
        goal__user=request.user
    )

    form = DailyLogForm(
        request.POST,
        instance=log
    )

    if form.is_valid():
        form.save()
    else:
        messages.error(request, 'Please correct the invalid study log values.')

    return redirect(
        'home_detail',
        goal_id=log.goal.id
    )


@login_required
def create_goal(request):
    if request.method == 'POST':
        form = StudyGoalForm(request.POST)

        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()

            return redirect('dashboard')

    else:
        form = StudyGoalForm()

    return render(
        request,
        'track/create_goal.html',
        {'form': form}
    )


@login_required
@require_POST
def toggle_log_status(request, log_id):

    try:
        log = DailyLog.objects.get(
            id=log_id,
            goal__user=request.user
        )

        data = json.loads(request.body)
        if not isinstance(data, dict):
            return JsonResponse({
                'status': 'error',
                'message': 'JSON object required'
            }, status=400)

        # Supported fields
        field_name = data.get('field')
        value = data.get('value')

        if field_name in [
            'morning_done',
            'morning_not_studied',
            'evening_done',
            'evening_not_studied',
            'github_pushed'
        ]:
            if not isinstance(value, bool):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Boolean value required'
                }, status=400)

            setattr(
                log,
                field_name,
                value
            )

            if value and field_name in ('morning_done', 'morning_not_studied'):
                paired_field = (
                    'morning_not_studied'
                    if field_name == 'morning_done'
                    else 'morning_done'
                )
                setattr(log, paired_field, False)
            elif value and field_name in ('evening_done', 'evening_not_studied'):
                paired_field = (
                    'evening_not_studied'
                    if field_name == 'evening_done'
                    else 'evening_done'
                )
                setattr(log, paired_field, False)

            log.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Database Updated!'
            })

        return JsonResponse({
            'status': 'error',
            'message': 'Invalid field'
        }, status=400)

    except DailyLog.DoesNotExist:

        return JsonResponse({
            'status': 'error',
            'message': 'Log not found'
        }, status=404)

    except json.JSONDecodeError:

        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)
