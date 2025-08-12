from django import forms
from .models import Tweet


class TweetForm(forms.ModelForm):
    """Form for creating and editing tweets"""

    text = forms.CharField(
        label="Tweet Text",
        max_length=280,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "What's happening? (max 280 characters)",
                "maxlength": 280,
            }
        ),
    )

    image = forms.ImageField(
        label="Image (optional)",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )

    class Meta:
        model = Tweet
        fields = ["text", "image"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "What's happening? (max 280 characters)",
                    "maxlength": 280,
                }
            ),
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image file size must be under 5MB"
                )

            # Check file type
            allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if image.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Only JPEG, PNG, GIF and WebP images are allowed"
                )

        return image


class ReplyForm(forms.ModelForm):
    """Form for replying to tweets"""

    class Meta:
        model = Tweet
        fields = ["text", "image"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Reply to this tweet...",
                    "maxlength": 280,
                }
            ),
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image file size must be under 5MB"
                )

            # Check file type
            allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if image.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Only JPEG, PNG, GIF and WebP images are allowed"
                )

        return image
