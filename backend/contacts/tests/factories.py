import uuid
import factory
from django.contrib.auth.models import User
from django.utils import timezone

from contacts.models import Contact, ContactPhone, ContactEmail, InteractionEntry, ContactHistory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "testpass")


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact

    id = factory.LazyFunction(uuid.uuid4)
    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Contact {n}")
    context_tag = "work"
    organisation = "Acme Corp"
    created_at = factory.LazyFunction(timezone.now)


class ContactPhoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactPhone

    id = factory.LazyFunction(uuid.uuid4)
    contact = factory.SubFactory(ContactFactory)
    number = factory.Sequence(lambda n: f"+3249{n:07d}")


class ContactEmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactEmail

    id = factory.LazyFunction(uuid.uuid4)
    contact = factory.SubFactory(ContactFactory)
    address = factory.Sequence(lambda n: f"user{n}@example.com")


class InteractionEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InteractionEntry

    id = factory.LazyFunction(uuid.uuid4)
    contact = factory.SubFactory(ContactFactory)
    content = "Had a great conversation"
    created_at = factory.LazyFunction(timezone.now)


class ContactHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactHistory

    contact = factory.SubFactory(ContactFactory)
    field_name = "name"
    old_value = "Old Name"
    new_value = "New Name"
