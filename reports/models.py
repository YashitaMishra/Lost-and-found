from django.conf import settings
from django.db import models
from django.db.models import F, Q


class Category(models.Model):
    """Fixed list managed by the admin: Electronics, ID cards, Keys, Bags..."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Report(models.Model):
    class Type(models.TextChoices):
        LOST = "LOST", "Lost"
        FOUND = "FOUND", "Found"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        MATCH_PENDING = "MATCH_PENDING", "Match pending"
        RECOVERY_IN_PROGRESS = "RECOVERY_IN_PROGRESS", "Recovery in progress"
        RECOVERED = "RECOVERED", "Recovered"
        CLOSED = "CLOSED", "Closed"
        EXPIRED = "EXPIRED", "Expired"

    class LocationVisibility(models.TextChoices):
        EXACT = "EXACT", "Exact"
        LANDMARK = "LANDMARK", "Landmark only"
        HIDDEN = "HIDDEN", "Hidden"

    class PathVisibility(models.TextChoices):
        PRIVATE = "PRIVATE", "Private"
        PUBLIC = "PUBLIC", "Public"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="reports")
    report_type = models.CharField(max_length=5, choices=Type.choices)
    title = models.CharField(max_length=120)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 related_name="reports")

    # When it was lost or found (a time window)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()

    # Where: one point, plus an optional named landmark
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    landmark = models.ForeignKey("maps.Landmark", on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name="reports")
    held_at = models.CharField(max_length=200, blank=True,
                               help_text="FOUND only: where the item is kept now")

    # Privacy (FR11)
    location_visibility = models.CharField(max_length=10,
        choices=LocationVisibility.choices, default=LocationVisibility.EXACT)
    path_visibility = models.CharField(max_length=10,
        choices=PathVisibility.choices, default=PathVisibility.PRIVATE)

    status = models.CharField(max_length=25, choices=Status.choices,
                              default=Status.OPEN)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now_add=True)  # for 90-day expiry

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(event_start__lte=F("event_end")),
                                   name="report_start_before_end"),
        ]
        indexes = [
            models.Index(fields=["status", "report_type", "category", "event_start"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()}: {self.title}"
