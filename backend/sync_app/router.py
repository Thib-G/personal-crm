import uuid
from datetime import datetime, timezone as dt_tz
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError

from .schemas import SyncPushIn, SyncPushOut, SyncPullOut, SyncAppliedItem, SyncErrorItem, TombstoneOut

router = Router()


@router.get("/pull/", response=SyncPullOut)
def sync_pull(request, since: str = "1970-01-01T00:00:00Z"):
    from contacts.models import Contact, ContactPhone, ContactEmail, InteractionEntry, ContactHistory

    try:
        since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
    except ValueError:
        raise HttpError(400, "Invalid 'since' datetime format")

    contacts_qs = Contact.all_objects.filter(owner=request.user, updated_at__gt=since_dt)
    phones_qs = ContactPhone.objects.filter(contact__owner=request.user, updated_at__gt=since_dt)
    emails_qs = ContactEmail.objects.filter(contact__owner=request.user, updated_at__gt=since_dt)
    interactions_qs = InteractionEntry.objects.filter(contact__owner=request.user, updated_at__gt=since_dt)
    history_qs = ContactHistory.objects.filter(contact__owner=request.user, changed_at__gt=since_dt)

    tombstones = [
        TombstoneOut(entity="contact", id=str(c.id), deleted_at=c.deleted_at)
        for c in contacts_qs.filter(is_deleted=True)
    ]

    def contact_to_dict(c):
        return {
            "id": str(c.id), "name": c.name, "context_tag": c.context_tag,
            "organisation": c.organisation, "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
            "created_lat": float(c.created_lat) if c.created_lat else None,
            "created_lng": float(c.created_lng) if c.created_lng else None,
            "is_deleted": c.is_deleted,
        }

    return SyncPullOut(
        contacts=[contact_to_dict(c) for c in contacts_qs],
        contact_phones=[{"id": str(p.id), "contact_id": str(p.contact_id), "number": p.number} for p in phones_qs],
        contact_emails=[{"id": str(e.id), "contact_id": str(e.contact_id), "address": e.address} for e in emails_qs],
        interaction_entries=[
            {"id": str(i.id), "contact_id": str(i.contact_id), "content": i.content,
             "created_at": i.created_at.isoformat(), "lat": float(i.lat) if i.lat else None, "lng": float(i.lng) if i.lng else None}
            for i in interactions_qs
        ],
        contact_history=[
            {"id": str(h.id), "contact_id": str(h.contact_id), "field_name": h.field_name,
             "old_value": h.old_value, "new_value": h.new_value, "changed_at": h.changed_at.isoformat(),
             "lat": float(h.lat) if h.lat else None, "lng": float(h.lng) if h.lng else None}
            for h in history_qs
        ],
        server_time=timezone.now(),
        tombstones=tombstones,
    )


