"""
Pytest configuration and common fixtures for MiniTweet tests
"""

import pytest


@pytest.fixture
def test_user():
    """Create a test user for testing"""
    from django.contrib.auth.models import User

    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def test_user2():
    """Create a second test user for testing"""
    from django.contrib.auth.models import User

    return User.objects.create_user(
        username="testuser2", email="test2@example.com", password="testpass123"
    )


@pytest.fixture
def sample_tweet(test_user):
    """Create a sample tweet for testing"""
    from tweets.models import Tweet

    return Tweet.objects.create(text="This is a test tweet", user=test_user)


@pytest.fixture
def sample_tweet_with_image(test_user):
    """Create a sample tweet with image for testing"""
    from django.core.files.uploadedfile import SimpleUploadedFile
    from tweets.models import Tweet

    # Create a simple test image
    image_content = b"fake-image-content"
    image = SimpleUploadedFile(
        "test_image.jpg", image_content, content_type="image/jpeg"
    )

    return Tweet.objects.create(
        text="This is a test tweet with image", user=test_user, image=image
    )


@pytest.fixture
def sample_reply(test_user, sample_tweet):
    """Create a sample reply tweet for testing"""
    from tweets.models import Tweet

    return Tweet.objects.create(
        text="This is a test reply", user=test_user, parent_tweet=sample_tweet
    )


@pytest.fixture
def large_image_file():
    """Create a large image file for testing file size validation"""
    from django.core.files.uploadedfile import SimpleUploadedFile

    # Create a file larger than 5MB
    large_content = b"x" * (6 * 1024 * 1024)  # 6MB
    return SimpleUploadedFile(
        "large_image.jpg", large_content, content_type="image/jpeg"
    )


@pytest.fixture
def invalid_image_file():
    """Create an invalid image file for testing file type validation"""
    from django.core.files.uploadedfile import SimpleUploadedFile

    invalid_content = b"invalid-file-content"
    return SimpleUploadedFile(
        "invalid_file.txt", invalid_content, content_type="text/plain"
    )


@pytest.fixture
def valid_image_file():
    """Create a valid image file for testing"""
    from django.core.files.uploadedfile import SimpleUploadedFile

    image_content = b"valid-image-content"
    return SimpleUploadedFile(
        "valid_image.png", image_content, content_type="image/png"
    )
