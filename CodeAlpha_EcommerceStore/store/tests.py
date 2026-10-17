from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, Product


class StoreFlowTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Gadgets")
        self.p1 = Product.objects.create(
            category=self.cat, name="Widget", price=Decimal("100.00"), stock=5
        )
        self.p2 = Product.objects.create(
            category=self.cat, name="Gizmo", price=Decimal("50.50"), stock=2
        )

    def test_list_and_detail_pages(self):
        r = self.client.get(reverse("product_list"))
        self.assertContains(r, "Widget")
        r = self.client.get(self.p1.get_absolute_url())
        self.assertEqual(r.status_code, 200)

    def test_category_menu_and_subcategories(self):
        audio = Category.objects.create(name="Audio", parent=self.cat)
        buds = Product.objects.create(
            category=audio, name="Buds", price=Decimal("10.00"), stock=1
        )
        # Menu bar lists the parent with its subcategory on every page.
        home = self.client.get(reverse("product_list"))
        self.assertContains(home, 'class="catbar"')
        self.assertContains(home, reverse("category", args=[audio.slug]))
        # Opening the parent shows its own products AND its subcategory's products.
        r = self.client.get(reverse("category", args=[self.cat.slug]))
        self.assertContains(r, "Widget")
        self.assertContains(r, "Buds")
        # Opening the subcategory shows only its own products.
        r = self.client.get(reverse("category", args=[audio.slug]))
        self.assertContains(r, "Buds")
        self.assertNotContains(r, "Widget")

    def test_only_one_subcategory_level(self):
        from django.core.exceptions import ValidationError

        sub = Category.objects.create(name="Sub", parent=self.cat)
        deeper = Category(name="Deeper", parent=sub)
        with self.assertRaises(ValidationError):
            deeper.full_clean()

    def test_picture_ignores_old_placeholder_photos(self):
        p = Product.objects.create(
            category=self.cat, name="Cricket Bat", price=Decimal("10.00"), stock=1,
            image_url="https://picsum.photos/seed/cricket-bat/600/450",
        )
        self.assertIn("/static/store/products/cricket-bat.svg", p.picture)
        p.image_url = "https://example.com/real-photo.jpg"
        self.assertEqual(p.picture, "https://example.com/real-photo.jpg")

    def test_footer_links_all_resolve(self):
        import re
        from .pages import PAGES

        home = self.client.get(reverse("product_list")).content.decode()
        self.assertIn('class="site-footer"', home)
        slugs = set(re.findall(r'href="/info/([\w-]+)/"', home))
        self.assertTrue(slugs)  # the footer links to info pages
        for slug in slugs:
            self.assertIn(slug, PAGES, f"footer links to unknown page {slug}")
        for slug in PAGES:
            self.assertEqual(self.client.get(reverse("info_page", args=[slug])).status_code, 200)

    def test_unknown_info_page_404_and_sitemap_lists_categories(self):
        self.assertEqual(self.client.get("/info/nope/").status_code, 404)
        r = self.client.get(reverse("info_page", args=["sitemap"]))
        self.assertContains(r, "Gadgets")

    def test_for_you_home_page(self):
        # A category matching one of the built-in ads, so a banner is shown.
        elec = Category.objects.create(name="Electronics", emoji="📱")
        Product.objects.create(category=elec, name="Cheap Gadget", price=Decimal("299.00"), stock=3)
        r = self.client.get(reverse("for_you"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(reverse("for_you"), "/")
        self.assertContains(r, "For You")
        self.assertContains(r, "hero-track")          # ad carousel
        self.assertContains(r, "From ₹299")           # banner price comes from real data
        self.assertContains(r, "Under ₹999")          # budget strip
        self.assertContains(r, "Shop by category")

    def test_for_you_works_with_no_products(self):
        Product.objects.all().delete()
        self.assertEqual(self.client.get(reverse("for_you")).status_code, 200)

    def test_all_products_lives_at_products_url(self):
        self.assertEqual(reverse("product_list"), "/products/")
        self.assertContains(self.client.get("/products/"), "Widget")

    def test_category_emoji_shown_in_menu_and_heading(self):
        cat = Category.objects.create(name="Books", emoji="📚")
        home = self.client.get(reverse("for_you"))
        self.assertContains(home, '<span class="ci">📚</span>')
        page = self.client.get(reverse("category", args=[cat.slug]))
        self.assertContains(page, "📚 Books")
        # A category without an emoji falls back to a default icon.
        self.assertEqual(Category.objects.create(name="Misc").icon, "🛍️")

    def test_search(self):
        r = self.client.get(reverse("product_list"), {"q": "gizmo"})
        self.assertContains(r, "Gizmo")
        self.assertNotContains(r, "Widget")

    def test_cart_add_update_remove(self):
        self.client.post(reverse("cart_add", args=[self.p1.id]), {"quantity": 2})
        r = self.client.get(reverse("cart_detail"))
        self.assertContains(r, "200.00")
        self.client.post(
            reverse("cart_add", args=[self.p1.id]), {"quantity": 3, "override": "1"}
        )
        self.assertContains(self.client.get(reverse("cart_detail")), "300.00")
        self.client.post(reverse("cart_remove", args=[self.p1.id]))
        self.assertContains(self.client.get(reverse("cart_detail")), "empty")

    def test_cart_quantity_capped_at_stock(self):
        self.client.post(reverse("cart_add", args=[self.p2.id]), {"quantity": 99})
        self.assertEqual(self.client.session["cart"][str(self.p2.id)], 2)

    def test_ajax_add_returns_json(self):
        r = self.client.post(
            reverse("cart_add", args=[self.p1.id]),
            {"quantity": 1},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        self.assertEqual(r.json()["count"], 1)

    def test_checkout_requires_login(self):
        self.client.post(reverse("cart_add", args=[self.p1.id]), {"quantity": 1})
        r = self.client.get(reverse("checkout"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r["Location"])

    def test_register_then_full_order(self):
        r = self.client.post(
            reverse("register"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "password1": "S3cure-pass-9",
                "password2": "S3cure-pass-9",
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username="alice").exists())

        self.client.post(reverse("cart_add", args=[self.p1.id]), {"quantity": 2})
        self.client.post(reverse("cart_add", args=[self.p2.id]), {"quantity": 1})
        r = self.client.post(
            reverse("checkout"),
            {
                "full_name": "Alice A",
                "email": "alice@example.com",
                "address": "1 Main St",
                "city": "Ludhiana",
                "postal_code": "141001",
            },
        )
        order = Order.objects.get()
        self.assertRedirects(r, reverse("order_success", args=[order.id]))
        self.assertEqual(order.total, Decimal("250.50"))
        self.p1.refresh_from_db()
        self.p2.refresh_from_db()
        self.assertEqual((self.p1.stock, self.p2.stock), (3, 1))
        self.assertEqual(len(self.client.session.get("cart", {})), 0)
        self.assertContains(self.client.get(reverse("order_history")), f"#{order.id}")

    def test_duplicate_email_rejected(self):
        User.objects.create_user("bob", "bob@example.com", "pw")
        r = self.client.post(
            reverse("register"),
            {
                "username": "bob2",
                "email": "BOB@example.com",
                "password1": "S3cure-pass-9",
                "password2": "S3cure-pass-9",
            },
        )
        self.assertContains(r, "already exists")

    def test_users_cannot_view_others_orders(self):
        owner = User.objects.create_user("owner", "o@example.com", "pw")
        order = Order.objects.create(
            user=owner, full_name="O", email="o@example.com",
            address="x", city="y", postal_code="1",
        )
        User.objects.create_user("intruder", "i@example.com", "pw")
        self.client.login(username="intruder", password="pw")
        r = self.client.get(reverse("order_success", args=[order.id]))
        self.assertEqual(r.status_code, 404)


class AccountTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Gadgets")
        self.p1 = Product.objects.create(category=self.cat, name="Widget", price=Decimal("100.00"), stock=5)
        self.p2 = Product.objects.create(category=self.cat, name="Gizmo", price=Decimal("50.00"), stock=5)
        self.user = User.objects.create_user("asha", "asha@example.com", "pw-12345", first_name="Asha")
        self.client.login(username="asha", password="pw-12345")

    ADDR = {"full_name": "Asha K", "phone": "9876543210", "address": "1 Main St", "city": "Mohali", "postal_code": "160062"}

    # ----- dropdown -----
    def test_account_dropdown_for_logged_in_user_only(self):
        r = self.client.get(reverse("for_you"))
        self.assertContains(r, "Your Account")
        for label in ["My Profile", "Orders", "Coupons", "Saved Addresses", "Wishlist", "Gift Cards", "Notifications", "Logout"]:
            self.assertContains(r, label)
        self.client.logout()
        r = self.client.get(reverse("for_you"))
        self.assertNotContains(r, "Your Account")
        self.assertContains(r, "Login")

    def test_all_account_pages_need_login_and_render(self):
        for name in ["account_profile", "account_addresses", "account_wishlist", "account_notifications", "account_coupons", "order_history"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.client.logout()
        for name in ["account_profile", "account_addresses", "account_wishlist", "account_notifications", "account_coupons"]:
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302, name)
            self.assertIn("/accounts/login/", r["Location"])

    # ----- profile -----
    def test_profile_update_and_duplicate_email(self):
        r = self.client.post(reverse("account_profile"), {"first_name": "Asha", "last_name": "Kaur", "email": "NEW@example.com"})
        self.assertRedirects(r, reverse("account_profile"))
        self.user.refresh_from_db()
        self.assertEqual((self.user.last_name, self.user.email), ("Kaur", "new@example.com"))
        User.objects.create_user("bob", "bob@example.com", "pw")
        r = self.client.post(reverse("account_profile"), {"first_name": "A", "last_name": "K", "email": "bob@example.com"})
        self.assertContains(r, "already uses this email")

    # ----- addresses -----
    def test_first_address_is_default_and_default_switches(self):
        self.client.post(reverse("account_addresses"), self.ADDR)
        first = self.user.addresses.get()
        self.assertTrue(first.is_default)
        self.client.post(reverse("account_addresses"), {**self.ADDR, "address": "2 Side Rd", "is_default": "on"})
        first.refresh_from_db()
        self.assertFalse(first.is_default)
        self.assertEqual(self.user.addresses.filter(is_default=True).count(), 1)
        self.assertEqual(self.user.addresses.first().address, "2 Side Rd")

    def test_delete_default_promotes_another_and_other_users_are_protected(self):
        self.client.post(reverse("account_addresses"), self.ADDR)
        self.client.post(reverse("account_addresses"), {**self.ADDR, "address": "2 Side Rd", "is_default": "on"})
        default = self.user.addresses.get(is_default=True)
        self.client.post(reverse("address_delete", args=[default.id]))
        self.assertEqual(self.user.addresses.count(), 1)
        self.assertTrue(self.user.addresses.get().is_default)
        other = User.objects.create_user("eve", "eve@example.com", "pw")
        from .models import Address
        theirs = Address.objects.create(user=other, **self.ADDR)
        self.assertEqual(self.client.post(reverse("address_delete", args=[theirs.id])).status_code, 404)
        self.assertEqual(self.client.post(reverse("address_make_default", args=[theirs.id])).status_code, 404)

    def test_checkout_prefilled_from_default_address(self):
        self.client.post(reverse("account_addresses"), self.ADDR)
        self.client.post(reverse("cart_add", args=[self.p1.id]), {"quantity": 1})
        r = self.client.get(reverse("checkout"))
        self.assertContains(r, "1 Main St")
        self.assertContains(r, "160062")

    # ----- wishlist -----
    def test_wishlist_toggle_add_remove_and_listing(self):
        url = reverse("wishlist_toggle", args=[self.p1.id])
        r = self.client.post(url, headers={"X-Requested-With": "XMLHttpRequest"})
        self.assertEqual(r.json()["on"], True)
        self.assertContains(self.client.get(reverse("account_wishlist")), "Widget")
        self.assertContains(self.client.get(reverse("product_list")), 'wish-btn on')
        r = self.client.post(url, headers={"X-Requested-With": "XMLHttpRequest"})
        self.assertEqual(r.json()["on"], False)
        self.assertEqual(self.user.wishlist.count(), 0)
        self.assertContains(self.client.get(reverse("account_wishlist")), "wishlist is empty")

    def test_wishlist_requires_login_and_post_and_safe_redirect(self):
        url = reverse("wishlist_toggle", args=[self.p1.id])
        self.assertEqual(self.client.get(url).status_code, 405)
        r = self.client.post(url, {"next": "//evil.example/x"})
        self.assertRedirects(r, reverse("account_wishlist"))
        r = self.client.post(url, {"next": "/products/"})
        self.assertRedirects(r, "/products/")
        self.client.logout()
        r = self.client.post(url)
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r["Location"])
        self.assertContains(self.client.get(reverse("product_list")), "/accounts/login/?next=")

    # ----- notifications / coupons -----
    def test_notifications_list_orders(self):
        from .models import Order, OrderItem
        o = Order.objects.create(user=self.user, full_name="A", email="a@example.com", address="x", city="y", postal_code="1")
        OrderItem.objects.create(order=o, product=self.p1, price=Decimal("100.00"), quantity=2)
        r = self.client.get(reverse("account_notifications"))
        self.assertContains(r, f"Order #{o.id} is pending")
        self.assertContains(r, "₹200.00")
        self.assertContains(self.client.get(reverse("account_coupons")), "no coupons")