@router.post("/push/", response=SyncPushOut)
def sync_push(request, payload: SyncPushIn):
    from contacts.models import Contact, ContactPhone, ContactEmail, InteractionEntry, ContactHistory
    from contacts.router import _get_location_enabled

    applied = []
    errors = []
    location_enabled = _get_location_enabled(request.user)

    for change in payload.changes:
        entity = change.entity
        operation = change.operation
        p = change.payload
        record_id = p.get("id", "")

        try:
            if entity == "contact":
                if operation == "create":
                    if not Contact.all_objects.filter(pk=record_id).exists():
                        contact = Contact.objects.create(
                            id=uuid.UUID(record_id),
                            owner=request.user,
                            name=p.get("name", "").strip(),
                            context_tag=p.get("context_tag", "other"),
                            organisation=p.get("organisation"),
                            created_at=p.get("created_at", timezone.now()),
                            created_lat=p.get("created_lat") if location_enabled else None,
                            created_lng=p.get("created_lng") if location_enabled else None,
                        )
                        for phone in p.get("phones", []):
                            if phone.get("number", "").strip():
                                ContactPhone.objects.get_or_create(
                                    id=uuid.UUID(phone["id"]),
                                    defaults={"contact": contact, "number": phone["number"].strip()},
                                )
                        for email in p.get("emails", []):
                            if email.get("address", "").strip():
                                ContactEmail.objects.get_or_create(
                                    id=uuid.UUID(email["id"]),
                                    defaults={"contact": contact, "address": email["address"].strip()},
                                )
                elif operation == "update":
                    try:
                        contact = Contact.all_objects.filter(owner=request.user).get(pk=record_id)
                        edit_lat = p.get("edit_lat") if location_enabled else None
                        edit_lng = p.get("edit_lng") if location_enabled else None

                        if "name" in p and p["name"].strip() and p["name"].strip() != contact.name:
                            ContactHistory.objects.create(
                                contact=contact, field_name="name",
                                old_value=contact.name, new_value=p["name"].strip(),
                                lat=edit_lat, lng=edit_lng,
                            )
                            contact.name = p["name"].strip()
                        if "context_tag" in p and p["context_tag"] != contact.context_tag:
                            ContactHistory.objects.create(
                                contact=contact, field_name="context_tag",
                                old_value=contact.context_tag, new_value=p["context_tag"],
                                lat=edit_lat, lng=edit_lng,
                            )
                            contact.context_tag = p["context_tag"]
                        if "organisation" in p and p["organisation"] != contact.organisation:
                            ContactHistory.objects.create(
                                contact=contact, field_name="organisation",
                                old_value=contact.organisation or "", new_value=p["organisation"] or "",
                                lat=edit_lat, lng=edit_lng,
                            )
                            contact.organisation = p["organisation"]
                        contact.save()

                        if "phones" in p and p["phones"] is not None:
                            old_phones = list(contact.phones.values_list("number", flat=True))
                            contact.phones.all().delete()
                            for phone in p["phones"]:
                                if phone.get("number", "").strip():
                                    ContactPhone.objects.create(
                                        id=uuid.UUID(phone["id"]), contact=contact,
                                        number=phone["number"].strip(),
                                    )
                            new_phones = [ph["number"] for ph in p["phones"] if ph.get("number", "").strip()]
                            ContactHistory.objects.create(
                                contact=contact, field_name="phones",
                                old_value=str(old_phones), new_value=str(new_phones),
                                lat=edit_lat, lng=edit_lng,
                            )

                        if "emails" in p and p["emails"] is not None:
                            old_emails = list(contact.emails.values_list("address", flat=True))
                            contact.emails.all().delete()
                            for email in p["emails"]:
                                if email.get("address", "").strip():
                                    ContactEmail.objects.create(
                                        id=uuid.UUID(email["id"]), contact=contact,
                                        address=email["address"].strip(),
                                    )
                            new_emails = [em["address"] for em in p["emails"] if em.get("address", "").strip()]
                            ContactHistory.objects.create(
                                contact=contact, field_name="emails",
                                old_value=str(old_emails), new_value=str(new_emails),
                                lat=edit_lat, lng=edit_lng,
                            )
                    except Contact.DoesNotExist:
                        errors.append(SyncErrorItem(entity=entity, id=record_id, error="Contact not found"))
                        continue
                elif operation == "delete":
                    Contact.all_objects.filter(pk=record_id, owner=request.user).update(
                        is_deleted=True, deleted_at=timezone.now()
                    )

            elif entity == "interaction_entry":
                if operation == "create":
                    contact_id = p.get("contact_id", "")
                    try:
                        contact = Contact.objects.filter(owner=request.user).get(pk=contact_id)
                        if not InteractionEntry.objects.filter(pk=record_id).exists():
                            InteractionEntry.objects.create(
                                id=uuid.UUID(record_id),
                                contact=contact,
                                content=p.get("content", "").strip(),
                                created_at=p.get("created_at", timezone.now()),
                                lat=p.get("lat") if location_enabled else None,
                                lng=p.get("lng") if location_enabled else None,
                            )
                    except Contact.DoesNotExist:
                        errors.append(SyncErrorItem(entity=entity, id=record_id, error="Contact not found"))
                        continue

            applied.append(SyncAppliedItem(entity=entity, id=record_id, updated_at=timezone.now()))

        except Exception as e:
            errors.append(SyncErrorItem(entity=entity, id=record_id, error=str(e)))

    return SyncPushOut(applied=applied, errors=errors)
