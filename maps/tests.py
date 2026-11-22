from django.test import TestCase

from maps.models import CampusBoundary, is_on_campus

# A simple square for testing, not the real campus
SECOND = [[28.970, 77.120], [28.970, 77.130], [28.980, 77.130], [28.980, 77.120]]
SQUARE = [[28.940, 77.100], [28.940, 77.110], [28.950, 77.110], [28.950, 77.100]]


class CampusBoundaryTests(TestCase):
    def test_point_inside_is_on_campus(self):
        CampusBoundary.objects.create(name="Main", points=SQUARE)
        self.assertTrue(is_on_campus(28.945, 77.105))

    def test_point_outside_is_refused(self):
        CampusBoundary.objects.create(name="Main", points=SQUARE)
        self.assertFalse(is_on_campus(28.960, 77.105))

    def test_no_boundary_yet_allows_everything(self):
        self.assertTrue(is_on_campus(0, 0))

    def test_point_on_second_campus_is_allowed(self):
        CampusBoundary.objects.create(name="Main", points=SQUARE)
        CampusBoundary.objects.create(name="New", points=SECOND)
        self.assertTrue(is_on_campus(28.975, 77.125))
        self.assertFalse(is_on_campus(28.960, 77.105))
