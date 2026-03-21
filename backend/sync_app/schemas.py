from typing import Optional, List, Any
from datetime import datetime
from ninja import Schema


class OutboxChangeIn(Schema):
    entity: str
    operation: str
    payload: dict


class SyncPushIn(Schema):
    changes: List[OutboxChangeIn]


class SyncAppliedItem(Schema):
    entity: str
    id: str
    updated_at: Optional[datetime]


class SyncErrorItem(Schema):
    entity: str
    id: str
    error: str


class SyncPushOut(Schema):
    applied: List[SyncAppliedItem]
    errors: List[SyncErrorItem]


class TombstoneOut(Schema):
    entity: str
    id: str
    deleted_at: datetime


class SyncPullOut(Schema):
    contacts: List[dict]
    contact_phones: List[dict]
    contact_emails: List[dict]
    interaction_entries: List[dict]
    contact_history: List[dict]
    server_time: datetime
    tombstones: List[TombstoneOut]
