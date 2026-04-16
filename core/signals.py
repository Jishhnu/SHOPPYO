try:
    import requests
    from allauth.socialaccount.signals import social_account_updated
except ImportError:
    requests = None
    social_account_updated = None

from django.core.files.base import ContentFile
from django.dispatch import receiver


if social_account_updated is not None:
    @receiver(social_account_updated)
    def save_google_data(request, sociallogin, **kwargs):
        user = sociallogin.user
        data = sociallogin.account.extra_data

        user.first_name = data.get("given_name", "")
        user.last_name = data.get("family_name", "")

        if data.get("email"):
            user.email = data["email"]

        image_url = data.get("picture")
        if image_url and requests is not None:
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    user.profile_image.save(
                        f"{user.username}/google.jpg",
                        ContentFile(response.content),
                        save=False,
                    )
            except Exception as exc:
                print("Image error:", exc)

        user.save()
