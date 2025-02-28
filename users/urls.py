from django.urls import path
from .views import SignUpView, SignInView, HomeView, check_username, check_email, ResendOTPView, check_otp, validateOTPView, ChangeEmailView, PassResetView, check_and_passreset, reset_password, ProfileUpdateView, ProfileView
from .views import ProfileEdit, ProfileView, SecurityView
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('logout/', LogoutView.as_view( next_page = 'signin'), name='logout'),
    path('home/', HomeView.as_view(), name='home'),
    path('check-username/', check_username, name='check_username'),
    path('check-email/', check_email, name='check_email'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('verify-otp/', check_otp, name='check_otp'),
    path('validate-otp/', validateOTPView.as_view(), name='validate_otp'),
    path('change-email/', ChangeEmailView.as_view(), name='change_email'),
    path('passreset/', PassResetView.as_view(), name='passreset'), #View for the password reset page
    path('check-and-passreset/', check_and_passreset, name='check_and_passreset'), #Order for checking email and sending OTP
    path('reset-password/', reset_password, name='reset_password'), #Order for resetting password
    path('update-profile/', ProfileUpdateView.as_view(), name='update_profile'), #View for updating profile initially
    path('profile-edit/', ProfileEdit.as_view(), name='profile_edit'), #View for editing the profile later
    path('profile/', ProfileView.as_view(), name='profile'), #View for viewing the profile
    path('security_update/', SecurityView.as_view(), name='security')
]