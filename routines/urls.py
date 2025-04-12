from django.urls import path
from .views import SchedulerView, TimelineView, TemplateEditorView


urlpatterns = [
    path('scheduler/', SchedulerView.as_view(), name='scheduler'),
    path('timeline/', TimelineView.as_view(), name='timeline'),
    path('template-editor/', TemplateEditorView.as_view(), name='template_editor'),
]