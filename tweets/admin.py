from django.contrib import admin
from .models import Tweet


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ("user", "text", "created_at", "parent_tweet", "has_image")
    list_filter = ("created_at", "user", "parent_tweet")
    search_fields = ("text", "user__username")
    readonly_fields = ("created_at", "updated_at")

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = "Has Image"
