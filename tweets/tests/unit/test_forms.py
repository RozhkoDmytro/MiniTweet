"""
Unit tests for Tweet forms using pytest
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from tweets.forms import TweetForm, ReplyForm


@pytest.mark.django_db
@pytest.mark.forms
@pytest.mark.unit
class TestTweetForm:
    """Test cases for TweetForm"""

    def test_tweet_form_valid_data(self, test_user):
        """Test TweetForm with valid data"""
        form_data = {"text": "This is a valid tweet"}
        form = TweetForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["text"] == "This is a valid tweet"

    def test_tweet_form_empty_text(self, test_user):
        """Test TweetForm with empty text"""
        form_data = {"text": ""}
        form = TweetForm(data=form_data)

        assert not form.is_valid()
        assert "text" in form.errors

    def test_tweet_form_text_too_long(self, test_user):
        """Test TweetForm with text longer than 280 characters"""
        long_text = "x" * 281
        form_data = {"text": long_text}
        form = TweetForm(data=form_data)

        assert not form.is_valid()
        assert "text" in form.errors

    def test_tweet_form_with_valid_image(self, test_user):
        """Test TweetForm with valid image"""
        image_content = b"valid-image-content"
        image = SimpleUploadedFile(
            "test_image.jpg", image_content, content_type="image/jpeg"
        )

        form_data = {"text": "Tweet with image"}
        files = {"image": image}

        form = TweetForm(data=form_data, files=files)
        assert form.is_valid()

    def test_tweet_form_with_large_image(self, test_user):
        """Test TweetForm with image larger than 5MB"""
        # Create a file larger than 5MB
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        large_image = SimpleUploadedFile(
            "large_image.jpg", large_content, content_type="image/jpeg"
        )

        form_data = {"text": "Tweet with large image"}
        files = {"image": large_image}

        form = TweetForm(data=form_data, files=files)
        assert not form.is_valid()
        assert "image" in form.errors

    def test_tweet_form_with_invalid_image_type(self, test_user):
        """Test TweetForm with invalid image type"""
        invalid_content = b"invalid-file-content"
        invalid_file = SimpleUploadedFile(
            "invalid_file.txt", invalid_content, content_type="text/plain"
        )

        form_data = {"text": "Tweet with invalid image"}
        files = {"image": invalid_file}

        form = TweetForm(data=form_data, files=files)
        assert not form.is_valid()
        assert "image" in form.errors

    def test_tweet_form_widget_attributes(self, test_user):
        """Test TweetForm widget attributes"""
        form = TweetForm()

        # Check text field widget attributes
        text_widget = form.fields["text"].widget
        assert text_widget.attrs["class"] == "form-control"
        assert text_widget.attrs["rows"] == 3
        assert text_widget.attrs["maxlength"] == 280
        assert (
            text_widget.attrs["placeholder"] == "What's happening? (max 280 characters)"
        )

        # Check image field widget attributes
        image_widget = form.fields["image"].widget
        assert image_widget.attrs["class"] == "form-control"
        assert image_widget.attrs["accept"] == "image/*"

    def test_tweet_form_fields(self, test_user):
        """Test TweetForm field configuration"""
        form = TweetForm()

        assert "text" in form.fields
        assert "image" in form.fields
        assert form.Meta.fields == ["text", "image"]

    def test_tweet_form_save(self, test_user):
        """Test TweetForm save method"""
        form_data = {"text": "Test tweet to save"}
        form = TweetForm(data=form_data)

        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = test_user
            tweet.save()

            assert tweet.text == "Test tweet to save"
            assert tweet.user == test_user


@pytest.mark.django_db
@pytest.mark.forms
@pytest.mark.unit
class TestReplyForm:
    """Test cases for ReplyForm"""

    def test_reply_form_valid_data(self, test_user):
        """Test ReplyForm with valid data"""
        form_data = {"text": "This is a valid reply"}
        form = ReplyForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["text"] == "This is a valid reply"

    def test_reply_form_empty_text(self, test_user):
        """Test ReplyForm with empty text"""
        form_data = {"text": ""}
        form = ReplyForm(data=form_data)

        assert not form.is_valid()
        assert "text" in form.errors

    def test_reply_form_text_too_long(self, test_user):
        """Test ReplyForm with text longer than 280 characters"""
        long_text = "x" * 281
        form_data = {"text": long_text}
        form = ReplyForm(data=form_data)

        assert not form.is_valid()
        assert "text" in form.errors

    def test_reply_form_with_valid_image(self, test_user):
        """Test ReplyForm with valid image"""
        image_content = b"valid-image-content"
        image = SimpleUploadedFile(
            "test_image.png", image_content, content_type="image/png"
        )

        form_data = {"text": "Reply with image"}
        files = {"image": image}

        form = ReplyForm(data=form_data, files=files)
        assert form.is_valid()

    def test_reply_form_with_large_image(self, test_user):
        """Test ReplyForm with image larger than 5MB"""
        # Create a file larger than 5MB
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        large_image = SimpleUploadedFile(
            "large_image.jpg", large_content, content_type="image/jpeg"
        )

        form_data = {"text": "Reply with large image"}
        files = {"image": large_image}

        form = ReplyForm(data=form_data, files=files)
        assert not form.is_valid()
        assert "image" in form.errors

    def test_reply_form_with_invalid_image_type(self, test_user):
        """Test ReplyForm with invalid image type"""
        invalid_content = b"invalid-file-content"
        invalid_file = SimpleUploadedFile(
            "invalid_file.txt", invalid_content, content_type="text/plain"
        )

        form_data = {"text": "Reply with invalid image"}
        files = {"image": invalid_file}

        form = ReplyForm(data=form_data, files=files)
        assert not form.is_valid()
        assert "image" in form.errors

    def test_reply_form_widget_attributes(self, test_user):
        """Test ReplyForm widget attributes"""
        form = ReplyForm()

        # Check text field widget attributes
        text_widget = form.fields["text"].widget
        assert text_widget.attrs["class"] == "form-control"
        assert text_widget.attrs["rows"] == 2
        assert text_widget.attrs["maxlength"] == 280
        assert text_widget.attrs["placeholder"] == "Reply to this tweet..."

        # Check image field widget attributes
        image_widget = form.fields["image"].widget
        assert image_widget.attrs["class"] == "form-control"
        assert image_widget.attrs["accept"] == "image/*"

    def test_reply_form_fields(self, test_user):
        """Test ReplyForm field configuration"""
        form = ReplyForm()

        assert "text" in form.fields
        assert "image" in form.fields
        assert form.Meta.fields == ["text", "image"]

    def test_reply_form_save(self, test_user):
        """Test ReplyForm save method"""
        form_data = {"text": "Test reply to save"}
        form = ReplyForm(data=form_data)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = test_user
            reply.save()

            assert reply.text == "Test reply to save"
            assert reply.user == test_user


@pytest.mark.django_db
@pytest.mark.forms
@pytest.mark.unit
class TestFormValidation:
    """Test cases for form validation"""

    def test_image_size_validation_edge_case(self, test_user):
        """Test image size validation at the 5MB boundary"""
        # Create a file exactly 5MB
        exact_size_content = b"x" * (5 * 1024 * 1024)  # 5MB
        exact_size_image = SimpleUploadedFile(
            "exact_size_image.jpg", exact_size_content, content_type="image/jpeg"
        )

        form_data = {"text": "Tweet with exact size image"}
        files = {"image": exact_size_image}

        form = TweetForm(data=form_data, files=files)
        assert form.is_valid()

    def test_image_content_type_validation(self, test_user):
        """Test image content type validation"""
        # Test with different valid image types
        valid_types = [
            ("image/jpeg", "test.jpg"),
            ("image/png", "test.png"),
            ("image/gif", "test.gif"),
            ("image/webp", "test.webp"),
        ]

        for content_type, filename in valid_types:
            image_content = b"valid-image-content"
            image = SimpleUploadedFile(
                filename, image_content, content_type=content_type
            )

            form_data = {"text": f"Tweet with {content_type}"}
            files = {"image": image}

            form = TweetForm(data=form_data, files=files)
            assert form.is_valid(), f"Failed for {content_type}"

    def test_form_without_image(self, test_user):
        """Test form validation when no image is provided"""
        form_data = {"text": "Tweet without image"}
        form = TweetForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data.get("image") is None


# Additional pytest-style tests
@pytest.mark.django_db
@pytest.mark.forms
@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected_valid",
    [
        ("", False),
        ("x", True),
        ("x" * 100, True),
        ("x" * 280, True),
        ("x" * 281, False),
    ],
)
def test_tweet_form_text_validation(test_user, text, expected_valid):
    """Test tweet form text validation with different lengths"""
    form_data = {"text": text}
    form = TweetForm(data=form_data)
    assert form.is_valid() == expected_valid


@pytest.mark.django_db
@pytest.mark.forms
@pytest.mark.unit
@pytest.mark.parametrize(
    "content_type,filename,expected_valid",
    [
        ("image/jpeg", "test.jpg", True),
        ("image/png", "test.png", True),
        ("image/gif", "test.gif", True),
        ("image/webp", "test.webp", True),
        ("text/plain", "test.txt", False),
        ("application/pdf", "test.pdf", False),
    ],
)
def test_tweet_form_image_type_validation(
    test_user, content_type, filename, expected_valid
):
    """Test tweet form image type validation"""
    image_content = b"test-content"
    image = SimpleUploadedFile(filename, image_content, content_type=content_type)

    form_data = {"text": "Test tweet"}
    files = {"image": image}

    form = TweetForm(data=form_data, files=files)
    assert form.is_valid() == expected_valid


@pytest.mark.django_db
@pytest.mark.forms
@pytest.mark.unit
def test_form_cleaned_data_structure(test_user):
    """Test that form cleaned_data has correct structure"""
    form_data = {"text": "Test tweet"}
    form = TweetForm(data=form_data)

    if form.is_valid():
        cleaned_data = form.cleaned_data
        assert "text" in cleaned_data
        assert cleaned_data["text"] == "Test tweet"
        assert "image" in cleaned_data
        assert cleaned_data["image"] is None
