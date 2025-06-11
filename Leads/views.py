# views.py
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, Avg
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from xhtml2pdf import pisa
from datetime import timedelta, datetime
from django.utils import timezone
from django.utils.dateparse import parse_date
import json
import stripe
import csv
from .models import LeadsForms, UserProfile, Notes, Subscription
from django.conf import settings

# Set Stripe API key from settings
stripe.api_key = settings.STRIPE_SECRET_KEY

# --- Helper Functions ---

def ensure_user_profile(user):
    """
    Ensures a UserProfile exists for the given user, creating one if necessary.
    Returns the UserProfile instance.
    """
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile

# --- Authentication Views ---

def sign_up(request):
    """
    Handles user registration, creating a User and UserProfile.
    Redirects to login page on success, or renders signup page with errors.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        companyname = request.POST.get('companyname')
        role = request.POST.get('role')

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('signup')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect('signup')

            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(user=user, companyname=companyname, role=role)
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'signup.html')

def login(request):
    """
    Handles user login, authenticating credentials.
    Redirects to check_subscription for regular users, or dashboard for admin.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == 'admin':
            leads_monitor = LeadsForms.objects.all()
            return render(request, 'dashboard.html', {'leads': leads_monitor})
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                auth_login(request, user)
                return redirect('check_subscription')
            else:
                messages.error(request, "Invalid username or password.")
                return redirect('login')
    return render(request, 'logins.html')

def logout_view(request):
    """
    Logs out the current user and redirects to the login page.
    """
    logout(request)
    return redirect('login')

# --- Dashboard and Admin Views ---

@login_required
def dashboard(request):
    """
    Displays the user dashboard with lead statistics based on user role.
    Managers see all leads, Members see only their own.
    """
    user = request.user
    user_profile = ensure_user_profile(user)
    role = user_profile.role

    leads = LeadsForms.objects.none()
    if role == 'Manager':
        leads = LeadsForms.objects.all()
    elif role == 'Member':
        leads = LeadsForms.objects.filter(lead_owner=user)

    leads_by_contact = leads.values('contact_name').annotate(count=Count('id')).order_by('-count')
    leads_by_owner = leads.values('lead_owner__username').annotate(count=Count('id')).order_by('-count')
    leads_by_stage = leads.values('lead_stage').annotate(count=Count('id')).order_by('-count')
    closed_won_by_owner = leads.filter(lead_stage='Closed_Won').values('lead_owner__username').annotate(total_revenue=Sum('lead_revenue')).order_by('-total_revenue')

    owners_data = {
        "labels": [item['contact_name'] for item in leads_by_contact],
        "data": [item['count'] for item in leads_by_contact]
    }
    stage_data = {
        "labels": [item['lead_stage'] for item in leads_by_stage],
        "data": [item['count'] for item in leads_by_stage]
    }
    closed_won_data = {
        "labels": [item['lead_owner__username'] for item in closed_won_by_owner],
        "data": [item['total_revenue'] for item in closed_won_by_owner]
    }

    context = {
        'data': {
            'all_active': leads.aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'new': leads.filter(lead_stage='New').aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'hot': leads.filter(lead_stage='Hot').aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'Contacted': leads.filter(lead_stage='Contacted').aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'Follow Up': leads.filter(lead_stage='Follow_Up').aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'Closed Won': leads.filter(lead_stage='Closed_Won').aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'Closed Lost': leads.filter(lead_stage='Closed_Lost').aggregate(value=Sum('lead_revenue'), count=Count('id')),
        },
        'owners_data': json.dumps(owners_data, cls=DjangoJSONEncoder),
        'stage_data': json.dumps(stage_data, cls=DjangoJSONEncoder),
        'closed_won_data': json.dumps(closed_won_data, cls=DjangoJSONEncoder),
    }
    return render(request, 'dashboard.html', context)

