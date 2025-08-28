"""
Integration tests for form validation and error handling
"""

import pytest
from django.test import Client
from django.contrib.auth.models import User
from tweets.models import Tweet


@pytest.mark.django_db
@pytest.mark.integration
class FormValidationIntegrationTest:
    """Integration tests for form validation"""

    def test_basic_form_submission(self):
        """Test basic form submission"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client = Client()
        client.force_login(user)

        # Test GET request to form
        response = client.get("/")
        assert response.status_code == 200

    def test_form_with_valid_data(self):
        """Test form with valid data"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client = Client()
        client.force_login(user)

        # Test POST with valid data
        response = client.post("/", {"text": "Valid tweet text"})
        assert response.status_code in [
            200,
            302,
        ]  # Can be either redirect or success page

    def test_form_with_empty_data(self):
        """Test form with empty data"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client = Client()
        client.force_login(user)

        # Test POST with empty text
        response = client.post("/", {"text": ""})
        assert response.status_code == 200  # Should return to form with errors
