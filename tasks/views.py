from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from .forms import TaskCategoryForm, OneTimeTaskForm, RepetitiveTaskForm
from .models import Task, TaskCategory
from django.utils.decorators import method_decorator
import pytz
from datetime import datetime
from django.utils import timezone



@method_decorator(login_required(login_url="signin"), name="dispatch")
class CreateTaskView(View):
    template_name = "tasks/create_task.html"

    def get(self, request, *args, **kwargs):
        categories = TaskCategory.get_categories(user=request.user)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, self.template_name, {"categories": categories})
        return render(request, "dashbase.html")
    
    @staticmethod
    def set_default_notification_days(interval):
        """
        Set default notification days based on the task's frequency_interval.
        """
        if interval == 1:  # Daily
            notification_days = 1
        elif interval == 7:  # Weekly
            notification_days = 2
        elif interval == 30:  # Monthly
            notification_days = 5
        elif interval >= 365:  # Yearly
            notification_days = 30
        else:
            # For custom intervals, default to 1 day notification
            notification_days = 1
        return notification_days

    def post(self, request, *args, **kwargs):
        # print(request.POST)
        task_type = request.POST.get("task_type")  # Determine task type

        if task_type == "One-Time":
            form = OneTimeTaskForm(request.POST)
        elif task_type == "Repetitive":
            form = RepetitiveTaskForm(request.POST)
            
        else:
            return JsonResponse({"success": False, "errors": {"task_type": "Invalid task type"}}, status=400)

        if form.is_valid():
            task = form.save(commit=False)  # Don't save yet
            task.user = request.user  # Assign the user


            if task_type == "Repetitive":
                existing_task = Task.objects.filter(
                    user=request.user, title__iexact=task.title, is_repetitive=True
                ).exists()

                if existing_task:
                    form.add_error("title", "A repetitive task with this name already exists!")
                    return JsonResponse({"success": False, "errors": form.errors}, status=400)
                else:
                    task.is_repetitive = True

                if task.notification_days != 9999999999:
                    if task.frequency_interval < task.notification_days:
                        form.add_error(
                            "notification_days",
                            "Notification days cannot exceed the task frequency interval.",
                        )
                        return JsonResponse({"success": False, "errors": form.errors}, status=400)
                else:
                    task.notification_days = CreateTaskView.set_default_notification_days(task.frequency_interval)
            else:
                profile = self.request.user.profile
                user_tz = pytz.timezone(profile.user_timezone) if profile.user_timezone else pytz.UTC
                due_date = task.due_date
                current_date = timezone.localtime(timezone.now(), user_tz).date()
                if due_date < current_date:
                    form.add_error('due_date', "Task date must be today or in the future.")
                    return JsonResponse({"success": False, "errors": form.errors}, status=400) 
            task.save()
            return JsonResponse({"success": True, "message": "Task added successfully!"})

        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)



@method_decorator(login_required(login_url="signin"), name="dispatch")
class EditTaskView(View):
    template_name = "tasks/edit_task.html"

    def get(self, request, task_id, *args, **kwargs):
        task = get_object_or_404(Task, id=task_id, user=request.user)
        categories = TaskCategory.get_categories(user=request.user)
        durationHr = task.duration // 60
        durationMn = task.duration % 60

        if task.is_repetitive:
            form = RepetitiveTaskForm(instance=task)
        else:
            form = OneTimeTaskForm(instance=task)

        context = {
            "form": form,
            "task": task,
            "categories": categories,
            "duration_hours" : durationHr,
            "duration_minutes": durationMn
        }

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, self.template_name, context)
        return render(request, "dashbase.html", context)

    def post(self, request, task_id, *args, **kwargs):
        # print(request.POST)
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task_type = request.POST.get("task_type")  # Determine task type

        if task_type == "One-Time":
            form = OneTimeTaskForm(request.POST, instance=task)
        elif task_type == "Repetitive":
            form = RepetitiveTaskForm(request.POST, instance=task)
        else:
            return JsonResponse({"success": False, "errors": {"task_type": "Invalid task type"}}, status=400)

        if form.is_valid():
            updated_task = form.save(commit=False)
            updated_task.user = request.user  # Ensure the user remains the same

            if task_type == "Repetitive":
                existing_task = Task.objects.filter(
                    user=request.user, title__iexact=updated_task.title, is_repetitive=True
                ).exclude(id=task_id).exists()

                if existing_task:
                    form.add_error("title", "A repetitive task with this name already exists!")
                    return JsonResponse({"success": False, "errors": form.errors}, status=400)
                else:
                    updated_task.is_repetitive = True

                if task.notification_days != 9999999999:
                    if task.frequency_interval < task.notification_days:
                        form.add_error(
                            "notification_days",
                            "Notification days cannot exceed the task frequency interval.",
                        )
                        return JsonResponse({"success": False, "errors": form.errors}, status=400)
                else:
                    task.notification_days = CreateTaskView.set_default_notification_days(task.frequency_interval)
            else:
                profile = self.request.user.profile
                user_tz = pytz.timezone(profile.user_timezone) if profile.user_timezone else pytz.UTC
                due_date = task.due_date
                current_date = timezone.localtime(timezone.now(), user_tz).date()
                if due_date < current_date:
                    form.add_error('due_date', "Task date must be today or in the future.")
                    return JsonResponse({"success": False, "errors": form.errors}, status=400)
                updated_task.is_repetitive = False
            updated_task.save()
            return JsonResponse({"success": True, "message": "Task updated successfully!"})

        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)


@method_decorator(login_required(login_url="signin"), name="dispatch")
class TaskView(TemplateView):
    template_name = "tasks/view_task.html"

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, self.template_name)
        return render(request, 'dashbase.html')


class CreateCategoryView(View):
    def get(self, request):
        form = TaskCategoryForm()
        return render(request, 'create_category.html', {'form': form})

    def post(self, request):
        form = TaskCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
        return render(request, 'create_category.html', {'form': form}) # Re-render form with errors


@method_decorator(login_required(login_url="signin"), name="dispatch")
class ImportTaskView(View):
    template_name = "tasks/import_tasks.html"

    def get(self, request, *args, **kwargs):
        categories = TaskCategory.get_categories(user=request.user)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, self.template_name)
        return render(request, "dashbase.html")
    
@method_decorator(login_required(login_url="signin"), name="dispatch")
class ArchivedTaskView(View):
    template_name = "tasks/archived_task.html"

    def get(self, request, *args, **kwargs):
        categories = TaskCategory.get_categories(user=request.user)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, self.template_name)
        return render(request, "dashbase.html")