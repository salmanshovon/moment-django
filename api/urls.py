from django.urls import path
from .views import TaskListAPIView, TaskDetailAPIView, TaskDeleteAPIView, UpdateSortPreferenceView, SchedulerTasksView, RoutineCreateUpdateView, RoutineDetailView, NotificationsView, NotificationUpdateView, PublicTaskListAPIView, BulkCreateTasksFromPublicTasks
from .views import TimelineView, RoutineTemplateCreateView, RoutineTemplateListView, RoutineTemplateDetailView, RtnTemplateDeleteAPIView, TemplateTasksView, RoutineTemplateUpdateView, ArchivedTaskListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from .views import IrrigateSettingsAPI, NodeMCUAckAPI #For Irrigation Only

urlpatterns = [
    path('task-list/', TaskListAPIView.as_view(), name='task_list'),
    path('task-detail/<int:pk>/', TaskDetailAPIView.as_view(), name='task_detail'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('task-delete/<int:pk>/', TaskDeleteAPIView.as_view(), name='delete_task'),
    path('update-sort/', UpdateSortPreferenceView.as_view(), name='update_sort'),
    path('get-scheduling-tasks/', SchedulerTasksView.as_view(), name='get_sch_tasks'),
    path('routine-save/', RoutineCreateUpdateView.as_view(), name='routine_save'),
    path('routine-view/', RoutineDetailView.as_view(), name='routine_view'),
    path('notification/', NotificationsView.as_view(), name='get_notifications'),
    path('noti-update/', NotificationUpdateView.as_view(), name='update_notification'),
    path('pub-task-list/', PublicTaskListAPIView.as_view(), name='pub_task_list'),
    path('import-tasks/', BulkCreateTasksFromPublicTasks.as_view(), name='import_tasks'),
    path('timeline-view/', TimelineView.as_view(), name='timeline_api'),
    path('save-routine-template/', RoutineTemplateCreateView.as_view(), name='save_routine_template'),
    path('routine-template-list/', RoutineTemplateListView.as_view(), name='rtn_template_list'),
    path('get-routine-template/<int:pk>', RoutineTemplateDetailView.as_view(), name='get_routine_template'),
    path('template-delete/<int:pk>/', RtnTemplateDeleteAPIView.as_view(), name='delete_template'),
    path('get-template-tasks/', TemplateTasksView.as_view(), name='get_tmp_tasks'),
    path('update-template/<int:template_id>/', RoutineTemplateUpdateView.as_view(), name='update_template'),
    path('archived-task-list/', ArchivedTaskListView.as_view(), name='arc_task_list'),
    # temporary irrigation:
    path('ir-get/', IrrigateSettingsAPI.as_view(), name='irrigation-settings'),
    path('ir-put/', NodeMCUAckAPI.as_view(), name='nodemcu-ack'),
    # ----------------------------irrigation temporary zone ends----------------------
]