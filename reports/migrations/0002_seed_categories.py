from django.db import migrations

CATEGORIES = [
    "Bags",
    "Books and stationery",
    "Clothing",
    "Electronics",
    "ID cards",
    "Jewellery and accessories",
    "Keys",
    "Wallets and money",
    "Water bottles",
    "Other",
]


def add_categories(apps, schema_editor):
    Category = apps.get_model("reports", "Category")
    for name in CATEGORIES:
        Category.objects.get_or_create(name=name)


def remove_categories(apps, schema_editor):
    Category = apps.get_model("reports", "Category")
    Category.objects.filter(name__in=CATEGORIES, reports__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_categories, remove_categories),
    ]
