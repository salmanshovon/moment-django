from django.contrib import admin
from .models import Task, TaskCategory, PublicTask, PublicTaskCategory, ArchivedTask

@admin.register(PublicTaskCategory)
class PublicTaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'color')  # Added 'color'
    search_fields = ('title',)
    ordering = ('title',)

@admin.register(TaskCategory)
class UserTaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_category_title', 'custom_title', 'custom_description', 'custom_color', 'is_removed') #added color and removed TaskCategory as it does not exist.
    list_filter = ('user', 'is_removed')
    search_fields = ('user__username', 'category__title', 'custom_title')

    def get_category_title(self, obj):
        if obj.category:
            return obj.category.title
        return None
    get_category_title.short_description = 'Public Category Title'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'title',
        'user',
        'priority',
        'category',
        'due_date',
        'is_repetitive',
        'frequency_display',  # Custom method for frequency display
        'notification_days',
        'is_active',
        'created_at',
        'duration_display',  # Custom method for duration display
    )

    # Fields to filter the list by
    list_filter = (
        'user',
        'priority',
        'category',
        'is_repetitive',
        'is_active',
        'due_date',
    )

    # Fields to search in the admin panel
    search_fields = (
        'title',
        'user__username',  # Search by username
        'description',     # Search by task description
        'category__name',  # Search by category name
    )

    # Default ordering of tasks
    ordering = ('-created_at',)

    # Date hierarchy for easy navigation by date
    date_hierarchy = 'created_at'

    # Group fields in the edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'priority', 'category', 'task_merit'),
        }),
        ('Scheduling Information', {
            'fields': ('due_date', 'due_time', 'is_repetitive', 'frequency_interval', 'notification_days'),
        }),
        ('Task Settings', {
            'fields': ('is_active', 'in_routine', 'duration'),
        }),
    )

    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')

    # Custom methods for display
    def frequency_display(self, obj):
        """Display frequency in a more readable format."""
        if obj.is_repetitive:
            if obj.frequency_interval == 30:
                return "Monthly"
            elif obj.frequency_interval == 365:
                return "Yearly"
            return f"Every {obj.frequency_interval} days"
        return "One-Time"
    frequency_display.short_description = "Frequency"

    def duration_display(self, obj):
        """Display duration in a more readable format."""
        return f"{obj.duration} minutes"
    duration_display.short_description = "Duration"

    # Optimize database queries
    def get_queryset(self, request):
        """Customize the queryset to optimize performance."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'category')

    # Custom action for bulk activation/deactivation
    actions = ['activate_tasks', 'deactivate_tasks']

    def activate_tasks(self, request, queryset):
        """Bulk activate selected tasks."""
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} tasks activated successfully.")
    activate_tasks.short_description = "Activate selected tasks"

    def deactivate_tasks(self, request, queryset):
        """Bulk deactivate selected tasks."""
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} tasks deactivated successfully.")
    deactivate_tasks.short_description = "Deactivate selected tasks"


@admin.register(PublicTask)
class PublicTaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'description', 'priority', 'category', 'task_merit', 'is_repetitive', 'frequency_interval', 'notification_days'
    )
    list_filter = (
        'priority', 'category', 'is_repetitive'
    )
    search_fields = ('title', 'description')
    ordering = ('title',)


@admin.register(ArchivedTask)
class ArchivedTaskAdmin(admin.ModelAdmin):
    # Fields to display in the list view of the admin panel
    list_display = (
        'title',
        'user',
        'priority',
        'due_date',
        'is_repetitive',
        'archived_at',
    )

    # Fields to filter the list by
    list_filter = (
        'priority',
        'due_date',
        'is_repetitive',
        'archived_at',
    )

    # Fields to search in the admin panel
    search_fields = (
        'title',
        'user__username',  # Search by username of the user
        'description',
    )

    # Fields to group in the edit form
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description', 'priority', 'category', 'task_merit')
        }),
        ('Timing Information', {
            'fields': ('created_at', 'updated_at', 'due_date', 'due_time', 'archived_at'),
        }),
        ('Task Settings', {
            'fields': ('is_repetitive', 'frequency_interval', 'notification_days', 'is_active', 'in_routine'),
        }),
    )

    # Read-only fields (cannot be edited in the admin panel)
    readonly_fields = (
        'created_at',
        'updated_at',
        'archived_at',
    )

    # Automatically populate the user field based on the logged-in admin user
    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)