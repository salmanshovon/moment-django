from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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