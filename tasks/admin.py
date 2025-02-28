from django.contrib import admin
from .models import Task, TaskCategory, PublicTask, PublicTaskCategory

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'user', 'priority', 'category', 'due_date', 'is_repetitive', 
        'frequency_interval', 'notification_days', 'is_active', 'created_at'
    )
    list_filter = ('user', 'priority', 'category', 'is_repetitive', 'is_active')
    search_fields = ('title', 'user__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        """Customize the queryset to optimize performance."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'category')

    def frequency_display(self, obj):
        """Display frequency in a more readable format."""
        if obj.is_repetitive:
            return f"Every {obj.frequency_interval} days"
        return "One-Time"
    frequency_display.short_description = "Frequency"


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', "description")
    list_filter = ('title','user',)
    search_fields = ('title', 'user__username')

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

@admin.register(PublicTaskCategory)
class PublicTaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)
    ordering = ('title',)
