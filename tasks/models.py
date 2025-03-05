from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.db.models import F, ExpressionWrapper, IntegerField

PRIORITY_CHOICES = [
    (1, "Low"),
    (2, "Medium"),
    (3, "High"),
    (4, "Urgent"),
    (5, "Critical"),
]


class PublicTask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)
    category = models.ForeignKey("TaskCategory", on_delete=models.SET_NULL, blank=True, null=True)
    task_merit = models.IntegerField(blank=True, null=True)  # Merit score for the task

    is_repetitive = models.BooleanField(default=False)  # True for repetitive, False for one-time
    frequency_interval = models.IntegerField(blank=True, null=True)  # Interval in days (e.g., 7 for weekly, 30 for monthly)
    notification_days = models.IntegerField(default=1)  # Days before the due date to notify the user

    def __str__(self):
        return self.title


class PublicTaskCategory(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True, help_text="HTML color code (e.g., #FFFFFF or #000000)")

    def __str__(self):
        return self.title


class TaskCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(PublicTaskCategory, on_delete=models.CASCADE, null=True, blank=True)  # Link to public category (optional)
    custom_title = models.CharField(max_length=255, null=True, blank=True)  # For custom categories
    custom_description = models.TextField(blank=True, null=True)  # For custom categories
    custom_color = models.CharField(max_length=7, blank=True, null=True, help_text="HTML color code (e.g., #FFFFFF or #000000)")
    is_removed = models.BooleanField(default=False)  # Track if the user has removed this category

    class Meta:
        unique_together = ('user', 'category')  # Ensure each user-category pair is unique

    def __str__(self):
        if self.category:
            return f"{self.user.username} - {self.category.title}"
        return f"{self.user.username} - {self.custom_title} (Custom)"
    
    def get_category_details(self):
        """
        Returns the category details based on whether it's a public or custom category.
        """
        if self.category and not self.is_removed:
            # Return details from the linked PublicTaskCategory
            return {
                'title': self.category.title,
                'description': self.category.description,
                'color': self.category.color,
                'is_public': True,
            }
        else:
            # Return details from custom fields
            return {
                'title': self.custom_title,
                'description': self.custom_description,
                'color': self.custom_color,
                'is_public': False,
            }

    @classmethod
    def get_categories(cls, user):
        """
        Returns all category IDs, titles, and colors for a given user.
        """
        categories = cls.objects.filter(user=user)

        return [
            {
                'id': cat.category.id if cat.category else cat.id,
                'title': cat.category.title if cat.category else cat.custom_title,
                'color': getattr(cat.category, 'color', cat.custom_color or '#FFFFFF'),
            }
            for cat in categories if not cat.is_removed
        ]
        

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)
    category = models.ForeignKey("TaskCategory", on_delete=models.SET_NULL, blank=True, null=True)
    task_merit = models.IntegerField(blank=True, null=True)  # Merit score for the task
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.IntegerField(default=20) #default duration of a task is 20 minutes if not specified...
    # Fields for task scheduling
    due_date = models.DateField()  # Due date for the task
    due_time = models.TimeField(blank=True, null=True) # Time field for one-time tasks
    is_repetitive = models.BooleanField(default=False)  # True for repetitive, False for one-time
    frequency_interval = models.IntegerField(blank=True, null=True)  # Interval in days (e.g., 7 for weekly, 30 for monthly)
    notification_days = models.IntegerField(default=1)  # Days before the due date to notify the user
    is_active = models.BooleanField(default=True)  # Active status for scheduling

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving

        # Set default notification days based on frequency_interval
        if self.is_repetitive and not self.notification_days:
            self.set_default_notification_days()

        super().save(*args, **kwargs)


    def update_due_date(self):
        """
        Update the due date for repetitive tasks based on frequency_interval.
        """
        if self.is_repetitive and self.frequency_interval:
            self.due_date += timedelta(days=self.frequency_interval)
            self.save()  # Save the updated due date

    def deactivate(self):
        """
        Deactivate the task (mark as inactive).
        """
        self.is_active = False
        self.save()

    def activate(self):
        """
        Activate the task (mark as active).
        """
        self.is_active = True
        self.save()

    @staticmethod
    def get_user_tasks(user):
        today = timezone.localdate()
        
        # Fetch all tasks for the user that are active
        tasks = Task.objects.filter(
            user=user,
            is_active=True
        )
        
        # Filter tasks where (due_date - today) <= notification_days
        filtered_tasks = [
            task for task in tasks
            if (task.due_date - today) <= timedelta(days=task.notification_days)
        ]
        
        return filtered_tasks
    


@receiver(post_save, sender=User)
def assign_public_categories_to_user(sender, instance, created, **kwargs):
    if created:
        public_categories = PublicTaskCategory.objects.all()

        # Create UserTaskCategory instances for the new user
        TaskCategory.objects.bulk_create([
            TaskCategory(
                user=instance,
                category=cat,  # Link to the public category
                custom_title=None,  # Not a custom category
                custom_description=None,  # Not a custom category
                custom_color=None  # Copy the color from the public category
            )
            for cat in public_categories
        ])