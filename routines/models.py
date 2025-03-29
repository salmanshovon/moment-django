from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from tasks.models import Task
from users.models import Profile
from datetime import datetime
import pytz


class RoutineTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template_name = models.CharField(max_length=255)
    tasks = models.JSONField()  # Stores list of {start_time, end_time, task_id}
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.template_name
    
class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    for_date = models.DateField()  # The date for which the routine is created
    tasks = models.JSONField()  # Stores list of {start_time, end_time, task_id}
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Routine for {self.for_date} by {self.user.username}"
    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('reminder', 'Reminder'),
        ('alert', 'Alert'),
        ('update', 'Update'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    task = models.IntegerField(null=True, blank=True)  # Changed from ForeignKey to IntegerField
    title = models.CharField(max_length=255)
    message = models.TextField()
    date_time = models.DateTimeField()  # When the notification should be triggered
    is_generated = models.BooleanField(default=False)  # Whether the notification has been sent
    is_read = models.BooleanField(default=False)  # Whether the user has read the notification
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='reminder')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"
    

    @classmethod
    def get_user_notifications(cls, user):
        """
        Retrieves all notifications for a given user.

        Args:
            user (User): The user for whom to retrieve notifications.

        Returns:
            QuerySet: A QuerySet containing all notifications for the user, ordered by date_time in descending order.
        """
        return cls.objects.filter(user=user).order_by('date_time')
    
    @staticmethod
    def create_or_update_notifications(user, tasks):
        # Retrieve the user's profile
        profile = Profile.objects.filter(user=user).first()

        # Get the user's timezone from the profile, default to UTC if not set
        user_tz = pytz.timezone(profile.user_timezone) if profile and profile.user_timezone else pytz.UTC

        # Get the current time in the user's timezone
        current_time = timezone.localtime(timezone.now(), user_tz)
        # current_time = c_time.replace(tzinfo=None)

        # Fetch all notifications for the user in a single query
        user_notifications = Notification.objects.filter(user=user)
        notifications_dict = {notification.task: notification for notification in user_notifications}  # Use 'task' instead of 'task_id'

        notifications_to_update = []
        notifications_to_create = []

        for task in tasks:
            # Parse the task's start time (assumed to already be in the user's timezone)
            task_start_time = datetime.fromisoformat(task['start_time'].replace('Z', '+00:00')) #replace Z with +00:00 to make it parseable by fromisoformat.
            task_start_time = timezone.localtime(task_start_time, user_tz)

            task_id = task.get('id')
            notification = notifications_dict.get(task_id)  # Lookup by task_id

            if notification:
                # If the notification exists, update its time with the given time
                old_time = notification.date_time
                notification.date_time = task_start_time

                # Reset notification flags if the task is rescheduled to the future
                if old_time < current_time and task_start_time > current_time:
                    notification.is_generated = False
                    notification.is_read = False

                notifications_to_update.append(notification)
            else:
                # If the notification doesn't exist, create it with the given time
                notification_data = {
                    'user': user,
                    'task': task_id,  # Always set the task field with task_id
                    'title': task['title'],
                    'message': f"Reminder for {task['title']}",
                    'date_time': task_start_time,
                    'notification_type': 'reminder',
                }

                notifications_to_create.append(
                    Notification(**notification_data)
                )

        # Bulk update existing notifications
        if notifications_to_update:
            Notification.objects.bulk_update(notifications_to_update, ['date_time', 'is_generated', 'is_read'])

        # Bulk create new notifications
        if notifications_to_create:
            Notification.objects.bulk_create(notifications_to_create)
    
class Reflection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    for_date = models.DateField()  # The date being reflected upon
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE)
    task_results = models.JSONField()  # Stores list of {task_id, completed, alternative_task, task_merit}
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reflection for {self.for_date} by {self.user.username}"
    
class Archive(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_title = models.CharField(max_length=255)
    for_date = models.DateField()  # The date the task was completed
    created_at = models.DateTimeField(default=timezone.now)
    completion = models.BooleanField(default=False)

    def __str__(self):
        return f"Archived Task: {self.task_title} by {self.user.username}"
    
class Irrigate(models.Model):
    time = models.IntegerField(help_text="Duration of irrigation in minutes")
    command = models.BooleanField(default=False, help_text="On/Off command for irrigation")
    update_time = models.DateTimeField(default=timezone.now, help_text="When the record was last updated")
    action_time = models.DateTimeField(default=timezone.now, help_text="When the irrigation was actually performed")

    def __str__(self):
        return f"Irrigation for {self.time} mins at {self.action_time}"

    class Meta:
        ordering = ['-action_time']