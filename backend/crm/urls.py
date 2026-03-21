"""
URL configuration for crm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.http import FileResponse, Http404
from crm.api import api


def spa_index(request):
    spa_index_path = settings.STATIC_ROOT / "spa" / "index.html"
    if not spa_index_path.exists():
        raise Http404("SPA not built")
    return FileResponse(open(spa_index_path, "rb"), content_type="text/html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    re_path(r"^(?!static/).*$", spa_index),
]