@login_required
def admin_page(request):
    """
    Displays the admin dashboard with comprehensive lead statistics.
    Accessible only to admin users.
    """
    leads = LeadsForms.objects.all()
    leads_by_contact = leads.values('contact_name').annotate(count=Count('id')).order_by('-count')
    leads_by_owner = leads.values('lead_owner__username').annotate(count=Count('id')).order_by('-count')
    leads_by_stage = leads.values('lead_stage').annotate(count=Count('id')).order_by('-count')
    closed_won_by_owner = leads.filter(lead_stage='Closed_Won').values('lead_owner__username').annotate(total_reordinate_by_owner = leads.filter(lead_stage='Closed_Won').values('lead_owner__username').annotate(total_revenue=Sum('lead_revenue')).order_by('-total_revenue'))

    owners_data = {
        "labels": [item['contact_name'] for item in leads_by_contact],
        "data": [item['count'] for item in leads_by_contact]
    }
    stage_data = {
        "labels": [item['lead_stage'] for item in leads_by_stage],
        "data": [item['count'] for item in leads_by_stage]
    }
    closed_won_data = {
        "labels": [item['lead_owner__username'] for item in closed_won_by_owner],
        "data": [item['total_revenue'] for item in closed_won_by_owner]
    }

    context = {
        'data': {
            'all_active': leads.aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'new': leads.filter(lead_stage='New').aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'hot': leads.filter(lead_stage='Hot').aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'Contacted': leads.filter(lead_stage='Contacted').aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'Follow Up': leads.filter(lead_stage='Follow_Up').aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'Closed Won': leads.filter(lead_stage='Closed_Won').aggregate(value=Sum('lead_revenue'), count=Count('id')),
            'Closed Lost': leads.filter(lead_stage='Closed_Lost').aggregate(value=Sum('lead_revenue'), count=Count('id')),
        },
        'owners_data': json.dumps(owners_data, cls=DjangoJSONEncoder),
        'stage_data': json.dumps(stage_data, cls=DjangoJSONEncoder),
        'closed_won_data': json.dumps(closed_won_data, cls=DjangoJSONEncoder),
    }
    return render(request, 'admin_page.html', context)

# --- Lead Management Views ---

@login_required
def lead_create(request):
    """
    Creates a new lead and associated notes.
    Redirects to dashboard on success.
    """
    if request.method == 'POST':
        lead_data = LeadsForms(
            lead_title=request.POST.get('lead_title'),
            contact_name=request.POST.get('contact_name'),
            mobile_number=request.POST.get('mobile_number'),
            alternate_number=request.POST.get('alternate_number'),
            email_address=request.POST.get('email_address'),
            lead_stage=request.POST.get('lead_stage'),
            lead_revenue=request.POST.get('lead_revenue'),
            expected_closing_date=request.POST.get('expected_closing_date'),
            lead_owner=request.user,
            follow_up_date=request.POST.get('Follow_Up'),
            follow_up_notes=request.POST.get('Follow_Up_Notes'),
            additional_notes=request.POST.get('textarea'),
            campaign_name=request.POST.get('campaign_name'),
            campaign_content=request.POST.get('campaign_content'),
            campaign_terms=request.POST.get('campaign_terms'),
            caller_name=request.POST.get('caller_name'),
            call_duration=request.POST.get('call_duration'),
            reason_not_connected=request.POST.get('reason_not_connected'),
            contact_reference=request.POST.get('contact_reference'),
            last_call_time=request.POST.get('last_call_time'),
            last_call_status=request.POST.get('last_call_status'),
            last_call_remarks=request.POST.get('last_call_remarks')
        )
        lead_data.save()

        note = Notes(
            follow_up_date=request.POST.get('Follow_Up'),
            follow_up_notes=request.POST.get('Follow_Up_Notes'),
            additional_notes=request.POST.get('textarea'),
        )
        note.save()
        
        return redirect('dashboard')
    context = {'user_name': request.user.username}
    return render(request, 'lead_create.html', context)

