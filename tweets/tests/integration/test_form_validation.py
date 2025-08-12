"""
Integration tests for form validation and error handling
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.exceptions import ValidationError
from tweets.models import Tweet
from tweets.forms import TweetForm, ReplyForm


class FormValidationIntegrationTest(TestCase):
    """Integration tests for form validation across the application"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_form_validation_in_views(self):
        """Test form validation integrated with views"""
        self.client.login(username="testuser", password="testpass123")

        # Test empty text validation
        response = self.client.post(reverse("tweets:tweet_create"), {"text": ""})
        self.assertEqual(response.status_code, 200)  # Should return to form
        self.assertContains(response, "Please correct the errors below")

        # Test text too long validation
        long_text = "x" * 281
        response = self.client.post(reverse("tweets:tweet_create"), {"text": long_text})
        self.assertEqual(response.status_code, 200)  # Should return to form

        # Test valid tweet creation
        response = self.client.post(
            reverse("tweets:tweet_create"), {"text": "Valid tweet text"}
        )
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Verify tweet was created
        tweet = Tweet.objects.get(text="Valid tweet text")
        self.assertEqual(tweet.user, self.user)

    def test_image_validation_in_views(self):
        """Test image validation integrated with views"""
        self.client.login(username="testuser", password="testpass123")

        # Test large image validation
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        large_image = SimpleUploadedFile(
            "large_image.jpg", large_content, content_type="image/jpeg"
        )

        response = self.client.post(
            reverse("tweets:tweet_create"),
            {"text": "Tweet with large image"},
            files={"image": large_image},
        )
        self.assertEqual(response.status_code, 200)  # Should return to form

        # Test invalid image type
        invalid_file = SimpleUploadedFile(
            "invalid.txt", b"invalid content", content_type="text/plain"
        )

        response = self.client.post(
            reverse("tweets:tweet_create"),
            {"text": "Tweet with invalid image"},
            files={"image": invalid_file},
        )
        self.assertEqual(response.status_code, 200)  # Should return to form

        # Test valid image
        valid_content = b"valid-image-content"
        valid_image = SimpleUploadedFile(
            "valid_image.png", valid_content, content_type="image/png"
        )

        response = self.client.post(
            reverse("tweets:tweet_create"),
            {"text": "Tweet with valid image"},
            files={"image": valid_image},
        )
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Verify tweet was created with image
        tweet = Tweet.objects.get(text="Tweet with valid image")
        self.assertIsNotNone(tweet.image)

    def test_form_validation_messages(self):
        """Test that validation error messages are displayed correctly"""
        self.client.login(username="testuser", password="testpass123")

        # Test empty text error message
        response = self.client.post(reverse("tweets:tweet_create"), {"text": ""})
        self.assertContains(response, "Please correct the errors below")

        # Test image error message
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        large_image = SimpleUploadedFile(
            "large_image.jpg", large_content, content_type="image/jpeg"
        )

        response = self.client.post(
            reverse("tweets:tweet_create"),
            {"text": "Tweet with large image"},
            files={"image": large_image},
        )
        self.assertContains(response, "Image file size must be under 5MB")

    def test_form_validation_persistence(self):
        """Test that form data persists after validation errors"""
        self.client.login(username="testuser", password="testpass123")

        # Submit form with invalid data
        response = self.client.post(
            reverse("tweets:tweet_create"),
            {"text": "Valid text but invalid image"},
            files={
                "image": SimpleUploadedFile(
                    "large.jpg", b"x" * (6 * 1024 * 1024), content_type="image/jpeg"
                )
            },
        )

        self.assertEqual(response.status_code, 200)

        # Check that form still contains the text
        form = response.context["form"]
        self.assertEqual(form.data.get("text"), "Valid text but invalid image")

    def test_reply_form_validation(self):
        """Test reply form validation integrated with views"""
        self.client.login(username="testuser", password="testpass123")

        # Create a parent tweet
        parent_tweet = Tweet.objects.create(
            text="Parent tweet for replies", user=self.user
        )

        # Test empty text in reply
        response = self.client.post(
            reverse("tweets:tweet_reply", kwargs={"pk": parent_tweet.pk}), {"text": ""}
        )
        self.assertEqual(response.status_code, 302)  # Should redirect back to detail

        # Test valid reply
        response = self.client.post(
            reverse("tweets:tweet_reply", kwargs={"pk": parent_tweet.pk}),
            {"text": "Valid reply text"},
        )
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Verify reply was created
        reply = Tweet.objects.get(text="Valid reply text")
        self.assertEqual(reply.parent_tweet, parent_tweet)

    def test_form_validation_edge_cases(self):
        """Test form validation edge cases"""
        self.client.login(username="testuser", password="testpass123")

        # Test text exactly at maximum length
        max_text = "x" * 280
        response = self.client.post(reverse("tweets:tweet_create"), {"text": max_text})
        self.assertEqual(response.status_code, 302)  # Should succeed

        # Test text one character over maximum
        over_max_text = "x" * 281
        response = self.client.post(
            reverse("tweets:tweet_create"), {"text": over_max_text}
        )
        self.assertEqual(response.status_code, 200)  # Should fail

        # Test image exactly at maximum size
        exact_size_content = b"x" * (5 * 1024 * 1024)  # 5MB
        exact_size_image = SimpleUploadedFile(
            "exact_size.jpg", exact_size_content, content_type="image/jpeg"
        )

        response = self.client.post(
            reverse("tweets:tweet_create"),
            {"text": "Tweet with exact size image"},
            files={"image": exact_size_image},
        )
        self.assertEqual(response.status_code, 302)  # Should succeed

    def test_form_validation_across_different_views(self):
        """Test that form validation is consistent across different views"""
        self.client.login(username="testuser", password="testpass123")

        # Create a tweet to test update
        tweet = Tweet.objects.create(text="Original tweet text", user=self.user)

        # Test validation in create view
        response = self.client.post(reverse("tweets:tweet_create"), {"text": ""})
        self.assertEqual(response.status_code, 200)

        # Test validation in update view
        response = self.client.post(
            reverse("tweets:tweet_update", kwargs={"pk": tweet.pk}), {"text": ""}
        )
        self.assertEqual(response.status_code, 200)

        # Test validation in list view (POST)
        response = self.client.post(reverse("tweets:tweet_list"), {"text": ""})
        self.assertEqual(response.status_code, 200)

    def test_form_validation_with_csrf(self):
        """Test form validation with CSRF protection"""
        self.client.login(username="testuser", password="testpass123")

        # Test that forms require CSRF token
        response = self.client.post(
            reverse("tweets:tweet_create"),
            {"text": "Valid tweet text"},
            HTTP_X_CSRFTOKEN="invalid_token",
        )

        # Should fail due to CSRF validation
        self.assertEqual(response.status_code, 403)

    def test_form_validation_performance(self):
        """Test form validation performance with large datasets"""
        self.client.login(username="testuser", password="testpass123")

        # Create many tweets to test performance
        for i in range(100):
            Tweet.objects.create(text=f"Tweet {i}", user=self.user)

        # Test that list view still performs well
        response = self.client.get(reverse("tweets:tweet_list"))
        self.assertEqual(response.status_code, 200)

        # Test that form submission still works
        response = self.client.post(
            reverse("tweets:tweet_create"), {"text": "Performance test tweet"}
        )
        self.assertEqual(response.status_code, 302)

    def test_form_validation_error_recovery(self):
        """Test that users can recover from validation errors"""
        self.client.login(username="testuser", password="testpass123")

        # Submit invalid form
        response = self.client.post(reverse("tweets:tweet_create"), {"text": ""})
        self.assertEqual(response.status_code, 200)

        # Correct the error and resubmit
        response = self.client.post(
            reverse("tweets:tweet_create"), {"text": "Corrected tweet text"}
        )
        self.assertEqual(response.status_code, 302)

        # Verify tweet was created
        tweet = Tweet.objects.get(text="Corrected tweet text")
        self.assertEqual(tweet.user, self.user)

    def test_form_validation_integration_with_models(self):
        """Test that form validation integrates properly with model validation"""
        self.client.login(username="testuser", password="testpass123")

        # Test that form validation catches model validation errors
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        large_image = SimpleUploadedFile(
            "large_image.jpg", large_content, content_type="image/jpeg"
        )

        # This should fail at form level
        response = self.client.post(
            reverse("tweets:tweet_create"),
            {"text": "Tweet with large image"},
            files={"image": large_image},
        )
        self.assertEqual(response.status_code, 200)

        # Verify no tweet was created
        with self.assertRaises(Tweet.DoesNotExist):
            Tweet.objects.get(text="Tweet with large image")

    def test_form_validation_cross_browser_compatibility(self):
        """Test form validation with different content types and encodings"""
        self.client.login(username="testuser", password="testpass123")

        # Test with different content types
        content_types = [
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]

        for content_type in content_types:
            with self.subTest(content_type=content_type):
                if content_type == "multipart/form-data":
                    # Test with file upload
                    image_content = b"valid-image-content"
                    image = SimpleUploadedFile(
                        "test_image.jpg", image_content, content_type="image/jpeg"
                    )

                    response = self.client.post(
                        reverse("tweets:tweet_create"),
                        {"text": f"Tweet with {content_type}"},
                        files={"image": image},
                        content_type=content_type,
                    )
                else:
                    response = self.client.post(
                        reverse("tweets:tweet_create"),
                        {"text": f"Tweet with {content_type}"},
                        content_type=content_type,
                    )

                # Should succeed in both cases
                self.assertEqual(response.status_code, 302)
