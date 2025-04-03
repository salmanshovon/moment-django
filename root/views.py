from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect


class TnCView(TemplateView):
    template_name='tnc.html'

class PrivacyPolicyView(TemplateView):
    template_name='privacy_policy.html'

class RootView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # Replace 'home' with your actual home URL name
        
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'landing.html')

        return render(request, 'rootbase.html')
    
class OfflineView(TemplateView):
    template_name='offline.html'

class FeaturesView(TemplateView):
    template_name='features.html'

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, self.template_name)
        return render(request, 'rootbase.html')
    

class PriceView(TemplateView):
    template_name='pricing.html'

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, self.template_name)
        return render(request, 'rootbase.html')