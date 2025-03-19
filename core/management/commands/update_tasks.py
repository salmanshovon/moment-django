from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pytz
from collections import defaultdict
from tasks.models import Task, ArchivedTask
from users.models import Profile  # Ensure correct import of Profile

class Command(BaseCommand):
    help = "Update due dates for overdue repetitive tasks and archive past non-repetitive tasks based on user's timezone"

    def handle(self, *args, **kwargs):
        updated_count = 0
        archived_count = 0

        # Fetch all repetitive tasks
        repetitive_tasks = Task.objects.filter(is_repetitive=True)

        # Fetch all non-repetitive tasks
        non_repetitive_tasks = Task.objects.filter(is_repetitive=False)

        # Group tasks by user
        tasks_by_user = defaultdict(list)
        for task in repetitive_tasks:
            tasks_by_user[task.user].append(task)
        for task in non_repetitive_tasks:
            tasks_by_user[task.user].append(task)

        # Fetch all profiles for users with tasks
        user_ids = tasks_by_user.keys()
        profiles = Profile.objects.filter(user__in=user_ids).select_related('user')

        # Create a dictionary to map user to their timezone
        user_timezone_map = {
            profile.user: pytz.timezone(profile.user_timezone) if profile.user_timezone else pytz.UTC
            for profile in profiles
        }

        # Process tasks for each user
        for user, tasks in tasks_by_user.items():
            user_tz = user_timezone_map.get(user, pytz.UTC)  # Fallback to UTC if profile not found
            user_now = timezone.localtime(timezone.now(), user_tz).date()
            user_yesterday = user_now - timedelta(days=1)  # Yesterday in the user's timezone

            for task in tasks:
                if task.is_repetitive:
                    # Update due dates for overdue repetitive tasks
                    while task.due_date < user_now:
                        if task.frequency_interval == 30:
                            task.due_date += relativedelta(months=1)
                        elif task.frequency_interval == 365:
                            task.due_date += relativedelta(years=1)
                        else:
                            task.due_date += timedelta(days=task.frequency_interval)

                    updated_count += 1
                    task.save()
                else:
                    # Archive non-repetitive tasks that are overdue (due before yesterday)
                    if task.due_date < user_yesterday:
                        archived_task = ArchivedTask(
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
                            archived_at=timezone.now(),  # Set the archived timestamp
                        )
                        archived_task.save()
                        archived_count += 1
                        task.delete()  # Delete the original task (or mark it as inactive if preferred)

        # self.stdout.write(self.style.SUCCESS(
        #     f"Updated {updated_count} overdue repetitive tasks and archived {archived_count} past non-repetitive tasks."
        # ))