from django.db import migrations


def clear_placeholder_images(apps, schema_editor):
    """Remove the random picsum.photos links from the first sample data so the
    matching bundled illustration is shown instead."""
    Product = apps.get_model("store", "Product")
    Product.objects.filter(image_url__contains="picsum.photos").update(image_url="")


class Migration(migrations.Migration):
    dependencies = [("store", "0002_category_subcategories")]

    operations = [
        migrations.RunPython(clear_placeholder_images, migrations.RunPython.noop),
    ]
