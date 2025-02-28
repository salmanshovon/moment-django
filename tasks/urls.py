from django.urls import path
from .views import CreateTaskView, TaskView, EditTaskView


urlpatterns = [
    path('create_task/', CreateTaskView.as_view(), name='create_task'),
    path('view_task/', TaskView.as_view(), name="view_task"),
    path('edit_task/<int:task_id>/', EditTaskView.as_view(), name="edit_task")
]