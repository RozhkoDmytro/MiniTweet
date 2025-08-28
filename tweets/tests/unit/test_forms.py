"""
Unit tests for Tweet forms using pytest
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
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
