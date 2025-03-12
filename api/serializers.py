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
        Create a new Routine instance if one does not exist for the given for_date.
        """
        user = self.context['request'].user
        for_date = validated_data['for_date']

        # Check if a routine already exists for the given date and user
        routine, created = Routine.objects.get_or_create(
            user=user,
            for_date=for_date,
            defaults={
                'tasks': validated_data['tasks'],
                'created_at': timezone.now(),
                'updated_at': timezone.now(),
            }
        )

        # If the routine already exists, update it
        if not created:
            routine.tasks = validated_data['tasks']
            routine.updated_at = timezone.now()
            routine.save()

        return routine