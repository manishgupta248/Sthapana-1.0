from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from apps.people.models import Employee
from apps.tasks.models import Task


@login_required
def dashboard(request):
    open_tasks = Task.objects.exclude(status__in=[Task.STATUS_COMPLETED, Task.STATUS_CANCELLED])
    context = {
        'employee_count': Employee.objects.count(),
        'pending_tasks_count': open_tasks.count(),
        'overdue_tasks_count': open_tasks.filter(due_date__lt=timezone.localdate()).count(),
    }
    return render(request, 'dashboard.html', context)