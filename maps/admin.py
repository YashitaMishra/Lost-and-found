from django.contrib import admin
from .models import CampusBoundary, Landmark


@admin.register(Landmark)
class LandmarkAdmin(admin.ModelAdmin):
    list_display = ["name", "kind", "latitude", "longitude"]
    list_filter = ["kind"]
    search_fields = ["name"]


admin.site.register(CampusBoundary)
