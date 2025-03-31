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
    task = models.BigIntegerField(null=True, blank=True)  # Changed from ForeignKey to IntegerField
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
        profile = Profile.objects.filter(user=user).values("user_timezone").first()
        user_tz = pytz.timezone(profile["user_timezone"]) if profile and profile["user_timezone"] else pytz.UTC
        current_time = timezone.localtime(timezone.now(), user_tz)

        # Fetch only necessary fields
        user_notifications = Notification.objects.filter(user=user).values_list("task", "id", "date_time", "is_generated", "is_read")
        
        # Store existing notification tasks for quick lookup
        notifications_dict = {str(task): (notif_id, date_time, is_generated, is_read) for task, notif_id, date_time, is_generated, is_read in user_notifications if task is not None}

        notifications_to_update = []
        notifications_to_create = []

        for task in tasks:
            task_id = task.get('id')
            if task_id is None:
                continue
            
            task_id_str = str(task_id)
            task_start_time = datetime.fromisoformat(task['start_time'].replace('Z', '+00:00'))
            task_start_time = timezone.localtime(task_start_time, user_tz)

            if task_id_str in notifications_dict:
                notif_id, old_time, is_generated, is_read = notifications_dict[task_id_str]

                # Update only if the time has changed
                if old_time != task_start_time:
                    notifications_to_update.append(Notification(
                        id=notif_id,
                        date_time=task_start_time,
                        is_generated=False if old_time < current_time and task_start_time > current_time else is_generated,
                        is_read=False if old_time < current_time and task_start_time > current_time else is_read
                    ))
            else:
                notifications_to_create.append(Notification(
                    user=user,
                    task=task_id,
                    title=task['title'],
                    message=f"Reminder for {task['title']}",
                    date_time=task_start_time,
                    notification_type='reminder',
                ))

        # Perform bulk updates and inserts in a single query each
        if notifications_to_update:
            Notification.objects.bulk_update(notifications_to_update, ['date_time', 'is_generated', 'is_read'])

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