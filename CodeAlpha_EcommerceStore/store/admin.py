from django.contrib import admin

from .models import Address, Category, Order, OrderItem, Product, WishlistItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["__str__", "emoji", "parent", "slug"]
    list_editable = ["emoji"]
    list_filter = ["parent"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "available"]
    list_filter = ["available", "category"]
    list_editable = ["price", "stock", "available"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "status", "created"]
    list_filter = ["status", "created"]
    list_editable = ["status"]
    inlines = [OrderItemInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["full_name", "user", "city", "postal_code", "is_default"]
    search_fields = ["full_name", "user__username", "city"]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "created"]
