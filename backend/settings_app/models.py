import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PrivacySettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="privacysettings"
    )
    location_tracking_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Privacy Settings"
        verbose_name_plural = "Privacy Settings"

    def __str__(self):
        return f"PrivacySettings for {self.user.username}"


@receiver(post_save, sender=User)
def create_privacy_settings(sender, instance, created, **kwargs):
    if created:
        PrivacySettings.objects.get_or_create(user=instance)
