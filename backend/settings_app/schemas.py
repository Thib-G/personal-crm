from ninja import Schema


class PrivacySettingsOut(Schema):
    location_tracking_enabled: bool


class PrivacySettingsPatch(Schema):
    location_tracking_enabled: bool
