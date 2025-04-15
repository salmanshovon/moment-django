from rest_framework import generics, permissions, status
from rest_framework.generics import CreateAPIView, ListAPIView 
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from tasks.models import Task, PublicTask, ArchivedTask
from routines.models import Routine, Notification, RoutineTemplate
from .serializers import TaskDetails, TaskList, UserSettingsSerializer, RoutineSerializer, NotificationSerializer, NotificationUpdateSerializer, PublicTaskList, PublicTaskToTaskSerializer
from .serializers import RoutineTemplateSerializer, RoutineTemplateListSerializer, ArchivedTaskSerializer
from users.models import UserSettings
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from itertools import chain
from rest_framework.exceptions import NotFound
import pytz



class SchedulerTasksView(generics.ListAPIView):
    serializer_class = TaskList
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get the user from the request (or from the URL parameter)
        user = self.request.user  # Assuming the user is authenticated
        param = self.request.GET.get('param', 'true')  # Get param as a string
        # Use the static method `get_user_tasks` to fetch the tasks
        param = param.lower() == 'true'  # True if 'true', False if 'false'
        return Task.get_user_tasks(user, param=param)
    
class TemplateTasksView(generics.ListAPIView):
    serializer_class = TaskList
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.get_repetitive_tasks(user)

class TaskListAPIView(generics.ListAPIView):
    serializer_class = TaskList
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retrieve the user's sort preference
        sort_criteria = self.request.user.usersettings.sort

        # Get the base queryset filtered by the logged-in user and active tasks
        queryset = Task.objects.filter(user=self.request.user, is_active=True)

        # Check if a search query is provided
        search_query = self.request.query_params.get('q', None)
        if search_query:
            # Filter tasks based on the search query
            queryset = queryset.filter(
                Q(title__icontains=search_query) |  # Search by title
                Q(description__icontains=search_query)  # Search by description
            )

        # Apply sorting based on the criteria
        if sort_criteria == 'priority':
            queryset = queryset.order_by('-priority')
        elif sort_criteria == 'due_date':
            queryset = queryset.order_by('due_date', 'due_time')  # Sort by date and time
        elif sort_criteria == 'duration':
            queryset = queryset.order_by('duration')
        elif sort_criteria == 'task_merit':
            queryset = queryset.order_by('-task_merit')  # Sort by merit score (descending)
        elif sort_criteria == 'added':
            queryset = queryset.order_by('-created_at')  # Sort by creation date (descending)
        elif sort_criteria == 'updated_at':
            queryset = queryset.order_by('-updated_at')  # Sort by last updated date (descending)
        elif sort_criteria == 'title':
            queryset = queryset.order_by('title')
        else:
            # Default sorting by priority
            queryset = queryset.order_by('-priority')

        return queryset

class TaskDetailAPIView(generics.RetrieveAPIView):
    serializer_class = TaskDetails
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return tasks only for the logged-in user
        return Task.objects.filter(user=self.request.user)


class TaskDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object() #uses get_queryset and pk from url
        self.perform_destroy(instance)
        return Response({'message': 'Task deleted successfully!'},status=status.HTTP_200_OK)
    

class RtnTemplateDeleteAPIView(generics.DestroyAPIView):
    permissions_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RoutineTemplate.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Template deleted successfully!'},status=status.HTTP_200_OK)

