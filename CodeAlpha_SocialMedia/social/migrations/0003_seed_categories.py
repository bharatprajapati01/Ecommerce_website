from django.db import migrations

CATEGORIES = [
    ("Music", "music", ["Pop", "Hip-hop", "Indie", "Classical"]),
    ("Gaming", "gamepad", ["PC", "Console", "Mobile", "Esports"]),
    ("Education", "cap", ["Study tips", "Exams", "Courses"]),
    ("Science & Tech", "globe", ["Coding", "AI & ML", "Gadgets", "Space"]),
    ("Entertainment", "play", ["Movies", "Series", "Anime", "Memes"]),
    ("Student Hubs", "users", ["Campus life", "Internships", "Projects", "Hostel life"]),
]


def slugify(text):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in text)
    return "-".join(part for part in keep.split("-") if part)


def seed(apps, schema_editor):
    Category = apps.get_model("social", "Category")
    for i, (name, icon, subs) in enumerate(CATEGORIES):
        parent, _ = Category.objects.get_or_create(
            slug=slugify(name), defaults={"name": name, "icon": icon, "order": i}
        )
        for j, sub in enumerate(subs):
            Category.objects.get_or_create(
                slug=slugify(f"{name}-{sub}"),
                defaults={"name": sub, "parent": parent, "order": j},
            )


def unseed(apps, schema_editor):
    apps.get_model("social", "Category").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("social", "0002_categories")]
    operations = [migrations.RunPython(seed, unseed)]
