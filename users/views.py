from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, View, UpdateView, DetailView
from django.contrib.auth.views import LoginView
from .forms import SignUpForm, SignInForm, ProfileUpdateForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages
import json
from .utils import send_email_otp, verify_otp, update_password, get_timezone_from_ip
from .models import Profile

def not_authenticated(user):
    return not user.is_authenticated

@method_decorator(user_passes_test(not_authenticated, login_url='home'), name='dispatch')
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup_main.html'
    success_url = reverse_lazy('signin')

    def get(self, request, *args, **kwargs):
        """Handle AJAX requests."""
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return super().get(request, *args, **kwargs)
        return render(request, 'rootbase.html')

    def form_valid(self, form):
        """Handle valid form submissions, specifically for AJAX requests."""
        print("Form is valid. Processing user registration...")

        is_ajax = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        print(f"Is AJAX request: {is_ajax}")

        user = form.save(commit=False)  # Don't save the user yet
        print(f"User object created: {user}")

        user.save()  # Save the user to the database
        print(f"User saved: {user.id}")

        Profile.objects.create(user=user, is_verified=False)  # Explicitly create the profile
        print(f"Profile created for user: {user.id}")

        send_email_otp(user)  # Send OTP
        print(f"OTP sent to: {user.email}")

        if is_ajax:
            response_data = {
                'success': True,
                'message': 'Account created successfully! Please check your email for verification.',
                'redirect_url': self.success_url  # Optionally, include the redirect URL
            }
            print("AJAX response:", response_data)
            return JsonResponse(response_data)
        else:
            messages.success(self.request, "Account created successfully! Sign in now.")
            return super().form_valid(form)  # Handle non-AJAX form submissions

    def form_invalid(self, form):
        """Handle invalid form submissions, specifically for AJAX requests."""
        print("Form is invalid. Errors:", form.errors)

        is_ajax = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        print(f"Is AJAX request: {is_ajax}")

        if is_ajax:
            response_data = {
                'success': False,
                'errors': form.errors.get_json_data(),
                'message': 'Please correct the errors below.'
            }
            print("AJAX response:", response_data)
            return JsonResponse(response_data, status=400)
        else:
            return super().form_invalid(form)  # Handle non-AJAX form submissions


@method_decorator(user_passes_test(not_authenticated, login_url=reverse_lazy('home')), name='dispatch')
class SignInView(TemplateView):
    template_name = 'signin_main.html'
    success_url = reverse_lazy('update_profile')

    def get(self, request, *args, **kwargs):
        """Handle AJAX requests and 'isOut' parameter."""
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        is_out = request.headers.get('isOut')

        if is_ajax:
            if is_out:
                return super().get(request, *args, **kwargs)  # If isOut, send signin_main.html
            return render(request, 'logged_out.html')  # Default AJAX response
        
        return render(request, 'rootbase.html')  # If not AJAX, return rootbase.html
            

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if username and password:
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    # Get user's timezone from IP
                    user_timezone = get_timezone_from_ip(request) or "UTC"  # Default to UTC if not found
                    
                    # Update user's timezone in their profile
                    user.profile.user_timezone = user_timezone
                    user.profile.save()
                    login(request, user)
                    return JsonResponse({
                        "success": True,
                        "redirect_url": self.success_url
                    })
            
            return JsonResponse({
                "success": False, 
                "error": "Invalid username/email or password"
            }, status=400)
        
        # Fallback for non-AJAX requests
        return super().post(request, *args, **kwargs)


@method_decorator(user_passes_test(not_authenticated, login_url=reverse_lazy('home')), name='dispatch')
class PassResetView(TemplateView):
    template_name = 'passreset.html'



@method_decorator(login_required(login_url='signin'), name='dispatch')
class validateOTPView(TemplateView):
    template_name = 'validation.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.is_verified:
            if not request.user.profile.is_updated:
                return redirect('profile_update')
            else:
                return redirect('home')
        else:
            return super().dispatch(request, *args, **kwargs)  # Call the parent dispatch

class ResendOTPView(View):
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            send_email_otp(user)
            return JsonResponse({"message": "OTP resent successfully!"})
        
        except:
            data = json.loads(request.body)
            email = data.get('email')
            user = User.objects.filter(email=email).first()
            send_email_otp(user)
            return JsonResponse({"message": "OTP resent successfully!"})
        



