from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from allauth.account.utils import user_username
# from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        This method is called before logging in a user via a social account.
        It ensures that a user with the same email exists or creates one.
        """

        email = sociallogin.account.extra_data.get("email")
        first_name = sociallogin.account.extra_data.get("given_name", "")  # First Name
        last_name = sociallogin.account.extra_data.get("family_name", "")  # Last Name
        dp = sociallogin.account.extra_data.get("picture", "")  # Display Picture

        if not email:
            return  # Google did not provide an email, let allauth handle this error

        # Check if user with this email already exists
        user = User.objects.filter(email=email).first()

        if user:
            sociallogin.connect(request, user)
        else:
            # Create a new user with a unique username
            username = self.generate_unique_username(email)
            user = User.objects.create(email=email, username=username)
            user.set_unusable_password()  # Social accounts don’t need passwords

            # Save user and connect the social login to this user
            user.save()
            sociallogin.connect(request, user)

        # Mark Profile as verified
        if hasattr(user, "profile"):
            if not user.profile.is_updated:
                user.profile.full_name = f"{first_name} {last_name}".strip()
            
            if dp and not user.profile.picture:
                user.profile.picture = dp
            user.profile.is_verified = True
            user.profile.save()

    def generate_unique_username(self, email):
        """Generate a unique username based on the email address."""
        base_username = email.split("@")[0]
        username = base_username

        while User.objects.filter(username=username).exists():
            random_suffix = "".join(random.choices(string.digits, k=4))
            username = f"{base_username}{random_suffix}"

        return username
