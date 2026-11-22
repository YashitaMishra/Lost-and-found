from django.db import models


class Landmark(models.Model):
    class Kind(models.TextChoices):
        HOSTEL = "HOSTEL", "Hostel"
        ACADEMIC = "ACADEMIC", "Academic block"
        MESS = "MESS", "Mess"
        SPORTS = "SPORTS", "Sports"
        LIBRARY = "LIBRARY", "Library"
        GATE = "GATE", "Gate"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=100, unique=True)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name


class CampusBoundary(models.Model):
    """The outline of one campus area, as a list of [latitude, longitude] corners.

    There can be several rows (main campus, new campus...). A point is on
    campus if it is inside any of them; anything else is refused (ER3).
    """
    name = models.CharField(max_length=100, unique=True)
    points = models.JSONField(help_text="List of [latitude, longitude] corners, in order")

    class Meta:
        verbose_name_plural = "campus boundaries"

    def __str__(self):
        return f"{self.name} ({len(self.points)} corners)"

    def contains(self, lat, lng):
        """True if the point is inside the outline (ray casting)."""
        lat, lng = float(lat), float(lng)
        inside = False
        pts = self.points
        j = len(pts) - 1
        for i in range(len(pts)):
            yi, xi = pts[i]
            yj, xj = pts[j]
            if (yi > lat) != (yj > lat):
                x_cross = xi + (lat - yi) * (xj - xi) / (yj - yi)
                if lng < x_cross:
                    inside = not inside
            j = i
        return inside


def is_on_campus(lat, lng):
    """Used by the report and path logic (R1, P1) to apply ER3.

    If no boundary has been loaded yet, every point is allowed, so
    nothing breaks while we are still building.
    """
    boundaries = list(CampusBoundary.objects.all())
    if not boundaries:
        return True
    return any(b.contains(lat, lng) for b in boundaries)
