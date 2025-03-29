from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from tasks.models import Task, PublicTask
from routines.models import Routine, Notification
from .serializers import TaskDetails, TaskList, UserSettingsSerializer, RoutineSerializer, NotificationSerializer, NotificationUpdateSerializer, PublicTaskList, PublicTaskToTaskSerializer
from users.models import UserSettings
from django.contrib.auth.models import User
from django.utils import timezone
from itertools import chain


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
        
        # Determine the target date based on the 'param' value
        if param == 'true':
            target_date = timezone.now().date()  # Today's date
        elif param == 'false':
            target_date = timezone.now().date() + timezone.timedelta(days=1)  # Tomorrow's date
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
        today = timezone.now().date()
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
        print(self.request.data)
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