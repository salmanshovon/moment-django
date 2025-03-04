from rest_framework import serializers
from tasks.models import Task
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