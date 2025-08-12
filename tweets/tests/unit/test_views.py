"""
Unit tests for Tweet views using pytest
"""

import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from tweets.models import Tweet


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetListView:
    """Test cases for tweet_list view"""

    def test_tweet_list_get(self, test_user):
        """Test GET request to tweet_list view"""
        # Create some test tweets
        tweet1 = Tweet.objects.create(text="First tweet", user=test_user)
        tweet2 = Tweet.objects.create(text="Second tweet", user=test_user)

        factory = RequestFactory()
        request = factory.get("/")
        request.user = test_user

        from tweets.views import tweet_list

        response = tweet_list(request)

        assert response.status_code == 200
        assert "tweets" in response.context
        assert "form" in response.context

        # Check tweets are ordered correctly (newest first)
        tweets = response.context["tweets"]
        assert tweets[0] == tweet2
        assert tweets[1] == tweet1

    def test_tweet_list_post_valid(self, test_user):
        """Test POST request to tweet_list view with valid data"""
        factory = RequestFactory()
        request = factory.post("/", {"text": "New test tweet"})
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_list

        response = tweet_list(request)

        # Should redirect after successful creation
        assert response.status_code == 302

        # Check tweet was created
        tweet = Tweet.objects.get(text="New test tweet")
        assert tweet.user == test_user

    def test_tweet_list_post_invalid(self, test_user):
        """Test POST request to tweet_list view with invalid data"""
        factory = RequestFactory()
        request = factory.post("/", {"text": ""})  # Empty text is invalid
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_list

        response = tweet_list(request)

        assert response.status_code == 200
        assert "form" in response.context
        assert "tweets" in response.context

    def test_tweet_list_post_with_image(self, test_user):
        """Test POST request to tweet_list view with image"""
        image_content = b"valid-image-content"
        image = SimpleUploadedFile(
            "test_image.jpg", image_content, content_type="image/jpeg"
        )

        factory = RequestFactory()
        request = factory.post(
            "/", {"text": "Tweet with image"}, files={"image": image}
        )
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_list

        response = tweet_list(request)

        assert response.status_code == 302

        # Check tweet was created with image
        tweet = Tweet.objects.get(text="Tweet with image")
        assert tweet.image is not None

    def test_tweet_list_post_large_file(self, test_user):
        """Test POST request to tweet_list view with large file"""
        # Create a large file (6MB)
        large_content = b"x" * (6 * 1024 * 1024)
        large_image = SimpleUploadedFile(
            "large_image.jpg", large_content, content_type="image/jpeg"
        )

        factory = RequestFactory()
        request = factory.post(
            "/", {"text": "Tweet with large image"}, files={"image": large_image}
        )
        request.user = test_user
        request.content_type = "multipart/form-data"
        request.META["CONTENT_LENGTH"] = str(len(large_content))

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_list

        response = tweet_list(request)

        assert response.status_code == 200
        assert "form" in response.context


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetCreateView:
    """Test cases for tweet_create view"""

    def test_tweet_create_get(self, test_user):
        """Test GET request to tweet_create view"""
        factory = RequestFactory()
        request = factory.get("/create/")
        request.user = test_user

        from tweets.views import tweet_create

        response = tweet_create(request)

        assert response.status_code == 200
        assert "form" in response.context

    def test_tweet_create_post_valid(self, test_user):
        """Test POST request to tweet_create view with valid data"""
        factory = RequestFactory()
        request = factory.post("/create/", {"text": "New tweet from create view"})
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_create

        response = tweet_create(request)

        assert response.status_code == 302

        # Check tweet was created
        tweet = Tweet.objects.get(text="New tweet from create view")
        assert tweet.user == test_user

    def test_tweet_create_post_invalid(self, test_user):
        """Test POST request to tweet_create view with invalid data"""
        factory = RequestFactory()
        request = factory.post("/create/", {"text": ""})  # Empty text is invalid
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_create

        response = tweet_create(request)

        assert response.status_code == 200
        assert "form" in response.context


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetDetailView:
    """Test cases for tweet_detail view"""

    def test_tweet_detail(self, test_user, test_user2):
        """Test tweet_detail view"""
        # Create a tweet with replies
        parent_tweet = Tweet.objects.create(text="Parent tweet", user=test_user)
        reply1 = Tweet.objects.create(
            text="First reply", user=test_user, parent_tweet=parent_tweet
        )
        reply2 = Tweet.objects.create(
            text="Second reply", user=test_user2, parent_tweet=parent_tweet
        )

        factory = RequestFactory()
        request = factory.get(f"/{parent_tweet.pk}/")
        request.user = test_user

        from tweets.views import tweet_detail

        response = tweet_detail(request, parent_tweet.pk)

        assert response.status_code == 200
        assert "tweet" in response.context
        assert "replies" in response.context
        assert "reply_form" in response.context

        # Check context data
        assert response.context["tweet"] == parent_tweet
        replies = response.context["replies"]
        assert len(replies) == 2
        assert replies[0] == reply1  # Ordered by created_at
        assert replies[1] == reply2

    def test_tweet_detail_not_found(self, test_user):
        """Test tweet_detail view with non-existent tweet"""
        factory = RequestFactory()
        request = factory.get("/999/")
        request.user = test_user

        from tweets.views import tweet_detail

        with pytest.raises(Exception):  # Should raise 404
            tweet_detail(request, 999)


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetReplyView:
    """Test cases for tweet_reply view"""

    def test_tweet_reply_post_valid(self, test_user):
        """Test POST request to tweet_reply view with valid data"""
        parent_tweet = Tweet.objects.create(text="Parent tweet", user=test_user)

        factory = RequestFactory()
        request = factory.post(
            f"/{parent_tweet.pk}/reply/", {"text": "This is a reply"}
        )
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_reply

        response = tweet_reply(request, parent_tweet.pk)

        assert response.status_code == 302

        # Check reply was created
        reply = Tweet.objects.get(text="This is a reply")
        assert reply.user == test_user
        assert reply.parent_tweet == parent_tweet

    def test_tweet_reply_post_invalid(self, test_user):
        """Test POST request to tweet_reply view with invalid data"""
        parent_tweet = Tweet.objects.create(text="Parent tweet", user=test_user)

        factory = RequestFactory()
        request = factory.post(
            f"/{parent_tweet.pk}/reply/", {"text": ""}  # Empty text is invalid
        )
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_reply

        response = tweet_reply(request, parent_tweet.pk)

        assert response.status_code == 302  # Should redirect back to detail

    def test_tweet_reply_with_image(self, test_user):
        """Test POST request to tweet_reply view with image"""
        parent_tweet = Tweet.objects.create(text="Parent tweet", user=test_user)
        image_content = b"valid-image-content"
        image = SimpleUploadedFile(
            "test_image.png", image_content, content_type="image/png"
        )

        factory = RequestFactory()
        request = factory.post(
            f"/{parent_tweet.pk}/reply/",
            {"text": "Reply with image"},
            files={"image": image},
        )
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_reply

        response = tweet_reply(request, parent_tweet.pk)

        assert response.status_code == 302

        # Check reply was created with image
        reply = Tweet.objects.get(text="Reply with image")
        assert reply.image is not None


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetUpdateView:
    """Test cases for tweet_update view"""

    def test_tweet_update_get(self, test_user):
        """Test GET request to tweet_update view"""
        tweet = Tweet.objects.create(text="Original tweet", user=test_user)

        factory = RequestFactory()
        request = factory.get(f"/{tweet.pk}/update/")
        request.user = test_user

        from tweets.views import tweet_update

        response = tweet_update(request, tweet.pk)

        assert response.status_code == 200
        assert "form" in response.context
        assert "tweet" in response.context

    def test_tweet_update_post_valid(self, test_user):
        """Test POST request to tweet_update view with valid data"""
        tweet = Tweet.objects.create(text="Original tweet", user=test_user)

        factory = RequestFactory()
        request = factory.post(f"/{tweet.pk}/update/", {"text": "Updated tweet text"})
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_update

        response = tweet_update(request, tweet.pk)

        assert response.status_code == 302

        # Check tweet was updated
        tweet.refresh_from_db()
        assert tweet.text == "Updated tweet text"

    def test_tweet_update_unauthorized(self, test_user, test_user2):
        """Test tweet_update view with unauthorized user"""
        tweet = Tweet.objects.create(text="Original tweet", user=test_user2)

        factory = RequestFactory()
        request = factory.get(f"/{tweet.pk}/update/")
        request.user = test_user

        from tweets.views import tweet_update

        with pytest.raises(Exception):  # Should raise 404
            tweet_update(request, tweet.pk)


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestTweetDeleteView:
    """Test cases for tweet_delete view"""

    def test_tweet_delete_get(self, test_user):
        """Test GET request to tweet_delete view"""
        tweet = Tweet.objects.create(text="Tweet to delete", user=test_user)

        factory = RequestFactory()
        request = factory.get(f"/{tweet.pk}/delete/")
        request.user = test_user

        from tweets.views import tweet_delete

        response = tweet_delete(request, tweet.pk)

        assert response.status_code == 200
        assert "tweet" in response.context

    def test_tweet_delete_post(self, test_user):
        """Test POST request to tweet_delete view"""
        tweet = Tweet.objects.create(text="Tweet to delete", user=test_user)
        tweet_id = tweet.pk

        factory = RequestFactory()
        request = factory.post(f"/{tweet.pk}/delete/")
        request.user = test_user

        # Add messages framework
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        from tweets.views import tweet_delete

        response = tweet_delete(request, tweet.pk)

        assert response.status_code == 302

        # Check tweet was deleted
        with pytest.raises(Tweet.DoesNotExist):
            Tweet.objects.get(id=tweet_id)

    def test_tweet_delete_unauthorized(self, test_user, test_user2):
        """Test tweet_delete view with unauthorized user"""
        tweet = Tweet.objects.create(text="Tweet to delete", user=test_user2)

        factory = RequestFactory()
        request = factory.get(f"/{tweet.pk}/delete/")
        request.user = test_user

        from tweets.views import tweet_delete

        with pytest.raises(Exception):  # Should raise 404
            tweet_delete(request, tweet.pk)


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
class TestViewAuthentication:
    """Test cases for view authentication"""

    def test_login_required_decorators(self, test_user, test_user2):
        """Test that login_required decorators work correctly"""
        tweet = Tweet.objects.create(text="Test tweet", user=test_user)

        factory = RequestFactory()

        # Test update view requires login
        request = factory.get(f"/{tweet.pk}/update/")
        request.user = test_user2  # Different user

        from tweets.views import tweet_update

        with pytest.raises(Exception):  # Should raise 404
            tweet_update(request, tweet.pk)

        # Test delete view requires login
        request = factory.get(f"/{tweet.pk}/delete/")
        request.user = test_user2  # Different user

        from tweets.views import tweet_delete

        with pytest.raises(Exception):  # Should raise 404
            tweet_delete(request, tweet.pk)


