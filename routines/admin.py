from django.contrib import admin
from .models import RoutineTemplate, Routine, Reflection, Archive, Notification, Irrigate

@admin.register(RoutineTemplate)
class RoutineTemplateAdmin(admin.ModelAdmin):
    list_display = ('template_name', 'user', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at')
    search_fields = ('template_name', 'user__username')

@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ('user', 'for_date', 'created_at', 'updated_at')
    list_filter = ('user', 'for_date')
    search_fields = ('user__username', 'for_date')

@admin.register(Reflection)
class ReflectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'for_date', 'routine', 'created_at')
    list_filter = ('user', 'for_date')
    search_fields = ('user__username', 'for_date')

@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ('user', 'task_title', 'for_date', 'completion', 'created_at')
    list_filter = ('user', 'for_date', 'completion')
    search_fields = ('task_title', 'user__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'date_time', 'is_generated', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_generated', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'task', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('date_time', 'is_generated', 'is_read')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Irrigate)
class IrrigateAdmin(admin.ModelAdmin):
    list_display = ('time', 'command', 'action_time', 'update_time')
    list_filter = ('command', 'action_time')
    search_fields = ('time',)
    list_editable = ('command',)
    readonly_fields = ('update_time',)
    actions = ['toggle_command']

    fieldsets = (
        ('Irrigation Settings', {
            'fields': ('time', 'command')
        }),
        ('Timestamps', {
            'fields': ('action_time', 'update_time'),
            'classes': ('collapse',)
        }),
    )

    def toggle_command(self, request, queryset):
        """Custom admin action to toggle command status"""
        for obj in queryset:
            obj.command = not obj.command
            obj.save()
    toggle_command.short_description = "Toggle selected irrigation commands"