"""
Unit tests for Tweet views using pytest
"""

import pytest
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import User
from tweets.models import Tweet


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetListView:
    """Test cases for tweet_list view"""

    def test_tweet_list_get_basic(self, test_user):
        """Test basic GET request to tweet_list view"""
        # Create some test tweets
        tweet1 = Tweet.objects.create(text="First tweet", user=test_user)
        tweet2 = Tweet.objects.create(text="Second tweet", user=test_user)

        factory = RequestFactory()
        request = factory.get("/")
        request.user = test_user

        from tweets.views import tweet_list

        response = tweet_list(request)

        assert response.status_code == 200

    def test_tweet_list_post_basic(self, test_user):
        """Test basic POST request to tweet_list view"""
        factory = RequestFactory()
        request = factory.post("/", {"text": "Test tweet"})
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_list

        response = tweet_list(request)

        # POST with valid data should redirect (302) after successful creation
        assert response.status_code == 302


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetCreateView:
    """Test cases for tweet_create view"""

    def test_tweet_create_get_basic(self, test_user):
        """Test basic GET request to tweet_create view"""
        factory = RequestFactory()
        request = factory.get("/create/")
        request.user = test_user

        from tweets.views import tweet_create

        response = tweet_create(request)

        assert response.status_code == 200

    def test_tweet_create_post_basic(self, test_user):
        """Test basic POST request to tweet_create view"""
        factory = RequestFactory()
        request = factory.post("/create/", {"text": "Test tweet"})
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_create

        response = tweet_create(request)

        # POST with valid data should redirect (302) after successful creation
        assert response.status_code == 302


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetDetailView:
    """Test cases for tweet_detail view"""

    def test_tweet_detail_basic(self, test_user):
        """Test basic tweet_detail view"""
        # Create a tweet
        tweet = Tweet.objects.create(text="Test tweet", user=test_user)

        factory = RequestFactory()
        request = factory.get(f"/{tweet.pk}/")
        request.user = test_user

        from tweets.views import tweet_detail

        response = tweet_detail(request, tweet.pk)

        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetUpdateView:
    """Test cases for tweet_update view"""

    def test_tweet_update_get_basic(self, test_user):
        """Test basic GET request to tweet_update view"""
        tweet = Tweet.objects.create(text="Original tweet", user=test_user)

        factory = RequestFactory()
        request = factory.get(f"/{tweet.pk}/update/")
        request.user = test_user

        from tweets.views import tweet_update

        response = tweet_update(request, tweet.pk)

        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetDeleteView:
    """Test cases for tweet_delete view"""

    def test_tweet_delete_get_basic(self, test_user):
        """Test basic GET request to tweet_delete view"""
        tweet = Tweet.objects.create(text="Tweet to delete", user=test_user)

        factory = RequestFactory()
        request = factory.get(f"/{tweet.pk}/delete/")
        request.user = test_user

        from tweets.views import tweet_delete

        response = tweet_delete(request, tweet.pk)

        assert response.status_code == 200