class UpdateSortPreferenceView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    def post(self, request):
        # Get or create UserSettings for the current user
        user_settings, created = UserSettings.objects.get_or_create(user=request.user)

        # Update the sort preference
        serializer = UserSettingsSerializer(user_settings, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response({'success': False},serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RoutineCreateUpdateView(generics.CreateAPIView):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Save the routine with the current authenticated user.
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Override the create method to return a custom success response.
        """
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Routine saved successfully!", "routine": response.data},
            status=status.HTTP_201_CREATED
        )
    

class RoutineDetailView(APIView):
    serializer_class = RoutineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get the user from the request (or from the URL parameter)
        user = request.user  # Assuming the user is authenticated
        param = request.GET.get('param', 'true')  # Get param as a string
        
        profile = self.request.user.profile
        user_tz = pytz.timezone(profile.user_timezone) if profile.user_timezone else pytz.UTC
        
        # Determine the target date based on the 'param' value
        if param == 'true':
            target_date = timezone.localtime(timezone.now(), user_tz).date()
        elif param == 'false':
            target_date = timezone.localtime(timezone.now(), user_tz).date() + timezone.timedelta(days=1)  # Tomorrow's date
        else:
            # Handle invalid 'param' values
            raise ValueError("Invalid 'param' value. It must be 'true' or 'false'.")
        
        # Fetch the routine for the user and target date
        routine = Routine.objects.filter(user=user, for_date=target_date).first()

        # Return serialized routine if found, otherwise return null
        if routine:
            serializer = RoutineSerializer(routine)
            return Response(serializer.data, status=200)
        else:
            return Response(3, status=200)  # Return null in JSON format

class TimelineView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the authenticated user
        profile = self.request.user.profile
        user_tz = pytz.timezone(profile.user_timezone) if profile.user_timezone else pytz.UTC
        today = timezone.localtime(timezone.now(), user_tz).date()
        tomorrow = today + timezone.timedelta(days=1)

        # Fetch routines for today and tomorrow
        routines = Routine.objects.filter(user=user, for_date__in=[today, tomorrow])

        # Serialize the routines
        if routines.exists():
            tasks = list(chain.from_iterable(routine.tasks for routine in routines))
            # serializer = TimelineSerializer(routines, many=True)
            return Response(tasks, status=200)
        else:
            return Response([], status=200)  # Return an empty list if no routines exist

class NotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.get_user_notifications(user)

class NotificationUpdateView(generics.GenericAPIView):
    serializer_class = NotificationUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        # print(self.request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification_ids = serializer.validated_data['notification_ids']
        is_read = serializer.validated_data.get('is_read')
        is_generated = serializer.validated_data.get('is_generated')

        notifications = Notification.objects.filter(id__in=notification_ids)

        if notifications.count() != len(notification_ids):
            return Response({"error": "One or more notification IDs not found."}, status=status.HTTP_400_BAD_REQUEST)

        for notification in notifications:
            if is_read is not None:
                notification.is_read = is_read
            if is_generated is not None:
                notification.is_generated = is_generated
            notification.save()

        return Response({"message": "Notifications updated successfully."}, status=status.HTTP_200_OK)
    

class PublicTaskListAPIView(generics.ListAPIView):
    serializer_class = PublicTaskList
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get the base queryset
        queryset = PublicTask.objects.all()
        
        # Get titles of tasks to exclude (user's repetitive active tasks)
        exclude_titles = Task.objects.filter(
            user=self.request.user,
            is_repetitive=True,  # Fixed typo: was 'is_repeptitive'
        ).values_list('title', flat=True)  # Get just the titles

        # Exclude tasks with matching titles
        if exclude_titles:
            queryset = queryset.exclude(title__in=exclude_titles)

        # Handle search query
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
                
        return queryset.order_by('title')
    
class BulkCreateTasksFromPublicTasks(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = PublicTaskToTaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            tasks = serializer.save()
            return Response({"message": f"{len(tasks)} tasks added successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RoutineTemplateCreateView(CreateAPIView):
    queryset = RoutineTemplate.objects.all()
    serializer_class = RoutineTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            template_name = serializer.validated_data.get('template_name')
            user = request.user

            if template_name:
                base_name = template_name
                count = 0
                while RoutineTemplate.objects.filter(user=user, template_name=template_name).exists():
                    count += 1
                    template_name = f"{base_name} {count}"

                serializer.validated_data['template_name'] = template_name
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"error": "Template name is required."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RoutineTemplateUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, template_id):
        """
        Fully update a RoutineTemplate by its ID.
        """
        template = get_object_or_404(RoutineTemplate, id=template_id, user=request.user)
        serializer = RoutineTemplateSerializer(template, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(taskCount=len(serializer.validated_data.get('tasks', [])))
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class RoutineTemplateListView(generics.ListAPIView):
    serializer_class = RoutineTemplateListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only templates belonging to the authenticated user
        return RoutineTemplate.objects.filter(user=self.request.user)
    

class RoutineTemplateDetailView(generics.RetrieveAPIView):
    queryset = RoutineTemplate.objects.all()
    serializer_class = RoutineTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Restrict queryset to templates owned by the requesting user."""
        return self.queryset.filter(user=self.request.user)

    def get_object(self):
        """Override to raise NotFound if the object doesn't belong to the user."""
        try:
            obj = self.get_queryset().get(id=self.kwargs['pk'])
        except RoutineTemplate.DoesNotExist:
            raise NotFound("RoutineTemplate not found.")
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Get mapping of task IDs to their due dates
        task_due_date_map = Task.get_repetitive_task_due_date_map(request.user)
        
        # Update each task's due_date if it exists in the map
        updated_tasks = []
        for task in data['tasks']:
            task_id = task.get('id')
            if task_id in task_due_date_map:
                # Only update the due_date, keep all other fields the same
                updated_task = {**task}  # Create a copy
                updated_task['due_date'] = task_due_date_map[task_id].strftime('%Y-%m-%d')
                updated_tasks.append(updated_task)
            else:
                # Keep task as-is if not found in repetitive tasks
                updated_tasks.append(task)
        
        data['tasks'] = updated_tasks
        return Response(data)
    

class ArchivedTaskPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArchivedTaskListView(generics.ListAPIView):
    serializer_class = ArchivedTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ArchivedTaskPagination

    def get_queryset(self):
        # Base queryset - user's archived tasks
        queryset = ArchivedTask.objects.filter(user=self.request.user)
        
        # Handle search query
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query))
        
        return queryset.order_by('-archived_at')  # Newest first

#For irrigation (Temporary)
from .serializers import IrrigateBasicSerializer
from routines.models import Irrigate

class IrrigateSettingsAPI(generics.RetrieveAPIView):
    """API to serve only time and command fields and update update_time on each request"""
    serializer_class = IrrigateBasicSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        obj, _ = Irrigate.objects.get_or_create(pk=1)
        obj.update_time = timezone.now()  # Update the timestamp
        obj.save(update_fields=['update_time'])  # Save only the update_time field
        return obj

class NodeMCUAckAPI(APIView):
    """API for NodeMCU to send acknowledgment"""
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        irrigate = Irrigate.objects.filter(pk=1).first()
        if not irrigate:
            return Response({"status": "error", "message": "No irrigation settings found"}, status=404)
        
        # Update action_time and reset command
        irrigate.action_time = timezone.now()
        irrigate.command = False
        irrigate.save()
        
        return Response({"status": "success", "message": "Acknowledgment received"})
    
# ------------------------------------------------------------------------------------------temporary zone ends------------------------------