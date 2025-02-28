from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserSettings

class Command(BaseCommand):
    print("✅ Command module loaded")
    help = "Create UserSettings for existing users without one."

    def handle(self, *args, **kwargs):
        users = User.objects.filter(usersettings__isnull=True)
        created_count = 0

        for user in users:
            UserSettings.objects.create(user=user)
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"Created UserSettings for {user.username}"))

        self.stdout.write(self.style.SUCCESS(f"✅ Created UserSettings for {created_count} users."))