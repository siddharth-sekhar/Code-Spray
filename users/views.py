# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from problems.models import Submission, Problem, Topic

# Use @never_cache to prevent caching
@never_cache
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form}, status=200)

# ✅ SIGNUP view
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

# ✅ DASHBOARD view
@login_required
def dashboard(request):
    submissions = Submission.objects.filter(user=request.user)
    problems_solved = (
        submissions.filter(status='AC')
        .values('problem')
        .distinct()
        .count()
    )

    # Show last 5 submissions
    recent_submissions = submissions.order_by('-submitted_at')[:5]

    # Fetch all topics with their problems
    topics = Topic.objects.all().prefetch_related('problem_set')
    
    # Get total problems count
    total_problems = Problem.objects.count()

    return render(request, 'users/dashboard.html', {
        'submissions': recent_submissions,
        'problems_solved': problems_solved,
        'total_problems': total_problems,
        'topics': topics,
    })