from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .ads import HERO_ADS, WIDE_ADS, build_ads
from .cart import Cart
from .forms import AddressForm, CheckoutForm, ProfileForm, RegisterForm
from .models import Address, Category, Order, OrderItem, Product, WishlistItem
from .pages import PAGES


def for_you(request):
    """Home page: offer banners, a budget strip, and a fresh set of picks."""
    in_stock = Product.objects.filter(available=True, stock__gt=0).select_related("category")
    return render(
        request,
        "store/for_you.html",
        {
            "hero_ads": build_ads(HERO_ADS),
            "wide_ads": build_ads(WIDE_ADS),
            "budget": in_stock.filter(price__lte=999).order_by("price")[:14],
            "picks": in_stock.order_by("?")[:10],
        },
    )


def product_list(request, category_slug=None):
    products = Product.objects.filter(available=True).select_related("category")
    category = None
    subcategories = []
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        # A parent category also shows the products of its subcategories.
        products = products.filter(Q(category=category) | Q(category__parent=category))
        subcategories = category.children.all()

    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))

    sort = request.GET.get("sort", "")
    ordering = {
        "price_asc": "price",
        "price_desc": "-price",
        "name": "name",
    }.get(sort)
    if ordering:
        products = products.order_by(ordering)

    page = Paginator(products, 12).get_page(request.GET.get("page"))
    return render(
        request,
        "store/product_list.html",
        {
            "category": category,
            "subcategories": subcategories,
            "page": page,
            "q": q,
            "sort": sort,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related = (
        Product.objects.filter(category=product.category, available=True)
        .exclude(pk=product.pk)[:4]
    )
    return render(
        request, "store/product_detail.html", {"product": product, "related": related}
    )


# ---------- Cart ----------

def cart_detail(request):
    return render(request, "store/cart.html", {"cart": Cart(request)})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = Cart(request)
    try:
        qty = int(request.POST.get("quantity", 1))
    except ValueError:
        qty = 1
    override = request.POST.get("override") == "1"
    cart.add(product, quantity=qty, override=override)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "ok": True,
                "count": len(cart),
                "total": f"{cart.total():.2f}",
                "message": f"{product.name} added to cart",
            }
        )
    messages.success(request, f"{product.name} added to cart.")
    return redirect(request.POST.get("next") or "cart_detail")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Cart(request).remove(product)
    return redirect("cart_detail")


# ---------- Auth ----------

def register(request):
    if request.user.is_authenticated:
        return redirect("for_you")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.username}! Your account is ready.")
        return redirect("for_you")
    return render(request, "registration/register.html", {"form": form})


# ---------- Checkout / orders ----------

@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, "Your cart is empty.")
        return redirect("for_you")

    initial = {"email": request.user.email, "full_name": request.user.get_full_name()}
    saved = request.user.addresses.first()  # default address sorts first
    if saved:
        initial.update(
            full_name=saved.full_name, address=saved.address,
            city=saved.city, postal_code=saved.postal_code,
        )
    form = CheckoutForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.save()
                for line in cart:
                    product = Product.objects.select_for_update().get(
                        pk=line["product"].pk
                    )
                    qty = line["quantity"]
                    if qty > product.stock:
                        raise ValueError(
                            f"Sorry, only {product.stock} of {product.name} left."
                        )
                    OrderItem.objects.create(
                        order=order, product=product, price=product.price, quantity=qty
                    )
                    Product.objects.filter(pk=product.pk).update(
                        stock=F("stock") - qty
                    )
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("cart_detail")

        cart.clear()
        return redirect("order_success", order_id=order.id)

    return render(request, "store/checkout.html", {"cart": cart, "form": form})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "store/order_success.html", {"order": order})


@login_required
def order_history(request):
    orders = request.user.orders.prefetch_related("items__product")
    return render(request, "store/order_history.html", {"orders": orders})


# ---------- Footer info pages ----------

def info_page(request, slug):
    if slug not in PAGES:
        raise Http404("Page not found")
    title, paragraphs = PAGES[slug]
    return render(
        request,
        "store/info_page.html",
        {"title": title, "paragraphs": paragraphs, "is_sitemap": slug == "sitemap"},
    )


# ---------- Account ----------

@login_required
def account_profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("account_profile")
    return render(request, "store/account/profile.html", {"form": form})


@login_required
def account_addresses(request):
    form = AddressForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        # The first address is always the default.
        address.is_default = address.is_default or not request.user.addresses.exists()
        if address.is_default:
            request.user.addresses.update(is_default=False)
        address.save()
        messages.success(request, "Address saved.")
        return redirect("account_addresses")
    return render(
        request,
        "store/account/addresses.html",
        {"form": form, "addresses": request.user.addresses.all()},
    )


@login_required
@require_POST
def address_delete(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    was_default = address.is_default
    address.delete()
    if was_default:
        nxt = request.user.addresses.first()
        if nxt:
            nxt.is_default = True
            nxt.save(update_fields=["is_default"])
    messages.success(request, "Address removed.")
    return redirect("account_addresses")


@login_required
@require_POST
def address_make_default(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    request.user.addresses.update(is_default=False)
    address.is_default = True
    address.save(update_fields=["is_default"])
    return redirect("account_addresses")


@login_required
def account_wishlist(request):
    items = request.user.wishlist.select_related("product__category")
    return render(request, "store/account/wishlist.html", {"products": [i.product for i in items]})


@login_required
@require_POST
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
    on = created
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "on": on, "message": f"{'Added to' if on else 'Removed from'} wishlist"})
    messages.success(request, f"{product.name} {'added to' if on else 'removed from'} your wishlist.")
    nxt = request.POST.get("next", "")
    return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else "account_wishlist")


@login_required
def account_notifications(request):
    orders = request.user.orders.prefetch_related("items")
    return render(request, "store/account/notifications.html", {"orders": orders})


@login_required
def account_coupons(request):
    return render(request, "store/account/coupons.html")
