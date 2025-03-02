from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_updated = models.BooleanField(default=False)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    picture = models.URLField(blank=True, null=True)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sort = models.CharField(max_length=15, default="title")
    theme = models.IntegerField(default=0)

    def __str__(self):
        return f"Settings for {self.user.username}"

@receiver(social_account_added)
def create_social_user_profile(request, sociallogin, **kwargs):
    """ Create a profile only when a user logs in via social authentication """
    user = sociallogin.user
    Profile.objects.get_or_create(user=user)
    UserSettings.objects.get_or_create(user=user)

@receiver(post_save, sender=User)
def create_superuser_profile(sender, instance, created, **kwargs):
    """ Ensure profile is created only for superusers (not normal users) """
    if created and instance.is_superuser:  
        Profile.objects.get_or_create(user=instance)
        UserSettings.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        UserSettings.objects.get_or_create(user=instance)