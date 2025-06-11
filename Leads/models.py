# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role_choices = (
        ('Manager', 'Manager'),
        ('Admin', 'Admin'),
        ('Member', 'Member'),
    )
    role = models.CharField(max_length=20, choices=role_choices, default='Member')
    reports_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='team_members', help_text="The supervisor this user reports to"
    )
    companyname = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class LeadsForms(models.Model):
    lead_title = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    alternate_number = models.CharField(max_length=15, blank=True, null=True)
    email_address = models.EmailField(max_length=100)
    lead_stage_choices = (
        ('New', 'New'),
        ('Hot', 'Hot'),
        ('Contacted', 'Contacted'),
        ('Follow_Up', 'Follow_Up'),
        ('Closed_Won', 'Closed_Won'),
        ('Closed_Lost', 'Closed_Lost'),
    )
    lead_stage = models.CharField(max_length=20, choices=lead_stage_choices)
    lead_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    expected_closing_date = models.DateField()
    lead_owner = models.ForeignKey(User, related_name='leads_owned', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='leads_assigned', on_delete=models.SET_NULL, null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    campaign_name = models.CharField(max_length=100, blank=True, null=True)
    campaign_content = models.TextField(blank=True, null=True)
    campaign_terms = models.TextField(blank=True, null=True)
    caller_name = models.CharField(max_length=100, blank=True, null=True)
    call_duration = models.IntegerField(null=True, blank=True, help_text="Call duration in seconds")
    reason_not_connected = models.CharField(max_length=255, blank=True, null=True)
    contact_reference = models.CharField(max_length=255, blank=True, null=True)
    last_call_time = models.DateTimeField(null=True, blank=True)
    last_call_status = models.CharField(max_length=100, blank=True, null=True)
    last_call_remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.contact_name

    @classmethod
    def get_leads_for_user(cls, user):
        """Retrieve leads based on the user's role in the system."""
        try:
            user_profile = UserProfile.objects.get(user=user)
            user_role = user_profile.role

            if user_role == 'Manager':
                return cls.objects.all()
            else:
                return cls.objects.filter(lead_owner=user)
        except UserProfile.DoesNotExist:
            return cls.objects.none()


class Notes(models.Model):
    follow_up_date = models.DateField()
    follow_up_notes = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Note for {self.follow_up_date}"


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        return self.is_active and self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user.username}'s subscription"