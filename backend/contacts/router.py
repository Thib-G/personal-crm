import uuid
from typing import List, Optional
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError

from .models import Contact, ContactPhone, ContactEmail, ContactHistory, InteractionEntry, CONTEXT_CHOICES
from .schemas import (
    ContactIn, ContactOut, ContactListOut, ContactPatchIn,
    ContactPhoneOut, ContactEmailOut, ContactHistoryOut,
    InteractionEntryIn, InteractionEntryOut,
    MapPinOut,
)

router = Router()

VALID_TAGS = {c[0] for c in CONTEXT_CHOICES}


def _get_location_enabled(user):
    from settings_app.models import PrivacySettings
    ps = PrivacySettings.objects.filter(user=user).first()
    return ps.location_tracking_enabled if ps else True


def _contact_to_out(contact: Contact) -> ContactOut:
    phones = [ContactPhoneOut(id=str(p.id), number=p.number) for p in contact.phones.all()]
    emails = [ContactEmailOut(id=str(e.id), address=e.address) for e in contact.emails.all()]
    history = [
        ContactHistoryOut(
            id=str(h.id), field_name=h.field_name, old_value=h.old_value,
            new_value=h.new_value, changed_at=h.changed_at,
            lat=float(h.lat) if h.lat else None,
            lng=float(h.lng) if h.lng else None,
        )
        for h in contact.history.all()
    ]
    interactions = [
        InteractionEntryOut(
            id=str(i.id), contact_id=str(contact.id), content=i.content,
            created_at=i.created_at,
            lat=float(i.lat) if i.lat else None,
            lng=float(i.lng) if i.lng else None,
        )
        for i in contact.interaction_entries.all()
    ]
    return ContactOut(
        id=str(contact.id),
        name=contact.name,
        context_tag=contact.context_tag,
        organisation=contact.organisation,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
        created_lat=float(contact.created_lat) if contact.created_lat else None,
        created_lng=float(contact.created_lng) if contact.created_lng else None,
        phones=phones,
        emails=emails,
        history=history,
        interaction_entries=interactions,
    )


# ── Contacts CRUD ──────────────────────────────────────────────────────────────

@router.get("/", response=List[ContactListOut])
def list_contacts(request, q: Optional[str] = None, ordering: str = "name"):
    from django.db.models import Q

    if q is not None and len(q) < 2:
        raise HttpError(400, "Search query must be at least 2 characters")

    qs = Contact.objects.filter(owner=request.user).prefetch_related("phones", "emails")

    if q:
        qs = (
            qs.filter(
                Q(name__icontains=q)
                | Q(organisation__icontains=q)
                | Q(context_tag__icontains=q)
                | Q(phones__number__icontains=q)
                | Q(emails__address__icontains=q)
                | Q(interaction_entries__content__icontains=q)
            )
            .distinct()
        )

    valid_orderings = {"name", "-name", "created_at", "-created_at"}
    if ordering not in valid_orderings:
        ordering = "name"
    qs = qs.order_by(ordering)[:50]

    return [
        ContactListOut(
            id=str(c.id),
            name=c.name,
            context_tag=c.context_tag,
            organisation=c.organisation,
            created_at=c.created_at,
            updated_at=c.updated_at,
            created_lat=float(c.created_lat) if c.created_lat else None,
            created_lng=float(c.created_lng) if c.created_lng else None,
            phones=[ContactPhoneOut(id=str(p.id), number=p.number) for p in c.phones.all()],
            emails=[ContactEmailOut(id=str(e.id), address=e.address) for e in c.emails.all()],
        )
        for c in qs
    ]


@router.post("/", response={201: ContactOut})
def create_contact(request, payload: ContactIn):
    if not payload.name or not payload.name.strip():
        raise HttpError(400, "Name is required")
    if payload.context_tag not in VALID_TAGS:
        raise HttpError(422, f"context_tag must be one of {sorted(VALID_TAGS)}")
    if Contact.all_objects.filter(pk=payload.id).exists():
        raise HttpError(409, "Contact with this ID already exists")

    location_enabled = _get_location_enabled(request.user)

    contact = Contact.objects.create(
        id=uuid.UUID(payload.id),
        owner=request.user,
        name=payload.name.strip(),
        context_tag=payload.context_tag,
        organisation=payload.organisation,
        created_at=payload.created_at,
        created_lat=payload.created_lat if location_enabled else None,
        created_lng=payload.created_lng if location_enabled else None,
    )

    for phone in payload.phones:
        ContactPhone.objects.create(id=uuid.UUID(phone.id), contact=contact, number=phone.number)
    for email in payload.emails:
        ContactEmail.objects.create(id=uuid.UUID(email.id), contact=contact, address=email.address)

    contact.refresh_from_db()
    return 201, _contact_to_out(contact)


@router.get("/{contact_id}/", response=ContactOut)
def get_contact(request, contact_id: str):
    try:
        contact = (
            Contact.objects.filter(owner=request.user)
            .prefetch_related("phones", "emails", "history", "interaction_entries")
            .get(pk=contact_id)
        )
    except Contact.DoesNotExist:
        raise HttpError(404, "Contact not found")
    return _contact_to_out(contact)


