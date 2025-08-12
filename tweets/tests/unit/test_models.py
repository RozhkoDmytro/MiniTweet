"""
Unit tests for Tweet model using pytest
"""

import pytest


@pytest.mark.django_db
@pytest.mark.models
@pytest.mark.unit
class TestTweetModel:
    """Test cases for Tweet model"""

    def test_tweet_creation(self, test_user):
        """Test basic tweet creation"""
        from tweets.models import Tweet

        tweet = Tweet.objects.create(text="This is a test tweet", user=test_user)

        assert tweet.text == "This is a test tweet"
        assert tweet.user == test_user
        assert tweet.parent_tweet is None
        assert not tweet.image  # ImageField is falsy when no image
        assert tweet.created_at is not None
        assert tweet.updated_at is not None

    def test_tweet_string_representation(self, test_user):
        """Test tweet string representation"""
        from tweets.models import Tweet

        tweet = Tweet.objects.create(text="This is a test tweet", user=test_user)

        expected = f"{test_user.username}: This is a test tweet"
        assert str(tweet) == expected

    def test_tweet_with_long_text(self, test_user):
        """Test tweet with maximum allowed text length"""
        from tweets.models import Tweet

        long_text = "x" * 280
        tweet = Tweet.objects.create(text=long_text, user=test_user)

        assert len(tweet.text) == 280
        assert tweet.text == long_text

    def test_tweet_ordering(self, test_user):
        """Test tweet ordering by creation date"""
        from tweets.models import Tweet

        tweet1 = Tweet.objects.create(text="First tweet", user=test_user)
        tweet2 = Tweet.objects.create(text="Second tweet", user=test_user)

        tweets = Tweet.objects.all()
        assert tweets[0] == tweet2  # Most recent first
        assert tweets[1] == tweet1

    def test_tweet_reply_relationship(self, test_user):
        """Test tweet reply relationship"""
        from tweets.models import Tweet

        parent_tweet = Tweet.objects.create(text="Parent tweet", user=test_user)

        reply = Tweet.objects.create(
            text="Reply to parent", user=test_user, parent_tweet=parent_tweet
        )

        assert reply.parent_tweet == parent_tweet
        assert reply in parent_tweet.replies.all()
        assert parent_tweet.replies.count() == 1

    def test_tweet_user_relationship(self, test_user):
        """Test tweet user relationship"""
        from tweets.models import Tweet

        tweet = Tweet.objects.create(text="Test tweet", user=test_user)

        assert tweet.user == test_user
        assert tweet in test_user.tweets.all()
        assert test_user.tweets.count() == 1

    def test_tweet_meta_options(self):
        """Test tweet meta options"""
        from tweets.models import Tweet

        meta = Tweet._meta
        assert meta.ordering == ["-created_at"]


@pytest.mark.django_db
@pytest.mark.models
@pytest.mark.unit
class TestTweetValidation:
    """Test cases for Tweet validation"""

    def test_tweet_clean_method_valid(self, test_user):
        """Test tweet clean method with valid data"""
        from tweets.models import Tweet

        tweet = Tweet(text="Valid tweet", user=test_user)

        # Should not raise any exception
        tweet.clean()

    def test_tweet_clean_method_with_large_image(self, test_user):
        """Test tweet clean method with large image"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from tweets.models import Tweet

        # Create a large image file (6MB)
        large_image = SimpleUploadedFile(
            "large_image.jpg", b"x" * (6 * 1024 * 1024), content_type="image/jpeg"
        )

        tweet = Tweet(text="Tweet with large image", user=test_user, image=large_image)

        with pytest.raises(Exception):  # Should raise ValidationError
            tweet.clean()

    def test_tweet_save_calls_clean(self, test_user):
        """Test that save method calls clean method"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from tweets.models import Tweet

        # Create a large image file (6MB)
        large_image = SimpleUploadedFile(
            "large_image.jpg", b"x" * (6 * 1024 * 1024), content_type="image/jpeg"
        )

        tweet = Tweet(text="Tweet with large image", user=test_user, image=large_image)

        with pytest.raises(Exception):  # Should raise ValidationError
            tweet.save()


