from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Tweet(models.Model):
    # Basic tweet fields
    text = models.CharField(max_length=280)
    image = models.ImageField(upload_to="tweets/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # User and reply functionality
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tweets", default=1
    )
    parent_tweet = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    # Image validation and processing
    def clean(self):
        if self.image and self.image.size > 5 * 1024 * 1024:  # 5MB limit
            raise ValidationError("Image file size must be under 5MB")

    def save(self, *args, **kwargs):
        # Validate before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}"

    class Meta:
        ordering = ["-created_at"]
