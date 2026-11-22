"""Load Ashoka's campus outlines and named places from OpenStreetMap.

Run:  python manage.py import_campus
Or name the exact areas, as they are called on openstreetmap.org:
      python manage.py import_campus --name "Ashoka University" --name "Ashoka University New Campus"

Safe to run again: it updates outlines and places by name instead of making copies.
Outlines you added by hand in the admin are kept.
"""
import json
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand, CommandError

from maps.models import CampusBoundary, Landmark

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Without --name: every university or college area whose name contains "Ashoka"
DEFAULT_CAMPUS_FILTER = """
  way["amenity"~"^(university|college)$"]["name"~"Ashoka",i];
  relation["amenity"~"^(university|college)$"]["name"~"Ashoka",i];
"""


def build_query(names):
    if names:
        parts = "".join(
            f'  way["name"="{n}"];\n  relation["name"="{n}"];\n'
            for n in (name.replace('"', '') for name in names))
    else:
        parts = DEFAULT_CAMPUS_FILTER
    return f"""
[out:json][timeout:90];
(
{parts})->.campus;
.campus out geom;
.campus map_to_area->.a;
nwr(area.a)["name"];
out center tags;
"""


def guess_kind(tags):
    """Turn OpenStreetMap labels into our landmark kinds."""
    name = tags.get("name", "").lower()
    if tags.get("amenity") == "library" or "library" in name:
        return Landmark.Kind.LIBRARY
    if (tags.get("building") in ("dormitory", "residential")
            or "hostel" in name or "residence" in name):
        return Landmark.Kind.HOSTEL
    if (tags.get("amenity") in ("canteen", "restaurant", "food_court", "cafe")
            or "mess" in name or "dining" in name or "cafe" in name):
        return Landmark.Kind.MESS
    if (tags.get("leisure") in ("sports_centre", "pitch", "stadium", "fitness_centre")
            or "sports" in name or "court" in name or "ground" in name):
        return Landmark.Kind.SPORTS
    if tags.get("barrier") == "gate" or tags.get("entrance") or "gate" in name:
        return Landmark.Kind.GATE
    if (tags.get("building") in ("university", "college", "school")
            or "academic" in name or "block" in name):
        return Landmark.Kind.ACADEMIC
    return Landmark.Kind.OTHER


def outline_from(element):
    """Corners [lat, lng] of a campus way, or the biggest outer ring of a relation."""
    if element.get("geometry"):
        return [[p["lat"], p["lon"]] for p in element["geometry"]]
    rings = [m.get("geometry") or [] for m in element.get("members", [])
             if m.get("role") == "outer"]
    biggest = max(rings, key=len, default=[])
    return [[p["lat"], p["lon"]] for p in biggest]


def position_of(element):
    if "lat" in element:
        return element["lat"], element["lon"]
    if "center" in element:
        return element["center"]["lat"], element["center"]["lon"]
    return None


class Command(BaseCommand):
    help = "Load Ashoka's campus outlines and named places from OpenStreetMap"

    def add_arguments(self, parser):
        parser.add_argument("--name", action="append", default=[],
                            help="Exact name of a campus area on OpenStreetMap (can repeat)")
        parser.add_argument("--from-file", help="Use a saved Overpass JSON file instead of the internet")

    def handle(self, *args, **options):
        if options["from_file"]:
            with open(options["from_file"]) as f:
                data = json.load(f)
        else:
            self.stdout.write("Asking OpenStreetMap (can take up to a minute)...")
            body = urllib.parse.urlencode({"data": build_query(options["name"])}).encode()
            request = urllib.request.Request(OVERPASS_URL, data=body,
                                             headers={"User-Agent": "lost-and-found-student-project"})
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    data = json.load(response)
            except Exception as error:
                raise CommandError(f"Could not reach OpenStreetMap: {error}")

        elements = data.get("elements", [])
        campus = [e for e in elements if e.get("geometry") or e.get("members")]
        if not campus:
            raise CommandError("OpenStreetMap returned no campus outline. Check the names "
                               "on openstreetmap.org, or add the outline by hand in the admin.")

        boundaries = []
        for element in campus:
            outline = outline_from(element)
            name = element.get("tags", {}).get("name", f"Campus {element['id']}")[:100]
            if len(outline) < 3:
                self.stdout.write(self.style.WARNING(f"Skipped {name}: incomplete outline"))
                continue
            boundary, _ = CampusBoundary.objects.update_or_create(
                name=name, defaults={"points": outline})
            boundaries.append(boundary)
            self.stdout.write(self.style.SUCCESS(
                f"Campus outline saved: {name} ({len(outline)} corners)"))

        if not boundaries:
            raise CommandError("No usable campus outline found.")
        all_boundaries = list(CampusBoundary.objects.all())

        campus_ids = {(e["type"], e["id"]) for e in campus}
        added = updated = skipped = 0
        for element in elements:
            if (element["type"], element["id"]) in campus_ids:
                continue
            tags = element.get("tags", {})
            name = tags.get("name", "").strip()
            position = position_of(element)
            if not name or position is None:
                continue
            lat, lng = position
            if not any(b.contains(lat, lng) for b in all_boundaries):
                skipped += 1
                continue
            _, created = Landmark.objects.update_or_create(
                name=name[:100],
                defaults={"kind": guess_kind(tags),
                          "latitude": round(lat, 6), "longitude": round(lng, 6)})
            added += created
            updated += not created

        self.stdout.write(self.style.SUCCESS(
            f"Landmarks: {added} added, {updated} updated, {skipped} outside campus skipped"))
        self.stdout.write("Check them in the admin: fix any wrong kinds, delete odd ones, "
                          "and add missing places by hand.")
