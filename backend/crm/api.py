from ninja import NinjaAPI
from ninja.security import django_auth

api = NinjaAPI(
    title="Personal CRM",
    version="1.0",
    auth=django_auth,
)

# Routers are added after models are set up to avoid circular imports
# Each app's router is imported and added here:
from users.router import router as users_router  # noqa: E402
from settings_app.router import router as settings_router  # noqa: E402
from contacts.router import router as contacts_router  # noqa: E402
from sync_app.router import router as sync_router  # noqa: E402

api.add_router("/auth/", users_router, tags=["Auth"])
api.add_router("/settings/", settings_router, tags=["Settings"])
api.add_router("/contacts/", contacts_router, tags=["Contacts"])
api.add_router("/sync/", sync_router, tags=["Sync"], auth=django_auth)
