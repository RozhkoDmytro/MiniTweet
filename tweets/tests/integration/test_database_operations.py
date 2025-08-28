"""
Integration tests for database operations and data integrity
"""

import pytest
from django.contrib.auth.models import User
from django.db import transaction
from tweets.models import Tweet


@pytest.mark.django_db
@pytest.mark.integration
class DatabaseOperationsTest:
    """Test cases for database operations"""

    def test_basic_tweet_creation(self):
        """Test basic tweet creation"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        tweet = Tweet.objects.create(text="Test tweet", user=user)

        assert tweet.text == "Test tweet"
        assert tweet.user == user
        assert tweet.id is not None

    def test_tweet_with_reply(self):
        """Test tweet with reply creation"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        parent_tweet = Tweet.objects.create(text="Parent tweet", user=user)
        reply = Tweet.objects.create(
            text="Reply to parent", user=user, parent_tweet=parent_tweet
        )

        assert reply.parent_tweet == parent_tweet
        assert reply.text == "Reply to parent"

    def test_tweet_ordering(self):
        """Test tweet ordering by creation time"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        tweet1 = Tweet.objects.create(text="First tweet", user=user)
        tweet2 = Tweet.objects.create(text="Second tweet", user=user)

        # Get tweets ordered by creation time (newest first)
        tweets = Tweet.objects.all().order_by("-created_at")

        assert tweets[0] == tweet2
        assert tweets[1] == tweet1


@pytest.mark.django_db
@pytest.mark.integration
class DatabaseTransactionTest:
    """Test cases for database transactions"""

    def test_basic_transaction(self):
        """Test basic transaction"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        with transaction.atomic():
            tweet = Tweet.objects.create(text="Transaction tweet", user=user)
            assert tweet.id is not None

        # Tweet should exist after transaction
        assert Tweet.objects.filter(id=tweet.id).exists()
