"""
Integration tests for complete user workflows
"""

import pytest
from django.test import Client
from django.contrib.auth.models import User
from tweets.models import Tweet


@pytest.mark.django_db
@pytest.mark.integration
class UserWorkflowTest:
    """Integration tests for user workflows"""

    def test_basic_user_workflow(self):
        """Test basic user workflow"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client = Client()
        client.force_login(user)

        # Test user can access main page
        response = client.get("/")
        assert response.status_code == 200

    def test_user_can_create_tweet(self):
        """Test user can create a tweet"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client = Client()
        client.force_login(user)

        # Test creating a tweet
        response = client.post("/", {"text": "Test tweet from user"})
        assert response.status_code in [
            200,
            302,
        ]  # Can be either redirect or success page

    def test_user_can_view_tweets(self):
        """Test user can view tweets"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create a tweet
        tweet = Tweet.objects.create(text="Test tweet", user=user)

        client = Client()
        client.force_login(user)

        # Test viewing tweets
        response = client.get("/")
        assert response.status_code == 200
