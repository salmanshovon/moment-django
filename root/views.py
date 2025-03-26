from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect


class TnCView(TemplateView):
    template_name='tnc.html'

class RootView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # Replace 'home' with your actual home URL name
        return render(request, 'signin.html')
    
class OfflineView(TemplateView):
    template_name='offline.html'