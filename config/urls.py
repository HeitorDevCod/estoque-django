from django.contrib import admin
from django.urls import include, path

from inventory import web

urlpatterns = [
    path("", web.product_list, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("inventory.urls")),
    path("api-auth/", include("rest_framework.urls")),
]
