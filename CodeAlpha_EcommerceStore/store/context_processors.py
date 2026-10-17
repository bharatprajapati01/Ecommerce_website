from django.urls import reverse

from .account_menu import ACCOUNT_LINKS, LOGOUT_ICON, icon
from .cart import Cart
from .models import Category


def cart(request):
    return {"cart_count": len(Cart(request))}


def nav_categories(request):
    """Top-level categories (with their subcategories) for the menu bar."""
    return {
        "nav_categories": Category.objects.filter(parent__isnull=True).prefetch_related(
            "children"
        )
    }


def account(request):
    """Account menu entries and the ids of products on the user's wishlist."""
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated):
        return {"wishlist_ids": set()}
    current = getattr(request.resolver_match, "url_name", "")
    links = [
        {
            "label": label,
            "url": reverse(name, args=args),
            "icon": icon(ic),
            "active": current == name and name != "info_page",
        }
        for label, name, args, ic in ACCOUNT_LINKS
    ]
    return {
        "account_links": links,
        "logout_icon": LOGOUT_ICON,
        "wishlist_ids": set(user.wishlist.values_list("product_id", flat=True)),
    }
