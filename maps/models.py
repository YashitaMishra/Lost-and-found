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
