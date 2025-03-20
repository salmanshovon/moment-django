from django.contrib import admin
from .models import RoutineTemplate, Routine, Reflection, Archive, Notification

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