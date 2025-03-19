from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pytz
from tasks.models import Task
from users.models import Profile  # Ensure correct import of Profile

class Command(BaseCommand):
    help = "Update due dates for overdue repetitive tasks based on user's timezone"

    def handle(self, *args, **kwargs):
        updated_count = 0
        repetitive_tasks = Task.objects.filter(is_repetitive=True)

        for task in repetitive_tasks:
            try:
                # Get user's timezone or fallback to UTC
                profile = Profile.objects.get(user=task.user)
                user_tz = pytz.timezone(profile.user_timezone) if profile.user_timezone else pytz.UTC

                # Convert now() to user's timezone
                user_now = timezone.localtime(timezone.now(), user_tz).date()

                # Keep updating overdue tasks
                while task.due_date < user_now:
                    if task.frequency_interval == 30:
                        task.due_date += relativedelta(months=1)
                    elif task.frequency_interval == 365:
                        task.due_date += relativedelta(years=1)
                    else:
                        task.due_date += timedelta(days=task.frequency_interval)

                updated_count += 1

                task.save()

            except Profile.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Profile not found for user {task.user.id}"))

        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} overdue repetitive tasks."))
