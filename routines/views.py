from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View


@method_decorator(login_required(login_url="signin"), name="dispatch")
class SchedulerView(View):
    template_name = 'routines/scheduler.html'

    def get(self, request, *args, **kwargs):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, self.template_name)
        return render(request, "dashbase.html")
    
@method_decorator(login_required(login_url="signin"), name="dispatch")
class TimelineView(View):
    template_name = 'routines/timeline.html'

    def get(self, request, *args, **kwargs):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, self.template_name)
        return render(request, "dashbase.html")