@pytest.mark.django_db
@pytest.mark.models
@pytest.mark.unit
class TestTweetModelConstraints:
    """Test cases for Tweet model constraints"""

    def test_tweet_text_max_length(self, test_user):
        """Test tweet text maximum length constraint"""
        from tweets.models import Tweet

        # Try to create tweet with text longer than 280 characters
        long_text = "x" * 281

        with pytest.raises(Exception):
            Tweet.objects.create(text=long_text, user=test_user)

    def test_tweet_text_required(self, test_user):
        """Test that tweet text is required"""
        from tweets.models import Tweet
        from django.core.exceptions import ValidationError

        tweet = Tweet(user=test_user)  # Missing text field

        with pytest.raises(ValidationError):
            tweet.full_clean()

    def test_tweet_user_required(self):
        """Test that tweet user is required"""
        from tweets.models import Tweet
        from django.core.exceptions import ValidationError

        tweet = Tweet(text="Test tweet")  # Missing user field

        with pytest.raises(ValidationError):
            tweet.full_clean()

    def test_tweet_cascade_delete(self, test_user):
        """Test that tweets are deleted when user is deleted"""
        from tweets.models import Tweet

        tweet = Tweet.objects.create(text="Test tweet", user=test_user)

        tweet_id = tweet.id
        test_user.delete()

        # Tweet should be deleted
        with pytest.raises(Tweet.DoesNotExist):
            Tweet.objects.get(id=tweet_id)

    def test_reply_cascade_delete(self, test_user):
        """Test that replies are deleted when parent tweet is deleted"""
        from tweets.models import Tweet

        parent_tweet = Tweet.objects.create(text="Parent tweet", user=test_user)

        reply = Tweet.objects.create(
            text="Reply", user=test_user, parent_tweet=parent_tweet
        )

        reply_id = reply.id
        parent_tweet.delete()

        # Reply should be deleted
        with pytest.raises(Tweet.DoesNotExist):
            Tweet.objects.get(id=reply_id)


# Additional pytest-style tests
@pytest.mark.django_db
@pytest.mark.models
@pytest.mark.unit
def test_tweet_creation_with_fixtures(sample_tweet, test_user):
    """Test tweet creation using fixtures"""
    assert sample_tweet.user == test_user
    assert sample_tweet.text == "This is a test tweet"


@pytest.mark.django_db
@pytest.mark.models
@pytest.mark.unit
def test_tweet_with_image_creation(sample_tweet_with_image, test_user):
    """Test tweet with image creation using fixtures"""
    assert sample_tweet_with_image.user == test_user
    assert sample_tweet_with_image.image is not None
    assert sample_tweet_with_image.image.name.startswith("tweets/")


@pytest.mark.django_db
@pytest.mark.models
@pytest.mark.unit
def test_reply_creation(sample_reply, sample_tweet, test_user):
    """Test reply creation using fixtures"""
    assert sample_reply.user == test_user
    assert sample_reply.parent_tweet == sample_tweet
    assert sample_reply in sample_tweet.replies.all()


@pytest.mark.django_db
@pytest.mark.models
@pytest.mark.unit
@pytest.mark.parametrize("text_length", [1, 100, 280])
def test_tweet_text_lengths(test_user, text_length):
    """Test tweet creation with different text lengths"""
    from tweets.models import Tweet

    text = "x" * text_length
    tweet = Tweet.objects.create(text=text, user=test_user)
    assert len(tweet.text) == text_length


@pytest.mark.django_db
@pytest.mark.models
@pytest.mark.unit
def test_tweet_updated_at_changes(test_user):
    """Test that updated_at field changes when tweet is modified"""
    from tweets.models import Tweet

    tweet = Tweet.objects.create(text="Original text", user=test_user)
    original_updated_at = tweet.updated_at

    # Wait a bit to ensure timestamp difference
    import time

    time.sleep(0.001)

    tweet.text = "Updated text"
    tweet.save()

    assert tweet.updated_at > original_updated_at
