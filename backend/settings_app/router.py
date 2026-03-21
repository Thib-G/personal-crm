from ninja import Router
from ninja.errors import HttpError

from .models import PrivacySettings
from .schemas import PrivacySettingsOut, PrivacySettingsPatch

router = Router()


@router.get("/privacy/", response=PrivacySettingsOut)
def get_privacy_settings(request):
    settings, _ = PrivacySettings.objects.get_or_create(user=request.user)
    return PrivacySettingsOut(location_tracking_enabled=settings.location_tracking_enabled)


@router.patch("/privacy/", response=PrivacySettingsOut)
def update_privacy_settings(request, payload: PrivacySettingsPatch):
    settings, _ = PrivacySettings.objects.get_or_create(user=request.user)
    settings.location_tracking_enabled = payload.location_tracking_enabled
    settings.save()
    return PrivacySettingsOut(location_tracking_enabled=settings.location_tracking_enabled)
