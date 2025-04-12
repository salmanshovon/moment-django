from django import forms
from .models import Task, TaskCategory
from datetime import datetime

class TaskCategoryForm(forms.ModelForm):
    class Meta:
        model = TaskCategory
        fields = ['custom_title', 'custom_description']

# Common choices for frequency interval
FREQUENCY_INTERVAL_CHOICES = [
    (1, "Daily"),
    (7, "Weekly"),
    (30, "Monthly"),
    (365, "Yearly"),
    ("custom", "Custom"),
]

class OneTimeTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "priority",
            "category",
            "task_merit",
            "due_date",
            "due_time",
            "duration",
            "notification_days",
        ]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "due_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Get request from kwargs
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # Extract data from the form
        due_time = self.data.get('due_time')
        duration_minutes = self.data.get('duration')
        priority = self.data.get('priority')
        task_merit = self.data.get('task_merit')


        # Validate time (due_time)
        if due_time:
            try:
                datetime.strptime(due_time, "%H:%M")  # Validate 24-hour format
                cleaned_data['due_time'] = due_time  # Add due_time to cleaned_data
            except ValueError:
                self.add_error('due_time', "Invalid time format. Use HH:MM in 24-hour format.")
        else:
            self.add_error('due_time', "This field is required.")

        # Validate duration (duration_minutes)
        if duration_minutes:
            try:
                duration_minutes = int(duration_minutes)
                if duration_minutes <= 0:
                    self.add_error('duration', "Duration must be a positive integer.")
                else:
                    cleaned_data['duration'] = duration_minutes  # Add duration to cleaned_data
            except ValueError:
                self.add_error('duration', "Duration must be a valid integer.")
        else:
            self.add_error('duration', "This field is required.")


        # Validate priority
        if priority:
            try:
                priority = int(priority)
                if priority <= 0:
                    self.add_error('priority', "Priority must be a positive integer.")
                else:
                    cleaned_data['priority'] = priority  # Add priority to cleaned_data
            except ValueError:
                self.add_error('priority', "Priority must be a valid integer.")
        else:
            self.add_error('priority', "This field is required.")

        # Validate task merit
        if task_merit:
            try:
                task_merit = int(task_merit)
                if task_merit <= 0:
                    self.add_error('task_merit', "Task merit must be a positive integer.")
                else:
                    cleaned_data['task_merit'] = task_merit  # Add task_merit to cleaned_data
            except ValueError:
                self.add_error('task_merit', "Task merit must be a valid integer.")
        else:
            self.add_error('task_merit', "This field is required.")

        print(f"Updated cleaned_data: {cleaned_data}")
        return cleaned_data





class RepetitiveTaskForm(forms.ModelForm):
    frequency_interval = forms.ChoiceField(
        choices=FREQUENCY_INTERVAL_CHOICES,
        label="Frequency",
        widget=forms.Select(attrs={"id": "frequency-interval"}),
    )
    custom_frequency = forms.IntegerField(
        required=False,
        label="Custom Frequency (in days)",
        widget=forms.NumberInput(attrs={"id": "custom-frequency", "style": "display: none;"}),
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "priority",
            "category",
            "task_merit",
            "due_date",
            "duration",
            "frequency_interval",
            "notification_days",
        ]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


    def clean(self):
        print(self.data)
        cleaned_data = super().clean()

        frequency_interval = cleaned_data.get('frequency_interval')
        custom_frequency = self.data.get('custom_interval_number')

        # Convert custom_frequency to int if possible, otherwise None
        try:
            custom_frequency = int(custom_frequency)
        except (TypeError, ValueError):
            custom_frequency = None

        if frequency_interval == "custom":
            if not custom_frequency or custom_frequency <= 0:
                raise forms.ValidationError("Custom frequency must be a positive number.")
            cleaned_data['frequency_interval'] = custom_frequency
        else:
            try:
                cleaned_data['frequency_interval'] = int(frequency_interval)
            except (TypeError, ValueError):
                raise forms.ValidationError("Invalid frequency interval selected.")
        

        return cleaned_data

