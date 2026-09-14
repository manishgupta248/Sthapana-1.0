from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.people.models import Employee


@login_required
def dashboard(request):
    context = {
        'employee_count': Employee.objects.count(),
    }
    return render(request, 'dashboard.html', context)