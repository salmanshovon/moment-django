from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from tasks.models import Task
from .serializers import TaskDetails, TaskList, UserSettingsSerializer
from users.models import UserSettings
from django.contrib.auth.models import User


class SchedulerTasksView(generics.ListAPIView):
    serializer_class = TaskList
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get the user from the request (or from the URL parameter)
        user = self.request.user  # Assuming the user is authenticated
        # Use the static method `get_user_tasks` to fetch the tasks
        return Task.get_user_tasks(user)

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