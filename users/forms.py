from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class SignInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username_or_email = self.cleaned_data.get("username")

        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                return user.username  # Convert email to username
            except User.DoesNotExist:
                return username_or_email  # Return as is if no user found
        
        return username_or_email  # Return username as is
    

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'date_of_birth', 'gender', 'occupation']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=[('', 'Select'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]),
        }