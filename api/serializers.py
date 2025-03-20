from rest_framework import serializers
from tasks.models import Task
from routines.models import Routine, Notification
from django.utils import timezone
from users.models import UserSettings


class TaskDetails(serializers.ModelSerializer):

    category = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'category', 'task_merit', 
            'created_at', 'updated_at', 'duration', 'due_date', 'due_time', 
            'is_repetitive', 'frequency_interval', 'notification_days', 'is_active', 'color'
        ]

    def get_category(self, obj):
        """
        Returns the category title based on whether it's a public or custom category.
        """
        if obj.category:
            if not obj.category.is_removed:  # Ignore removed public categories
                return obj.category.category.title if obj.category.category else obj.category.custom_title
        return None  # If no valid category exists

    def get_color(self, obj):
        """
        Returns the category color based on whether it's a public or custom category.
        """
        if obj.category:
            if not obj.category.is_removed:  # Ignore removed public categories
                return getattr(obj.category.category, 'color', obj.category.custom_color or '#FFFFFF')
        return '#FFFFFF'  # Default color if no category is found

class TaskList(serializers.ModelSerializer):

    category = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'priority', 'category', 'duration', 'is_repetitive', 'due_date', 'due_time', 'frequency_interval', 'color',
        ]

    def get_category(self, obj):
        """
        Returns the category title based on whether it's a public or custom category.
        """
        if obj.category:
            if not obj.category.is_removed:  # Ignore removed public categories
                return obj.category.category.title if obj.category.category else obj.category.custom_title
        return None  # If no valid category exists

    def get_color(self, obj):
        """
        Returns the category color based on whether it's a public or custom category.
        """
        if obj.category:
            if not obj.category.is_removed:  # Ignore removed public categories
                return getattr(obj.category.category, 'color', obj.category.custom_color or '#FFFFFF')
        return '#FFFFFF'  # Default color if no category is found
    

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['sort']

class RoutineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Routine
        fields = ['id', 'user', 'for_date', 'tasks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_tasks(self, value):
        """
        Validate the 'tasks' field to ensure it contains the required structure.
        - If 'is_task' is True, validate the full set of required fields.
        - If 'is_task' is False, validate a smaller set of required fields.
        - Ensure all tasks have the 'is_task' key.
        """
        for task in value:
            # Ensure all tasks have the 'is_task' key
            if 'is_task' not in task:
                raise serializers.ValidationError("Each task must contain the 'is_task' key.")

            if task['is_task']:  # If it's a task, validate the full set of fields
                required_keys = ['start_time', 'duration', 'id', 'title', 'category', 'priority', 'is_repetitive', 'frequency_interval', 'due_date', 'due_time', 'color']
                if not all(key in task for key in required_keys):
                    raise serializers.ValidationError(f"If 'is_task' is True, the task must contain: {', '.join(required_keys)}.")
            else:  # If it's not a task, validate the smaller set of fields
                required_keys = ['id', 'title', 'duration', 'start_time']
                if not all(key in task for key in required_keys):
                    raise serializers.ValidationError(f"If 'is_task' is False, the task must contain: {', '.join(required_keys)}.")

        return value

    def create(self, validated_data):
        """
        Create a new Routine instance and update the `in_routine` field of tasks to True
        only if the task has `is_task` set to True.
        """
        user = self.context['request'].user
        for_date = validated_data['for_date']
        tasks_data = validated_data['tasks']
        current_time = timezone.now()

        # Check if a routine already exists for the given date and user
        routine, created = Routine.objects.get_or_create(
            user=user,
            for_date=for_date,
            defaults={'tasks': tasks_data, 'created_at': current_time, 'updated_at': current_time}
        )
        Notification.create_or_update_notifications(user, tasks_data)
        if created:
            # If the routine is newly created, update the in_routine field for tasks where is_task is True
            task_ids = [task['id'] for task in tasks_data if task.get('is_task', False)]
            Task.objects.filter(id__in=task_ids).update(in_routine=True)
            return routine
        else:
            # If routine already exists, call update method
            return self.update(routine, validated_data)

    
    def update(self, instance, validated_data):
        """
        Update the Routine instance and handle the `in_routine` field of tasks.
        - Only consider tasks where `is_task` is `True`.
        - Set `in_routine = False` for tasks no longer in the routine.
        - Set `in_routine = True` for newly added tasks.
        """
        # Filter tasks in the old routine where `is_task` is True
        old_tasks_with_is_task = {task['id'] for task in instance.tasks if task.get('is_task', False)}

        # Filter tasks in the new routine where `is_task` is True
        new_tasks_with_is_task = {task['id'] for task in validated_data['tasks'] if task.get('is_task', False)}

        # Update the routine instance
        instance.tasks = validated_data['tasks']
        instance.updated_at = timezone.now()
        instance.save()

        # Set `in_routine = False` for tasks no longer in the routine
        tasks_to_remove = old_tasks_with_is_task - new_tasks_with_is_task
        if tasks_to_remove:
            Task.objects.filter(id__in=tasks_to_remove).update(in_routine=False)

        # Set `in_routine = True` for newly added tasks
        tasks_to_add = new_tasks_with_is_task - old_tasks_with_is_task
        if tasks_to_add:
            Task.objects.filter(id__in=tasks_to_add).update(in_routine=True)

        return instance
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'task', 'title', 'message', 'date_time', 'is_generated', 'is_read', 'notification_type', 'created_at', 'updated_at']