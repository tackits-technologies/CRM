from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Subscription

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            exempt_urls = [
                reverse('checkout-session'),
                reverse('payment_success'),
                reverse('payment_cancel'),
                reverse('logout'),
                reverse('login'),
                reverse('signup'),
                reverse('subscription_page'),
                '/static/',  # Allow static files
                '/media/'   # Allow media files
            ]

            if not any(request.path.startswith(url) for url in exempt_urls):
                try:
                    subscription = request.user.subscription
                    if not subscription.is_valid():
                        messages.warning(request, "Your subscription has expired. Please renew to continue.")
                        return redirect('subscription_page')
                except Subscription.DoesNotExist:
                    return redirect('subscription_page')

        response = self.get_response(request)
        return response