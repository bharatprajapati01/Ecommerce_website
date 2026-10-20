from django.contrib import admin

from .models import Bookmark, Category, Comment, Follow, Like, Message, Notification, Post, Profile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(Bookmark)
admin.site.register(Notification)
admin.site.register(Message)
