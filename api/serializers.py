from rest_framework import serializers
from tasks.models import Task
from users.models import UserSettings

class TaskDetails(serializers.ModelSerializer):

    category = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'category', 'task_merit', 
            'created_at', 'updated_at', 'duration', 'due_date', 'due_time', 
            'is_repetitive', 'frequency_interval', 'notification_days', 'is_active'
        ]

    def get_category(self, obj):
        if obj.category:
            return obj.category.title  # Assuming your TaskCategory model has a 'title' field
        return None  # Or an appropriate default value if the category is null

class TaskList(serializers.ModelSerializer):

    category = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'priority', 'category', 'duration', 'is_repetitive', 'due_date', 'due_time', 'frequency_interval'
        ]

    def get_category(self, obj):
        if obj.category:
            return obj.category.title  # Assuming your TaskCategory model has a 'title' field
        return None  # Or an appropriate default value if the category is null
    

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['sort']