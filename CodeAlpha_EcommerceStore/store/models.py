from decimal import Decimal
from functools import lru_cache

from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


@lru_cache(maxsize=512)
def _bundled_illustration(slug):
    """Static URL of the illustration for this product slug, or '' if none exists."""
    path = f"store/products/{slug}.svg"
    return static(path) if finders.find(path) else ""


class Category(models.Model):
    """A category, optionally nested one level under a parent (subcategory)."""

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        help_text="Leave empty for a top-level category.",
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    emoji = models.CharField(
        max_length=8, blank=True, help_text="Icon shown next to the name, e.g. 📚"
    )

    @property
    def icon(self):
        return self.emoji or "🛍️"

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"], name="unique_category_name_per_parent"
            )
        ]

    def clean(self):
        if self.parent_id and self.parent.parent_id:
            raise ValidationError("Only one level of subcategories is supported.")
        if self.parent_id and self.parent_id == self.pk:
            raise ValidationError("A category cannot be its own parent.")

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent.name} › {self.name}" if self.parent_id else self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])

    @property
    def picture(self):
        """Uploaded image, else an explicit URL, else the bundled illustration
        (store/static/store/products/<slug>.svg) that matches the product name."""
        if self.image:
            return self.image.url
        # Old sample data used random picsum.photos images that never matched the
        # product, so they are ignored; any other explicit URL is respected.
        if self.image_url and "picsum.photos" not in self.image_url:
            return self.image_url
        return _bundled_illustration(self.slug)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    @property
    def total(self):
        return sum((i.line_total for i in self.items.all()), Decimal("0.00"))

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.PROTECT
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Address(models.Model):
    """A saved delivery address."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="addresses", on_delete=models.CASCADE
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created"]
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.full_name}, {self.address}, {self.city}"


class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="wishlist", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="wishlisted_by", on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_wishlist_item")
        ]

    def __str__(self):
        return f"{self.user} ♥ {self.product}"
