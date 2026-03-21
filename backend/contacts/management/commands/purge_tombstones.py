from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "Hard-delete contacts soft-deleted more than 30 days ago"

    def handle(self, *args, **options):
        from contacts.models import Contact

        cutoff = timezone.now() - timedelta(days=30)
        qs = Contact.all_objects.filter(is_deleted=True, deleted_at__lt=cutoff)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Purged {count} tombstoned contact(s)"))