@login_required
def lead_view(request):
    """
    Displays a paginated list of leads, filtered by role and search query.
    Managers see all leads, Members see only their own.
    """
    user = request.user
    user_profile = ensure_user_profile(user)
    role = user_profile.role
    query = request.GET.get('q', '').strip()

    if role == 'Manager':
        leads = LeadsForms.objects.all()
    else:
        leads = LeadsForms.objects.filter(lead_owner=user)

    if query:
        leads = LeadsForms.filter(
            Q(contact_name__icontains=query) |
            Q(email_address__icontains=query) |
            Q(mobile_number__icontains=query) |
            Q(lead_owner__username__icontains=query) |
            Q(lead_stage__icontains=query) |
            Q(follow_up_notes__icontains=query)
        ).distinct()

    paginator = Paginator(leads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'leads': page_obj,
        'query': query,
        'total_leads': leads.count(),
        'role': role,
    }
    return render(request, 'leads_view.html', context)

@login_required
def update_lead(request, lead_id):
    """
    Updates an existing lead's details.
    Redirects to lead view on success.
    """
    lead = get_object_or_404(LeadsForms, id=lead_id)
    if request.method == 'POST':
        lead.lead_title = request.POST.get('lead_title', lead.lead_title)
        lead.contact_name = request.POST.get('contact_name', lead.contact_name)
        lead.mobile_number = request.POST.get('mobile_number', lead.mobile_number)
        lead.alternate_number = request.POST.get('alternate_number', lead.alternate_number)
        lead.email_address = request.POST.get('email_address', lead.email_address)
        lead.lead_stage = request.POST.get('lead_stage', lead.lead_stage)
        lead.lead_revenue = request.POST.get('lead_revenue', lead.lead_revenue)
        lead.expected_closing_date = request.POST.get('expected_closing_date', lead.expected_closing_date)
        lead.follow_up_date = request.POST.get('Follow_Up', lead.follow_up_date)
        lead.follow_up_notes = request.POST.get('Follow_Up_Notes', lead.follow_up_notes)
        lead.additional_notes = request.POST.get('textarea', lead.additional_notes)
        lead.save()
        
        messages.success(request, "Lead updated successfully!")
        return redirect('view_leads')
    return render(request, 'update_lead.html', {'lead': lead})

@login_required
def delete_lead(request, lead_id):
    """
    Deletes a lead if the user has permission (owner or Manager).
    Redirects to lead view with success/error message.
    """
    lead = get_object_or_404(LeadsForms, id=lead_id)
    user = request.user
    user_profile = ensure_user_profile(user)
    role = user_profile.role
    if lead.lead_owner == request.user or role == 'Manager':
        lead.delete()
        messages.success(request, "Lead deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this lead.")
    return redirect('view_leads')

# --- Call Management Views ---

