from rest_framework import serializers
from tasks.models import Task, PublicTask, TaskCategory, ArchivedTask
from routines.models import Routine, Notification, RoutineTemplate
from django.utils import timezone
from users.models import UserSettings, Profile
from django.contrib.auth.models import User
import pytz
from datetime import timedelta

from routines.models import Irrigate


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
    
class PublicTaskList(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = PublicTask
        fields = [
            'id', 'title', 'priority', 'category', 'duration', 'is_repetitive', 'frequency_interval', 'color', 'task_merit', 
            'notification_days', 'description'
        ]

    def get_category(self, obj):
        """
        Returns the category title if the task has a category.
        """
        if obj.category:
            return obj.category.title
        return None  # If no category is assigned

    def get_color(self, obj):
        """
        Returns the category color if the task has a category, otherwise returns a default color.
        """
        if obj.category:
            return obj.category.color or '#FFFFFF'  # Use category color or default to white
        return '#FFFFFF'  # Default color if no category is found
    

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['sort']

class RoutineTemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutineTemplate
        fields = ('id', 'template_name', 'taskCount')

class RoutineTemplateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RoutineTemplate
        fields = ['id', 'user', 'template_name', 'tasks', 'taskCount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'taskCount', 'created_at', 'updated_at']

    def validate_tasks(self, value):
        """
        Validate the 'tasks' field to ensure it contains the required structure.
        Each task should be a dictionary with 'start_time', 'id', and 'is_fixed'.
        """
        for task in value:
            required_keys = ['start_time', 'id', 'is_fixed']
            if not isinstance(task, dict):
                raise serializers.ValidationError("Each task in the template must be a dictionary.")
            if not all(key in task for key in required_keys):
                raise serializers.ValidationError(
                    f"Each task in the template must contain: {', '.join(required_keys)}."
                )
        return value

    def create(self, validated_data):
        """
        Override the create method to automatically set the user and taskCount.
        """
        validated_data['user'] = self.context['request'].user
        validated_data['taskCount'] = len(validated_data.get('tasks', []))
        return super().create(validated_data)


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

class NotificationUpdateSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(child=serializers.IntegerField())
    is_read = serializers.BooleanField(required=False)
    is_generated = serializers.BooleanField(required=False)

    def validate(self, data):
        notification_ids = data.get('notification_ids', [])
        is_read = data.get('is_read')
        is_generated = data.get('is_generated')

        if not notification_ids:
            raise serializers.ValidationError("notification_ids are required.")

        if is_read is None and is_generated is None:
            raise serializers.ValidationError("Either is_read or is_generated must be provided.")

        return data
    

class PublicTaskToTaskSerializer(serializers.Serializer):
    public_task_ids = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        public_task_ids = validated_data['public_task_ids']

        # Fetch the user and their categories in one query
        user = self.context['request'].user
        user_categories = TaskCategory.get_categories(user)
        user_categories_dict = {cat['title']: cat['id'] for cat in user_categories}

        # Fetch all PublicTask objects in one query
        public_tasks = PublicTask.objects.filter(id__in=public_task_ids).select_related('category')

        profile = Profile.objects.filter(user=user).first()
        user_tz = pytz.timezone(profile.user_timezone) if profile.user_timezone else pytz.UTC
        

        # Calculate tomorrow's date
        tomorrow = timezone.localtime(timezone.now(), user_tz).date() + timedelta(days=1)


        tasks_to_create = []
        for public_task in public_tasks:
            category_title = public_task.category.title if public_task.category else None
            category_id = user_categories_dict.get(category_title) if category_title else None

            task_data = {
                'user': user,
                'title': public_task.title,
                'description': public_task.description,
                'priority': public_task.priority,
                'category_id': category_id,
                'task_merit': public_task.task_merit,
                'duration': public_task.duration,
                'is_repetitive': public_task.is_repetitive,
                'frequency_interval': public_task.frequency_interval,
                'notification_days': public_task.notification_days,
                'due_date': tomorrow,  # Set due_date as tomorrow
                'is_active': True,
                'in_routine': False,
            }

            tasks_to_create.append(Task(**task_data))

        # Bulk create all tasks in one query
        Task.objects.bulk_create(tasks_to_create)
        return tasks_to_create
    

class ArchivedTaskSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = ArchivedTask
        fields = [
            'id',
            'title',
            'description',
            'priority',
            'category',
            'color',
            'task_merit',
            'created_at',
            'updated_at',
            'duration',
            'due_date',
            'due_time',
            'is_repetitive',
            'frequency_interval',
            'notification_days',
            'archived_at'
        ]
        read_only_fields = fields  # All fields are read-only for archived tasks

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
    

#Temporary 2 serializers for irrigation:
class IrrigateBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Irrigate
        fields = ['time', 'command']

# ----------------------------------------------------------temporary zone ends------------------------------