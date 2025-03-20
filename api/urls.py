from django.urls import path
from .views import TaskListAPIView, TaskDetailAPIView, TaskDeleteAPIView, UpdateSortPreferenceView, SchedulerTasksView, RoutineCreateUpdateView, RoutineDetailView, NotificationsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('task-list/', TaskListAPIView.as_view(), name='task_list'),
    path('task-detail/<int:pk>/', TaskDetailAPIView.as_view(), name='task_detail'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('task-delete/<int:pk>/', TaskDeleteAPIView.as_view(), name='delete_task'),
    path('update-sort/', UpdateSortPreferenceView.as_view(), name='update_sort'),
    path('get-scheduling-tasks', SchedulerTasksView.as_view(), name='get_sch_tasks'),
    path('routine-save/', RoutineCreateUpdateView.as_view(), name='routine_save'),
    path('routine-view/', RoutineDetailView.as_view(), name='routine_view'),
    path('notification/', NotificationsView.as_view(), name='get_notifications'),
]