# Additional pytest-style tests
@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
def test_view_imports():
    """Test that all views can be imported correctly"""
    from tweets.views import (
        tweet_list,
        tweet_create,
        tweet_detail,
        tweet_reply,
        tweet_update,
        tweet_delete,
    )

    assert all(
        [
            tweet_list,
            tweet_create,
            tweet_detail,
            tweet_reply,
            tweet_update,
            tweet_delete,
        ]
    )


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
@pytest.mark.parametrize(
    "view_name,expected_status",
    [
        ("tweet_list", 200),
        ("tweet_create", 200),
    ],
)
def test_view_get_requests(test_user, view_name, expected_status):
    """Test GET requests to different views"""
    factory = RequestFactory()
    request = factory.get("/")
    request.user = test_user

    from tweets.views import tweet_list, tweet_create

    views = {"tweet_list": tweet_list, "tweet_create": tweet_create}
    view_func = views[view_name]

    response = view_func(request)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.unit
def test_view_context_data(test_user):
    """Test that views provide expected context data"""
    factory = RequestFactory()
    request = factory.get("/")
    request.user = test_user

    from tweets.views import tweet_list

    response = tweet_list(request)
    context = response.context

    assert "tweets" in context
    assert "form" in context
    assert isinstance(context["tweets"], list)
    assert hasattr(context["form"], "fields")
