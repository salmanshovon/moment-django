from rest_framework import serializers
from tasks.models import Task
from routines.models import Routine
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
        """
        for task in value:
            if not all(key in task for key in ['start_time', 'duration', 'id', 'title', 'category', 'priority','is_repetitive','frequency_interval', 'due_date', 'due_time', 'color']):
                raise serializers.ValidationError("Each task must contain 'start_time', 'duration', 'id', 'title', 'frequency_interval', 'due_date', 'due_time', 'color', 'category', and 'priority'.")
        return value

    def create(self, validated_data):
        """
        Create a new Routine instance and update the `in_routine` field of tasks to True.
        """
        user = self.context['request'].user
        for_date = validated_data['for_date']
        tasks_data = validated_data['tasks']

        # Check if a routine already exists for the given date and user
        routine, created = Routine.objects.get_or_create(
            user=user,
            for_date=for_date,
            defaults={'tasks': tasks_data, 'created_at': timezone.now(), 'updated_at': timezone.now()}
        )

        if created:
            # If the routine is newly created, update the in_routine field for tasks
            task_ids = [task['id'] for task in tasks_data]
            Task.objects.filter(id__in=task_ids).update(in_routine=True)
            return routine
        else:
            # If routine already exists, call update method
            return self.update(routine, validated_data)

    
    def update(self, instance, validated_data):
        """
        Update the Routine instance and handle the `in_routine` field of tasks.
        """
        old_task_ids = [task['id'] for task in instance.tasks]  # IDs of tasks currently in the routine
        new_task_ids = [task['id'] for task in validated_data['tasks']]  # IDs of tasks in the updated routine

        # Update the routine instance
        instance.tasks = validated_data['tasks']
        instance.updated_at = timezone.now()
        instance.save()

        # Update the `in_routine` field for tasks that are no longer in the routine
        tasks_to_remove = set(old_task_ids) - set(new_task_ids)
        if tasks_to_remove:
            Task.objects.filter(id__in=tasks_to_remove).update(in_routine=False)

        # Update the `in_routine` field for tasks that are newly added to the routine
        tasks_to_add = set(new_task_ids) - set(old_task_ids)
        if tasks_to_add:
            Task.objects.filter(id__in=tasks_to_add).update(in_routine=True)

        return instance