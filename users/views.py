# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from problems.models import Submission, Problem, Topic
import time

def session_valid_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_root')  
        
        last_activity = request.session.get('last_activity', 0)
        if time.time() - last_activity > 3600:  # 1 hour
            logout(request)
            request.session.flush()
            return redirect('login_root')  # Use root-level login URL
        
        # Update last activity
        request.session['last_activity'] = time.time()
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Custom middleware to prevent back button access after logout
class PreventBackButtonMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # Add a timestamp to track when user was last active
            request.session['last_activity'] = time.time()
        return None

    def process_response(self, request, response):
        if request.user.is_authenticated:
            # Add cache control headers to prevent caching
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response

# Use @never_cache to prevent caching
@never_cache
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard_root')  # Use root-level dashboard URL
    
    # Get the next parameter for redirect after login
    next_url = request.GET.get('next') or request.POST.get('next', 'dashboard_root')
    
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Set session timestamp
            request.session['last_activity'] = time.time()
            request.session['login_time'] = time.time()
            # Redirect to next_url or dashboard
            return redirect(next_url if next_url != 'dashboard_root' else 'dashboard_root')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form, 'next': next_url}, status=200)


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['last_activity'] = time.time()
            request.session['login_time'] = time.time()
            return redirect('dashboard_root')  # Use root-level dashboard URL
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

# ✅ DASHBOARD view with enhanced security
@login_required
@session_valid_required
@never_cache
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

# Enhanced logout view with comprehensive session cleanup
@require_http_methods(["POST"])
@never_cache
def user_logout(request):
    # Clear all session data
    request.session.flush()
    
    # Logout the user
    logout(request)
    
    # Set response headers to prevent caching
    response = redirect('login_root')  # Use the root-level login URL
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    # Add logout success parameter using reverse to get the correct URL
    from django.urls import reverse
    logout_url = reverse('login_root') + '?logout=success'
    response['Location'] = logout_url
    
    return response