"""
This module contains the view for the home page of the Routine Manager application.
Classes:
    HomeView: A class-based view that handles the display of the home page.
HomeView:
    Methods:
        dispatch(request, *args, **kwargs): Handles the HTTP request and determines the response based on user verification and request type.
    Decorators:
        @method_decorator(login_required(login_url='signin'), name='dispatch'): Ensures that the user is logged in before accessing the home page.
    Attributes:
        template_name (str): The name of the template to be rendered.
    dispatch(request, *args, **kwargs):
        - If the user is not verified, redirects to the 'validate_otp' page.
        - If the request is an XMLHttpRequest, renders the 'home.html' template.
        - If the request is not an XMLHttpRequest, renders the 'test.html' template, which contains in-page AJAX code to request and serve the real template via XMLHttpRequest.
Note:
    The purpose of this approach is to load the main base template first, which remains unchanged after the site is loaded. The dynamic parts of the page are requested and served through XMLHttpRequest to enhance performance and user experience.
"""
@method_decorator(login_required(login_url='signin'), name='dispatch')
class HomeView(TemplateView):
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_verified:
            return redirect('validate_otp')
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, self.template_name)
        else:
            return render(request, 'dashbase.html')
    

def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_unique': not User.objects.filter(username=username).exists()
    }
    return JsonResponse(data)

def check_email(request):
    email = request.GET.get('email', None)
    data = {
        'is_unique': not User.objects.filter(email=email).exists()
    }
    return JsonResponse(data)


def check_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        otp = data.get('otp')
        if 'email' in data:
            email = data.get('email')
            user = User.objects.filter(email=email).first()
            if verify_otp(user, otp):
                return JsonResponse({"success": True})
            return JsonResponse({"success": False, "error": "Invalid OTP"})
        else:
            if verify_otp(request.user, otp):
                return JsonResponse({"success": True})
            return JsonResponse({"success": False, "error": "Invalid OTP"})


@method_decorator(login_required(login_url='signin'), name='dispatch')
class ChangeEmailView(View):

    def post(self, request, *args, **kwargs):
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            new_email = data.get('new_email')

            # Validate the new email address
            if not new_email:
                return JsonResponse({"success": False, "error": "Email address is required."})

            # Check if the email is already in use
            if User.objects.filter(email=new_email).exists():
                return JsonResponse({"success": False, "error": "This email address is already in use."})

            # Update the user's email address
            user = request.user
            user.email = new_email
            user.save()

            # Send a new OTP to the updated email address
            send_email_otp(user)

            return JsonResponse({"success": True})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON data"})
        

def reset_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        user = User.objects.filter(email=email).first()
        if update_password(user, password):
            return JsonResponse({"success": True})



def check_and_passreset(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email", "").strip()

            if not email:
                return JsonResponse({"success": False, "error": "Email field is required."}, status=400)

            if not User.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "error": "This email address is not associated with any account."}, status=404)
            else:
                user = User.objects.get(email=email)

                # Generate a 6-digit OTP and send it to the user's email
                send_email_otp(user)
                return JsonResponse({"success": True, "message": "OTP has been sent to your email."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format."}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)



# Following View is for updating the profile at the first time after signup
@method_decorator(login_required(login_url='signin'), name='dispatch')
class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = "profile_update.html"  
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_verified:
            return redirect('validate_otp')
        elif request.user.profile.is_updated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Ensure the user can only update their own profile"""
        return self.request.user.profile

    def form_valid(self, form):
        """Handle the form submission if valid"""
        form.save()
        self.request.user.profile.is_updated = True
        return super().form_valid(form)

    def form_invalid(self, form):
        """If the form is invalid, return the same page with errors"""
        return self.render_to_response(self.get_context_data(form=form))
    

# Following View is for editing profile later on
@method_decorator(login_required(login_url='signin'), name='dispatch')
class ProfileEdit(UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = "profile_view_update.html"
    success_url = reverse_lazy('profile')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()  # Get the profile object
        form = self.get_form()  # Get the form instance
        context = self.get_context_data(object=self.object, form=form)  # Prepare context

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, self.template_name, context)
        return render(request, 'dashbase.html', context)

    def get_object(self, queryset=None):
        """Ensure the user can only update their own profile"""
        return self.request.user.profile

    def form_valid(self, form):
        """Handle successful form submission"""
        form.save()
        self.request.user.profile.is_updated = True
        return JsonResponse({'success': True, 'message': 'Profile updated successfully!'})

    def form_invalid(self, form):
        """Return form errors if invalid"""
        return JsonResponse({'success': False, 'errors': form.errors})



# Following View is for Viewing the Profile
@method_decorator(login_required(login_url='signin'), name='dispatch')
class ProfileView(DetailView):
    model = Profile
    template_name = 'profile_view.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Ensure the user can only view their own profile"""
        return self.request.user.profile
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, self.template_name, context)
        return render(request, 'dashbase.html', context)
    

class SecurityView(TemplateView):
    template_name = 'security.html'
