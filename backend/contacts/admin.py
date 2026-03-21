from django.contrib import admin
from contacts.models import (
    Contact,
    ContactPhone,
    ContactEmail,
    InteractionEntry,
    ContactHistory,
)


class ContactPhoneInline(admin.TabularInline):
    model = ContactPhone
    extra = 1
    can_delete = True


class ContactEmailInline(admin.TabularInline):
    model = ContactEmail
    extra = 1
    can_delete = True


class InteractionEntryInline(admin.TabularInline):
    model = InteractionEntry
    extra = 0
    max_num = 0
    can_delete = False
    readonly_fields = ("content", "created_at", "lat", "lng")


class ContactHistoryInline(admin.TabularInline):
    model = ContactHistory
    extra = 0
    max_num = 0
    can_delete = False
    readonly_fields = ("field_name", "old_value", "new_value", "changed_at", "lat", "lng")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "organisation", "context_tag", "is_deleted", "created_at")
    search_fields = ("name", "organisation")
    list_filter = ("context_tag", "owner", "is_deleted")
    inlines = [
        ContactPhoneInline,
        ContactEmailInline,
        InteractionEntryInline,
        ContactHistoryInline,
    ]

    def get_queryset(self, request):
        return Contact.all_objects.all()
