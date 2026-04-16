from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from seller.models import SellerProfile


@receiver(pre_save, sender=SellerProfile)
def capture_previous_seller_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return

    previous = sender.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
    instance._previous_status = previous


@receiver(post_save, sender=SellerProfile)
def notify_seller_status_change(sender, instance, created, **kwargs):
    if created:
        return

    previous_status = getattr(instance, "_previous_status", None)
    if previous_status == instance.status:
        return

    if instance.status == "APPROVED":
        subject = "Your ShoppyO seller account has been approved"
        message = (
            f"Hi {instance.user.first_name or instance.store_name},\n\n"
            "Your seller account has been approved. You can now sign in and start managing your store on ShoppyO.\n\n"
            "Regards,\nShoppyO Team"
        )
    elif instance.status == "REJECTED":
        subject = "Your ShoppyO seller account status update"
        message = (
            f"Hi {instance.user.first_name or instance.store_name},\n\n"
            "Your seller account has been reviewed and is currently rejected. "
            "Please contact support or update your submitted details if needed before trying again.\n\n"
            "Regards,\nShoppyO Team"
        )
    else:
        return

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [instance.user.email],
        fail_silently=True,
    )
