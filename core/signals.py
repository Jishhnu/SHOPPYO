import requests
from django.core.files.base import ContentFile
from allauth.socialaccount.signals import social_account_updated
from django.dispatch import receiver

@receiver(social_account_updated)
def save_google_data(request, sociallogin, **kwargs):
    user = sociallogin.user
    data = sociallogin.account.extra_data

    # ✅ 1. Save Name
    user.first_name = data.get('given_name', '')
    user.last_name = data.get('family_name', '')

    # ✅ 2. Email (already saved by allauth, but safe)
    # user.email = data.get('email', user.email)
    if data.get('email'):
        user.email = data['email']

    # ✅ 3. Profile Image (URL → ImageField)
    image_url = data.get('picture')

    if image_url:
        try:
            response = requests.get(image_url)

            if response.status_code == 200:
                file_name = f"{user.username}/google.jpg"

                user.profile_image.save(
                    file_name,
                    ContentFile(response.content),
                    save=False
                )

        except Exception as e:
            print("Image error:", e)

    user.save()
    print("Signal Trigger")
    print("DATA",data)