from typing import Optional, List
from datetime import datetime
from ninja import Schema
from ninja.errors import HttpError


# Phone / Email schemas
class ContactPhoneIn(Schema):
    id: str
    number: str


class ContactPhoneOut(Schema):
    id: str
    number: str


class ContactEmailIn(Schema):
    id: str
    address: str


class ContactEmailOut(Schema):
    id: str
    address: str


# History schema
class ContactHistoryOut(Schema):
    id: str
    field_name: str
    old_value: Optional[str]
    new_value: str
    changed_at: datetime
    lat: Optional[float]
    lng: Optional[float]


# Interaction schemas
class InteractionEntryIn(Schema):
    id: str
    content: str
    created_at: datetime
    lat: Optional[float] = None
    lng: Optional[float] = None


class InteractionEntryOut(Schema):
    id: str
    contact_id: str
    content: str
    created_at: datetime
    lat: Optional[float]
    lng: Optional[float]


# Contact schemas
VALID_CONTEXT_TAGS = {"event", "work", "personal", "other"}


class ContactIn(Schema):
    id: str
    name: str
    context_tag: str
    organisation: Optional[str] = None
    created_at: datetime
    created_lat: Optional[float] = None
    created_lng: Optional[float] = None
    phones: List[ContactPhoneIn] = []
    emails: List[ContactEmailIn] = []


class ContactPatchIn(Schema):
    name: Optional[str] = None
    context_tag: Optional[str] = None
    organisation: Optional[str] = None
    phones: Optional[List[ContactPhoneIn]] = None
    emails: Optional[List[ContactEmailIn]] = None
    edit_lat: Optional[float] = None
    edit_lng: Optional[float] = None


class ContactOut(Schema):
    id: str
    name: str
    context_tag: str
    organisation: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_lat: Optional[float]
    created_lng: Optional[float]
    phones: List[ContactPhoneOut]
    emails: List[ContactEmailOut]
    history: List[ContactHistoryOut] = []
    interaction_entries: List[InteractionEntryOut] = []


class ContactListOut(Schema):
    id: str
    name: str
    context_tag: str
    organisation: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_lat: Optional[float]
    created_lng: Optional[float]
    phones: List[ContactPhoneOut]
    emails: List[ContactEmailOut]


class MapPinOut(Schema):
    type: str
    id: str
    contact_id: str
    contact_name: str
    lat: float
    lng: float
    label: str
    timestamp: datetime
