from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from users.models import Profile
import pytz

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
    category = models.ForeignKey("PublicTaskCategory", on_delete=models.SET_NULL, blank=True, null=True)
    task_merit = models.IntegerField(blank=True, null=True)  # Merit score for the task

    duration = models.IntegerField(default=20) #default duration of a task is 20 minutes if not specified...
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
                'id': cat.id,
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
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, blank=True, null=True)
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
    in_routine = models.BooleanField(default=False)

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
    def get_user_tasks(user, param):
        # Get user's timezone or fallback to UTC
        profile = Profile.objects.get(user=user)
        user_tz = pytz.timezone(profile.user_timezone) if profile.user_timezone else pytz.UTC
        if param:
            date = timezone.localtime(timezone.now(), user_tz).date()  # Today's date in user's timezone
        else:
            date = timezone.localtime(timezone.now(), user_tz).date() + timedelta(days=1)  # Tomorrow's date
        
        # Fetch all tasks for the user that are active
        tasks = Task.objects.filter(
            user=user,
            is_active=True,
        )
        
        filtered_tasks = []
        for task in tasks:
            if task.frequency_interval == 1:
                filtered_tasks.append(task)
            else:
                days_until_due = (task.due_date - date).days
                # print(f"days untill due: {days_until_due} - notification days: {task.notification_days} - routine: {task.in_routine}")
                if 0 <= days_until_due <= task.notification_days and not task.in_routine:
                    filtered_tasks.append(task)
        return filtered_tasks
    
    @staticmethod
    def get_repetitive_task_due_date_map(user: User) -> dict:
        """
        Returns a dictionary mapping task IDs to their due_dates for all active,
        repetitive tasks belonging to the user.
        """
        repetitive_tasks = Task.objects.filter(
            user=user,
            is_repetitive=True,
            is_active=True
        )
        return {task.id: task.due_date for task in repetitive_tasks}
    
    @staticmethod
    def get_repetitive_tasks(user):
        """
        Returns all repetitive tasks for a given user, regardless of
        notification days and due date.
        """
        return Task.objects.filter(user=user, is_repetitive=True)


class ArchivedTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)  # Use the same choices as Task
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, blank=True, null=True)
    task_merit = models.IntegerField(blank=True, null=True)  # Merit score for the task
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.IntegerField(default=20)  # Default duration of a task is 20 minutes
    due_date = models.DateField()  # Due date for the task
    due_time = models.TimeField(blank=True, null=True)  # Time field for one-time tasks
    is_repetitive = models.BooleanField(default=False)  # True for repetitive, False for one-time
    frequency_interval = models.IntegerField(blank=True, null=True)  # Interval in days
    notification_days = models.IntegerField(default=1)  # Days before the due date to notify the user
    is_active = models.BooleanField(default=False)  # Archived tasks are inactive by default
    in_routine = models.BooleanField(default=False)
    archived_at = models.DateTimeField(default=timezone.now)  # Timestamp when the task was archived

    def __str__(self):
        return f"Archived Task: {self.title} (User: {self.user.username})"

    class Meta:
        verbose_name = "Archived Task"
        verbose_name_plural = "Archived Tasks"

    @staticmethod
    def get_archived_tasks_by_timeframe(user, start_date, end_date):
        """
        Returns all archived tasks for a given user within a specified time frame.
        
        Args:
            user (User): The user whose archived tasks to retrieve
            start_date (date/datetime): The start date of the time frame (inclusive)
            end_date (date/datetime): The end date of the time frame (inclusive)
            
        Returns:
            QuerySet: A queryset of ArchivedTask objects matching the criteria
        """
        return ArchivedTask.objects.filter(
            user=user,
            archived_at__date__gte=start_date,
            archived_at__date__lte=end_date
        ).order_by('-archived_at')

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