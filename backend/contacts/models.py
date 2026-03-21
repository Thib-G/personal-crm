import uuid
from django.db import models
from django.contrib.auth.models import User


class ActiveContactManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllContactManager(models.Manager):
    """Unfiltered manager for sync endpoints."""
    def get_queryset(self):
        return super().get_queryset()


CONTEXT_CHOICES = [
    ("event", "Event"),
    ("work", "Work"),
    ("personal", "Personal"),
    ("other", "Other"),
]


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="contacts")
    name = models.CharField(max_length=255, db_index=True)
    context_tag = models.CharField(max_length=20, choices=CONTEXT_CHOICES, default="other")
    organisation = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    created_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveContactManager()
    all_objects = AllContactManager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ContactPhone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="phones")
    number = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.number


class ContactEmail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="emails")
    address = models.CharField(max_length=254)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address


class InteractionEntry(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="interaction_entries")
    content = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Interaction on {self.created_at}"


class ContactHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="history")
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField()
    changed_at = models.DateTimeField(auto_now_add=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.field_name} changed at {self.changed_at}"
