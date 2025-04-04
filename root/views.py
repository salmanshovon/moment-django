from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect
import json
from .utils import send_contact_email_to_admin
from django.http import JsonResponse



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

class ContactUsView(TemplateView):
    template_name='contact_us.html'

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, self.template_name)
        return render(request, 'rootbase.html')
    
class ContactMailSendView(View):

    def post(self, request, *args, **kwargs):
        """Handle contact form submission with CSRF validation"""
        try:
            data = json.loads(request.body)
            name = data.get("name")
            email = data.get("email")
            message = data.get("message")

            # Validate required fields
            if not all([name, email, message]):
                return JsonResponse({
                    "success": False, 
                    "error": "Name, email, and message are required"
                }, status=400)

            # Send email using utility function
            success, error = send_contact_email_to_admin(name, email, message)
            
            if not success:
                return JsonResponse({
                    "success": False, 
                    "error": error or "Failed to send email"
                }, status=500)

            return JsonResponse({"success": True})

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False, 
                "error": "Invalid JSON format"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "success": False, 
                "error": f"Server error: {str(e)}"
            }, status=500)