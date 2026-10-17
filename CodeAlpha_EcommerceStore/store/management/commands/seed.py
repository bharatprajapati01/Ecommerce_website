from decimal import Decimal

from django.core.management.base import BaseCommand

from store.catalog import CATALOG, CATEGORY_EMOJI
from store.models import Category, Product


class Command(BaseCommand):
    help = "Populate the database with sample categories, subcategories and products."

    @staticmethod
    def _set_emoji(category):
        # Only fill in a missing icon, so icons you edit in the admin are kept.
        emoji = CATEGORY_EMOJI.get(category.name, "")
        if emoji and not category.emoji:
            category.emoji = emoji
            category.save(update_fields=["emoji"])

    def handle(self, *args, **options):
        created = moved = cleaned = 0
        for cat_name, info in CATALOG.items():
            parent, _ = Category.objects.get_or_create(parent=None, name=cat_name)
            self._set_emoji(parent)
            for sub_name, products in info["sub"].items():
                sub, _ = Category.objects.get_or_create(parent=parent, name=sub_name)
                self._set_emoji(sub)
                for name, desc, price, stock, _icon, _colour in products:
                    product, was_created = Product.objects.get_or_create(
                        name=name,
                        defaults={
                            "category": sub,
                            "description": desc,
                            "price": Decimal(price),
                            "stock": stock,
                        },
                    )
                    if was_created:
                        created += 1
                        continue
                    changed = []
                    if product.category_id != sub.id:
                        product.category = sub
                        changed.append("category")
                        moved += 1
                    # Earlier versions used random placeholder photos that did not
                    # match the product. Clear them so the matching illustration shows.
                    if product.image_url.startswith("https://picsum.photos"):
                        product.image_url = ""
                        changed.append("image_url")
                        cleaned += 1
                    if changed:
                        product.save(update_fields=changed)
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created} new products "
                f"(moved {moved}, replaced {cleaned} old placeholder images)."
            )
        )