@router.patch("/{contact_id}/", response=ContactOut)
def update_contact(request, contact_id: str, payload: ContactPatchIn):
    try:
        contact = Contact.objects.filter(owner=request.user).get(pk=contact_id)
    except Contact.DoesNotExist:
        raise HttpError(404, "Contact not found")

    location_enabled = _get_location_enabled(request.user)
    edit_lat = payload.edit_lat if location_enabled else None
    edit_lng = payload.edit_lng if location_enabled else None

    changed_fields = []
    if payload.name is not None:
        if not payload.name.strip():
            raise HttpError(400, "Name cannot be blank")
        if payload.name.strip() != contact.name:
            changed_fields.append(("name", contact.name, payload.name.strip()))
            contact.name = payload.name.strip()

    if payload.context_tag is not None and payload.context_tag != contact.context_tag:
        changed_fields.append(("context_tag", contact.context_tag, payload.context_tag))
        contact.context_tag = payload.context_tag

    if payload.organisation is not None and payload.organisation != contact.organisation:
        changed_fields.append(("organisation", contact.organisation or "", payload.organisation))
        contact.organisation = payload.organisation

    contact.save()

    for field_name, old_val, new_val in changed_fields:
        ContactHistory.objects.create(
            contact=contact,
            field_name=field_name,
            old_value=old_val,
            new_value=new_val,
            lat=edit_lat,
            lng=edit_lng,
        )

    if payload.phones is not None:
        old_phones = list(contact.phones.values("id", "number"))
        contact.phones.all().delete()
        for phone in payload.phones:
            ContactPhone.objects.create(id=uuid.UUID(phone.id), contact=contact, number=phone.number)
        new_phones = [p.number for p in payload.phones]
        ContactHistory.objects.create(
            contact=contact,
            field_name="phones",
            old_value=str([p["number"] for p in old_phones]),
            new_value=str(new_phones),
            lat=edit_lat,
            lng=edit_lng,
        )

    if payload.emails is not None:
        old_emails = list(contact.emails.values("id", "address"))
        contact.emails.all().delete()
        for email in payload.emails:
            ContactEmail.objects.create(id=uuid.UUID(email.id), contact=contact, address=email.address)
        new_emails = [e.address for e in payload.emails]
        ContactHistory.objects.create(
            contact=contact,
            field_name="emails",
            old_value=str([e["address"] for e in old_emails]),
            new_value=str(new_emails),
            lat=edit_lat,
            lng=edit_lng,
        )

    contact.refresh_from_db()
    return _contact_to_out(contact)


@router.delete("/{contact_id}/", response={204: None})
def delete_contact(request, contact_id: str):
    try:
        contact = Contact.objects.filter(owner=request.user).get(pk=contact_id)
    except Contact.DoesNotExist:
        raise HttpError(404, "Contact not found")
    contact.is_deleted = True
    contact.deleted_at = timezone.now()
    contact.save()
    return 204, None


# ── Interaction Entries ────────────────────────────────────────────────────────

@router.post("/{contact_id}/interactions/", response={201: InteractionEntryOut})
def add_interaction(request, contact_id: str, payload: InteractionEntryIn):
    try:
        contact = Contact.objects.filter(owner=request.user).get(pk=contact_id)
    except Contact.DoesNotExist:
        raise HttpError(404, "Contact not found")

    if not payload.content or not payload.content.strip():
        raise HttpError(400, "Content is required")

    location_enabled = _get_location_enabled(request.user)

    entry = InteractionEntry.objects.create(
        id=uuid.UUID(payload.id),
        contact=contact,
        content=payload.content.strip(),
        created_at=payload.created_at,
        lat=payload.lat if location_enabled else None,
        lng=payload.lng if location_enabled else None,
    )
    return 201, InteractionEntryOut(
        id=str(entry.id),
        contact_id=str(contact.id),
        content=entry.content,
        created_at=entry.created_at,
        lat=float(entry.lat) if entry.lat else None,
        lng=float(entry.lng) if entry.lng else None,
    )


@router.get("/{contact_id}/interactions/", response=List[InteractionEntryOut])
def list_interactions(request, contact_id: str):
    try:
        contact = Contact.objects.filter(owner=request.user).get(pk=contact_id)
    except Contact.DoesNotExist:
        raise HttpError(404, "Contact not found")

    return [
        InteractionEntryOut(
            id=str(i.id),
            contact_id=str(contact.id),
            content=i.content,
            created_at=i.created_at,
            lat=float(i.lat) if i.lat else None,
            lng=float(i.lng) if i.lng else None,
        )
        for i in contact.interaction_entries.order_by("-created_at")
    ]


# ── Map Pins ───────────────────────────────────────────────────────────────────

@router.get("/map/pins/", response=List[MapPinOut])
def map_pins(request):
    pins = []
    contacts = Contact.objects.filter(
        owner=request.user,
        created_lat__isnull=False,
        created_lng__isnull=False,
    )
    for c in contacts:
        pins.append(MapPinOut(
            type="contact",
            id=str(c.id),
            contact_id=str(c.id),
            contact_name=c.name,
            lat=float(c.created_lat),
            lng=float(c.created_lng),
            label=c.name,
            timestamp=c.created_at,
        ))

    interactions = InteractionEntry.objects.filter(
        contact__owner=request.user,
        lat__isnull=False,
        lng__isnull=False,
    ).select_related("contact")
    for i in interactions:
        pins.append(MapPinOut(
            type="interaction",
            id=str(i.id),
            contact_id=str(i.contact.id),
            contact_name=i.contact.name,
            lat=float(i.lat),
            lng=float(i.lng),
            label=i.content[:50] + "..." if len(i.content) > 50 else i.content,
            timestamp=i.created_at,
        ))

    return pins
