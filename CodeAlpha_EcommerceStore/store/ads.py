"""Promotional banners for the For You page.

These are Shopwise's own demo offers: each one links to a category and shows two
product illustrations. `from_price` is the real lowest price in that category, so
the banners never advertise a price the store doesn't have.

Edit the lists below to change the banners. A banner is skipped automatically if
its category does not exist.
"""
from django.db.models import Min, Q
from django.urls import reverse

from .models import Category, Product

# Sliding banners at the top of the page.
HERO_ADS = [
    dict(kicker="Festive sale", title="Crazy Deals", text="on gadgets & gear",
         category="electronics", products=["wireless-earbuds", "bluetooth-speaker"],
         colors=("#4f46e5", "#7c3aed"), cta="Shop electronics"),
    dict(kicker="Back to campus", title="Books for every reader", text="Bestsellers & coding classics",
         category="books", products=["atomic-habits", "python-crash-course"],
         colors=("#f59e0b", "#ef4444"), cta="Shop books"),
    dict(kicker="New season", title="Fresh styles", text="Wardrobe upgrades for everyone",
         category="clothing", products=["floral-summer-dress", "slim-fit-jeans"],
         colors=("#ec4899", "#be185d"), cta="Shop clothing"),
    dict(kicker="Home makeover", title="Kitchen essentials", text="Cook, brew and serve",
         category="home-kitchen", products=["electric-kettle-18l", "pressure-cooker-5l"],
         colors=("#10b981", "#0e7490"), cta="Shop home & kitchen"),
    dict(kicker="Get moving", title="Fitness fest", text="Gear up for your goals",
         category="sports-fitness", products=["yoga-mat-6mm", "dumbbell-set-2-x-5kg"],
         colors=("#0ea5e9", "#4338ca"), cta="Shop sports"),
]

# Wide banners placed between the sections.
WIDE_ADS = [
    dict(kicker="Style & comfort in one", title="Step up your footwear game", text="",
         category="footwear", products=["running-shoes", "formal-leather-shoes"],
         colors=("#1e293b", "#475569"), cta="Shop footwear"),
    dict(kicker="Power up", title="Accessories you'll use every day", text="",
         category="accessories", products=["portable-power-bank-20000mah", "wireless-mouse"],
         colors=("#0f766e", "#0891b2"), cta="Shop accessories"),
]


def build_ads(specs):
    """Turn the specs above into template-ready dicts (skipping unknown categories)."""
    slugs = {s for ad in specs for s in ad["products"]}
    products = {p.slug: p for p in Product.objects.filter(slug__in=slugs)}
    categories = {c.slug: c for c in Category.objects.filter(slug__in={a["category"] for a in specs})}

    ads = []
    for ad in specs:
        category = categories.get(ad["category"])
        if not category:
            continue
        lowest = (
            Product.objects.filter(available=True)
            .filter(Q(category=category) | Q(category__parent=category))
            .aggregate(m=Min("price"))["m"]
        )
        ads.append({
            **ad,
            "url": reverse("category", args=[category.slug]),
            "from_price": lowest,
            "art": [products[s] for s in ad["products"] if s in products],
            "style": f"background: linear-gradient(120deg, {ad['colors'][0]}, {ad['colors'][1]});",
        })
    return ads
