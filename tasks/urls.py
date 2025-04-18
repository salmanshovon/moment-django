from django.urls import path
from .views import CreateTaskView, TaskView, EditTaskView, ImportTaskView, ArchivedTaskView


urlpatterns = [
    path('create_task/', CreateTaskView.as_view(), name='create_task'),
    path('view_task/', TaskView.as_view(), name="view_task"),
    path('edit_task/<int:task_id>/', EditTaskView.as_view(), name="edit_task"),
    path('import-tasks/', ImportTaskView.as_view(), name="import_task"),
    path('archived-tasks/', ArchivedTaskView.as_view(), name="archived_task"),
]