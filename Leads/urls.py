# urls.py
from django.urls import path, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

# URL patterns for the application
urlpatterns = [
    # Admin route
    path('admin/', admin.site.urls),

    # Home Route
    path('', views.home, name='home'),

    # Authentication Routes
    path('signup/', views.sign_up, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('check_subscription/', views.check_subscription, name='check_subscription'),

    # Dashboard and Admin Routes
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_page/', views.admin_page, name='admin_page'),

    # Lead Management Routes
    path('lead_create/', views.lead_create, name='LeadCreate'),
    path('view_leads/', views.lead_view, name='view_leads'),
    path('update_lead/<int:lead_id>/', views.update_lead, name='update_lead'),
    path('delete_lead/<int:lead_id>/', views.delete_lead, name='delete_lead'),

    # Reporting Routes
    path('leads_report/', views.reports, name='Report'),
    # Redirect for case-insensitive Leads_Report

    # Subscription and Payment Routes
    path('subscription/', views.subscription_page, name='subscription_page'),
    path('create-checkout-session/', views.create_checkout_session, name='checkout-session'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),

    # Feature Routes
    path('maps/', views.maps, name='maps'),
    path('whatsapp/inbox/', views.inbox, name='inbox'),
    path('whatsapp/campaigns/', views.campaigns, name='campaigns'),
    path('whatsapp/automation/', views.automation, name='automation'),
    path('tasks/', views.task, name='Tasks'),

    # Call Management Routes
    path('calls/history/', views.call_history, name='call_history'),
    path('calls/analytics/', views.call_analytics, name='call_analytics'),
    path('calls/topper/', views.call_topper, name='call_topper'),

    # User Profile Route
    path('user_profile/', views.user_profile, name='user_profile'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)