@login_required
def call_history(request):
    """
    Displays a paginated list of call logs from LeadsForms, filtered by role, search query, and date range.
    Includes CSV export functionality.
    Managers see all calls, Members see only their own.
    """
    user = request.user
    user_profile = ensure_user_profile(user)
    role = user_profile.role
    query = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if role == 'Manager':
        calls = LeadsForms.objects.exclude(last_call_time__isnull=True)
    else:
        calls = LeadsForms.objects.filter(lead_owner=user).exclude(last_call_time__isnull=True)

    if query:
        calls = calls.filter(
            Q(contact_name__icontains=query) |
            Q(caller_name__icontains=query) |
            Q(last_call_status__icontains=query) |
            Q(last_call_remarks__icontains=query)
        ).distinct()

    if start_date:
        start_date = parse_date(start_date)
        if start_date:
            calls = calls.filter(last_call_time__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        if end_date:
            calls = calls.filter(last_call_time__date__lte=end_date)

    # Handle CSV export
    if 'export' in request.GET and request.GET['export'] == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="call_history.csv"'
        writer = csv.writer(response)
        writer.writerow(['Contact Name', 'Caller', 'Call Time', 'Duration (min)', 'Status', 'Remarks', 'Owner'])
        for call in calls:
            writer.writerow([
                call.contact_name,
                call.caller_name or 'N/A',
                call.last_call_time.strftime('%Y-%m-%d %H:%M') if call.last_call_time else 'N/A',
                call.call_duration or 'N/A',
                call.last_call_status or 'N/A',
                call.last_call_remarks or 'N/A',
                call.lead_owner.username
            ])
        return response

    paginator = Paginator(calls, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'calls': page_obj,
        'query': query,
        'start_date': start_date,
        'end_date': end_date,
        'total_calls': calls.count(),
        'role': role,
    }
    return render(request, 'call_history.html', context)

@login_required
def call_analytics(request):
    """
    Displays call analytics, including total calls, average duration, calls by status, and calls over time.
    Supports time period filtering (e.g., last 7 days, 30 days).
    Managers see all data, Members see only their own.
    """
    user = request.user
    user_profile = ensure_user_profile(user)
    role = user_profile.role
    period = request.GET.get('period', '30')  # Default to last 30 days

    if role == 'Manager':
        calls = LeadsForms.objects.exclude(last_call_time__isnull=True)
    else:
        calls = LeadsForms.objects.filter(lead_owner=user).exclude(last_call_time__isnull=True)

    # Apply time period filter
    try:
        days = int(period)
        start_date = timezone.now() - timedelta(days=days)
        calls = calls.filter(last_call_time__gte=start_date)
    except ValueError:
        days = 30
        start_date = timezone.now() - timedelta(days=30)
        calls = calls.filter(last_call_time__gte=start_date)

    total_calls = calls.count()
    avg_duration = calls.aggregate(avg_duration=Avg('call_duration'))['avg_duration'] or 0
    calls_by_status = calls.values('last_call_status').annotate(count=Count('id')).order_by('-count')
    
    # Calculate success rate (calls associated with Closed_Won leads)
    closed_won_calls = calls.filter(lead_stage='Closed_Won').count()
    success_rate = (closed_won_calls / total_calls * 100) if total_calls > 0 else 0

    # Calls over time (daily count)
    calls_by_day = calls.values('last_call_time__date').annotate(count=Count('id')).order_by('last_call_time__date')
    dates = [item['last_call_time__date'].strftime('%Y-%m-%d') for item in calls_by_day]
    counts = [item['count'] for item in calls_by_day]

    status_data = {
        "labels": [item['last_call_status'] or 'Unknown' for item in calls_by_status],
        "data": [item['count'] for item in calls_by_status]
    }
    time_data = {
        "labels": dates,
        "data": counts
    }

    context = {
        'total_calls': total_calls,
        'avg_duration': round(avg_duration / 60, 2) if avg_duration else 0,  # Convert seconds to minutes
        'success_rate': round(success_rate, 2),
        'status_data': json.dumps(status_data, cls=DjangoJSONEncoder),
        'time_data': json.dumps(time_data, cls=DjangoJSONEncoder),
        'period': period,
    }
    return render(request, 'call_analytics.html', context)

@login_required
def call_topper(request):
    """
    Displays top performers based on call volume, duration, or revenue.
    Includes CSV export for top performers.
    Managers see all users, Members see only themselves.
    """
    user = request.user
    user_profile = ensure_user_profile(user)
    role = user_profile.role
    sort_by = request.GET.get('sort_by', 'call_count')  # Options: call_count, call_duration, revenue

    if role == 'Manager':
        calls = LeadsForms.objects.exclude(last_call_time__isnull=True)
        closed_won = LeadsForms.objects.filter(lead_stage='Closed_Won')
    else:
        calls = LeadsForms.objects.filter(lead_owner=user).exclude(last_call_time__isnull=True)
        closed_won = LeadsForms.objects.filter(lead_owner=user, lead_stage='Closed_Won')

    if sort_by == 'call_count':
        top_users = calls.values('lead_owner__username').annotate(value=Count('id')).order_by('-value')[:5]
    elif sort_by == 'call_duration':
        top_users = calls.values('lead_owner__username').annotate(value=Sum('call_duration')).order_by('-value')[:5]
    else:  # revenue
        top_users = closed_won.values('lead_owner__username').annotate(value=Sum('lead_revenue')).order_by('-value')[:5]

    top_data = {
        "labels": [item['lead_owner__username'] for item in top_users],
        "data": [item['value'] for item in top_users]
    }

    # Handle CSV export
    if 'export' in request.GET and request.GET['export'] == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="top_performers_{sort_by}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Username', sort_by.replace('_', ' ').title()])
        for user in top_users:
            writer.writerow([user['lead_owner__username'], user['value']])
        return response

    context = {
        'top_data': json.dumps(top_data, cls=DjangoJSONEncoder),
        'sort_by': sort_by,
        'role': role,
    }
    return render(request, 'call_topper.html', context)

# --- User Profile View ---

@login_required
def user_profile(request):
    """
    Displays and updates the user's profile information, including profile picture.
    Shows recent leads and calls, and team members for Managers.
    """
    user = request.user
    user_profile = ensure_user_profile(user)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        companyname = request.POST.get('companyname')
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')

        # Validate username
        if username and username != user.username:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('user_profile')
            user.username = username

        # Validate email
        if email and email != user.email:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect('user_profile')
            user.email = email

        # Update password if provided
        if password:
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect('user_profile')
            if len(password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return redirect('user_profile')
            user.set_password(password)

        # Update UserProfile
        user_profile.companyname = companyname or user_profile.companyname
        if role in ['Manager', 'Member']:  # Prevent setting Admin role
            user_profile.role = role
        if profile_picture:
            user_profile.profile_picture = profile_picture
        user.save()
        user_profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile')

    # Get recent activity
    recent_leads = LeadsForms.objects.filter(lead_owner=user).order_by('-id')[:5]
    recent_calls = LeadsForms.objects.filter(lead_owner=user).exclude(last_call_time__isnull=True).order_by('-last_call_time')[:5]
    team_members = UserProfile.objects.filter(reports_to=user) if user_profile.role == 'Manager' else []

    context = {
        'user': user,
        'user_profile': user_profile,
        'recent_leads': recent_leads,
        'recent_calls': recent_calls,
        'team_members': team_members,
    }
    return render(request, 'user_profile.html', context)

# --- Reporting Views ---

@login_required
def reports(request):
    """
    Displays a report of leads filtered by date range.
    Only shows leads owned by the current user.
    """
    leads = LeadsForms.objects.filter(lead_owner=request.user)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = parse_date(start_date)
        if start_date:
            leads = leads.filter(expected_closing_date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        if end_date:
            leads = leads.filter(expected_closing_date__lte=end_date)

    context = {
        'leads': leads,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'leads_reports.html', context)

@login_required
def download_leads_report_pdf(request):
    """
    Generates and downloads a PDF report of leads based on filters.
    Only includes leads owned by the current user.
    """
    user = request.user
    query = request.GET.get('q')
    lead_stage_filter = request.GET.get('lead_stage')
    date_filter = request.GET.get('date')

    leads = LeadsForms.objects.filter(lead_owner=user)
    if query:
        leads = leads.filter(
            Q(contact_name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(email_address__icontains=query)
        )
    if lead_stage_filter:
        leads = leads.filter(lead_stage=lead_stage_filter)
    if date_filter:
        leads = leads.filter(expected_closing_date=date_filter)

    context = {'user': user, 'leads': leads}
    template = get_template('leads_report.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="leads_report.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(f"Error generating PDF: {pisa_status.err}", status=500)

    return response

# --- Subscription and Payment Views ---

@login_required
def check_subscription(request):
    """
    Checks if the user has a valid subscription.
    Redirects to subscription page if invalid, or dashboard if valid.
    """
    if request.user.is_superuser:
        return redirect('dashboard')
    
    try:
        user_profile = request.user.userprofile
        if user_profile.role == 'Admin':
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        pass

    try:
        subscription = request.user.subscription
        if not subscription.is_valid():
            messages.warning(request, "Your subscription has expired. Please renew to continue.")
            return redirect('subscription_page')
    except Subscription.DoesNotExist:
        return redirect('subscription_page')
    
    return redirect('dashboard')

@login_required
def subscription_page(request):
    """
    Displays the user's subscription details.
    """
    try:
        subscription = request.user.subscription
    except Subscription.DoesNotExist:
        subscription = None
    
    return render(request, 'subscription.html', {'subscription': subscription})

@login_required
def create_checkout_session(request):
    """
    Creates a Stripe checkout session for a monthly subscription.
    Redirects to Stripe checkout page.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Monthly Subscription',
                        'description': '30 days access to CRM',
                    },
                    'unit_amount': 1000,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:8000/payment/success/',
            cancel_url='http://127.0.0.1:8000/payment/cancel/',
            metadata={'user_id': request.user.id}
        )
        return redirect(session.url, code=303)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def payment_success(request):
    """
    Handles successful payment, activates/updates subscription.
    Redirects to dashboard with success message.
    """
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        defaults={
            'end_date': timezone.now() + timedelta(days=30),
            'is_active': True
        }
    )
    
    if not created:
        subscription.end_date = timezone.now() + timedelta(days=30)
        subscription.is_active = True
        subscription.save()
    
    messages.success(request, "Payment successful! Your subscription is active.")
    return redirect('dashboard')

def payment_cancel(request):
    """
    Handles payment cancellation, renders cancellation page.
    """
    return render(request, 'cancel.html')

# --- Feature Views ---

def maps(request):
    """
    Displays a map with predefined locations.
    """
    locations = [
        {"name": "Location 1", "lat": 51.505, "lng": -0.09},
        {"name": "Location 2", "lat": 51.515, "lng": -0.1},
    ]
    return render(request, 'maps.html', {'locations': locations})

def inbox(request):
    """
    Displays a mock inbox with sample messages.
    Replace with actual database/API logic as needed.
    """
    messages = [
        {"sender": "+1234567890", "content": "Hello, I need help with my order.", "timestamp": "2025-05-12 10:30"},
        {"sender": "+0987654321", "content": "Can you provide more details about your services?", "timestamp": "2025-05-12 11:00"},
        {"sender": "+1122334455", "content": "Thank you for your quick response!", "timestamp": "2025-05-12 11:30"},
    ]
    return render(request, 'inbox.html', {'messages': messages})

def campaigns(request):
    """
    Handles WhatsApp campaign creation and message sending.
    Replace print statement with actual API integration.
    """
    success = False
    if request.method == 'POST':
        numbers = request.POST['numbers'].split(',')
        message = request.POST['message']
        for number in numbers:
            print(f"Sending message to {number.strip()}: {message}")
        success = True
    return render(request, 'campaigns.html', {'success': success})

def automation(request):
    """
    Saves automation rules for triggers and responses.
    Replace print statement with actual logic.
    """
    success = False
    if request.method == 'POST':
        trigger = request.POST['trigger']
        response = request.POST['response']
        print(f"Automation rule saved: Trigger = {trigger}, Response = {response}")
        success = True
    return render(request, 'automation.html', {'success': success})

def task(request):
    """
    Renders the tasks page.
    """
    return render(request, 'tasks.html')

# --- Home View ---

@login_required
def home(request):
    """
    Renders the home page for logged-in users.
    """
    return render(request, 'logins.html')