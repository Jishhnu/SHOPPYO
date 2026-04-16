import random
from django.contrib.auth import get_user_model

try:
    from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
except ImportError:
    DefaultSocialAccountAdapter = object

def generate_otp():
    return str(random.randint(100000,999999))

class AutoConnectSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If the social account is already linked, do nothing
        if sociallogin.is_existing:
            return
            
        # Check if a local user already exists with this email
        User = get_user_model()
        email = sociallogin.user.email
        if email:
            try:
                existing_user = User.objects.get(email=email)
                sociallogin.connect(request, existing_user) # Automatically link and login
            except User.DoesNotExist:
                pass
