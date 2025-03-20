from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pytz
from collections import defaultdict
from tasks.models import Task, ArchivedTask
from users.models import Profile
from routines.models import Notification

BATCH_SIZE = 1000  # Define the batch size

class Command(BaseCommand):
    help = "Update due dates for overdue repetitive tasks, archive past non-repetitive tasks, and remove old notifications based on user's timezone"

    def handle(self, *args, **kwargs):
        updated_tasks = []
        archived_tasks = []
        deleted_notifications_count = 0

        # Fetch all user profiles with timezone mapping in a single query
        profiles = Profile.objects.select_related('user').all()
        user_timezone_map = {
            profile.user: pytz.timezone(profile.user_timezone) if profile.user_timezone else pytz.UTC
            for profile in profiles
        }

        # Process tasks in batches to avoid memory overload
        task_count = Task.objects.count()
        for offset in range(0, task_count, BATCH_SIZE):
            tasks = Task.objects.select_related('user__profile')[offset : offset + BATCH_SIZE]
            tasks_by_user = defaultdict(list)

            for task in tasks:
                tasks_by_user[task.user].append(task)

            for user, tasks in tasks_by_user.items():
                user_tz = user_timezone_map.get(user, pytz.UTC)  # Fallback to UTC if profile not found
                user_now = timezone.localtime(timezone.now(), user_tz)
                user_36_hours_ago = user_now - timedelta(hours=36)
                user_yesterday = user_now - timedelta(days=1)

                # Delete notifications older than 36 hours in batches
                deleted_notifications = Notification.objects.filter(
                    user=user,
                    date_time__lt=user_36_hours_ago
                )[:BATCH_SIZE].delete()
                deleted_notifications_count += deleted_notifications[0]  # Count deleted notifications

                for task in tasks:
                    if task.is_repetitive:
                        # Update due dates for overdue repetitive tasks
                        while task.due_date < user_now.date():
                            if task.frequency_interval == 30:
                                task.due_date += relativedelta(months=1)
                            elif task.frequency_interval == 365:
                                task.due_date += relativedelta(years=1)
                            else:
                                task.due_date += timedelta(days=task.frequency_interval)
                        updated_tasks.append(task)
                    else:
                        # Archive non-repetitive tasks that are overdue
                        if task.due_date < user_yesterday.date():
                            archived_tasks.append(ArchivedTask(
                                user=task.user,
                                title=task.title,
                                description=task.description,
                                priority=task.priority,
                                category=task.category,
                                task_merit=task.task_merit,
                                created_at=task.created_at,
                                updated_at=task.updated_at,
                                duration=task.duration,
                                due_date=task.due_date,
                                due_time=task.due_time,
                                is_repetitive=task.is_repetitive,
                                frequency_interval=task.frequency_interval,
                                notification_days=task.notification_days,
                                is_active=False,  # Archived tasks are inactive
                                in_routine=task.in_routine,
                                archived_at=timezone.now(),
                            ))
                            task.delete()  # Delete the original task

        # Bulk update repetitive tasks
        if updated_tasks:
            Task.objects.bulk_update(updated_tasks, ['due_date'], batch_size=BATCH_SIZE)

        # Bulk create archived tasks
        if archived_tasks:
            ArchivedTask.objects.bulk_create(archived_tasks, batch_size=BATCH_SIZE)

        # self.stdout.write(self.style.SUCCESS(
        #     f"Updated {len(updated_tasks)} repetitive tasks, "
        #     f"archived {len(archived_tasks)} non-repetitive tasks, "
        #     f"and deleted {deleted_notifications_count} old notifications."
        # ))
