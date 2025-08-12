"""
Integration tests for complete user workflows
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from tweets.models import Tweet


class UserWorkflowTest(TestCase):
    """Integration tests for complete user workflows"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

    def test_complete_tweet_workflow(self):
        """Test complete workflow: create, view, update, delete tweet"""
        # Login user
        self.client.login(username="testuser", password="testpass123")

        # 1. Create a tweet
        response = self.client.post(
            reverse("tweets:tweet_create"), {"text": "My first tweet!"}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after creation

        # Get the created tweet
        tweet = Tweet.objects.get(text="My first tweet!")
        self.assertEqual(tweet.user, self.user)

        # 2. View the tweet
        response = self.client.get(
            reverse("tweets:tweet_detail", kwargs={"pk": tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My first tweet!")

        # 3. Update the tweet
        response = self.client.post(
            reverse("tweets:tweet_update", kwargs={"pk": tweet.pk}),
            {"text": "My updated tweet!"},
        )
        self.assertEqual(response.status_code, 302)  # Redirect after update

        # Check tweet was updated
        tweet.refresh_from_db()
        self.assertEqual(tweet.text, "My updated tweet!")

        # 4. Delete the tweet
        response = self.client.post(
            reverse("tweets:tweet_delete", kwargs={"pk": tweet.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect after deletion

        # Check tweet was deleted
        with self.assertRaises(Tweet.DoesNotExist):
            Tweet.objects.get(pk=tweet.pk)

    def test_complete_reply_workflow(self):
        """Test complete workflow: create tweet, reply to it, view conversation"""
        # Login user
        self.client.login(username="testuser", password="testpass123")

        # 1. Create a parent tweet
        response = self.client.post(
            reverse("tweets:tweet_create"), {"text": "Parent tweet for replies"}
        )
        self.assertEqual(response.status_code, 302)

        parent_tweet = Tweet.objects.get(text="Parent tweet for replies")

        # 2. Reply to the tweet
        response = self.client.post(
            reverse("tweets:tweet_reply", kwargs={"pk": parent_tweet.pk}),
            {"text": "This is my reply"},
        )
        self.assertEqual(response.status_code, 302)

        # Check reply was created
        reply = Tweet.objects.get(text="This is my reply")
        self.assertEqual(reply.parent_tweet, parent_tweet)
        self.assertEqual(reply.user, self.user)

        # 3. View the conversation
        response = self.client.get(
            reverse("tweets:tweet_detail", kwargs={"pk": parent_tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Parent tweet for replies")
        self.assertContains(response, "This is my reply")

        # Check replies are ordered correctly
        replies = response.context["replies"]
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0], reply)

    def test_multi_user_conversation(self):
        """Test conversation between multiple users"""
        # User 1 creates a tweet
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("tweets:tweet_create"), {"text": "What do you think about Django?"}
        )
        self.assertEqual(response.status_code, 302)

        parent_tweet = Tweet.objects.get(text="What do you think about Django?")

        # User 1 replies to their own tweet
        response = self.client.post(
            reverse("tweets:tweet_reply", kwargs={"pk": parent_tweet.pk}),
            {"text": "I think it's great for web development!"},
        )
        self.assertEqual(response.status_code, 302)

        # User 2 replies to the tweet
        self.client.login(username="testuser2", password="testpass123")
        response = self.client.post(
            reverse("tweets:tweet_reply", kwargs={"pk": parent_tweet.pk}),
            {"text": "I agree, Django is excellent!"},
        )
        self.assertEqual(response.status_code, 302)

        # Check all replies were created
        replies = Tweet.objects.filter(parent_tweet=parent_tweet)
        self.assertEqual(replies.count(), 2)

        # View the conversation
        response = self.client.get(
            reverse("tweets:tweet_detail", kwargs={"pk": parent_tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "What do you think about Django?")
        self.assertContains(response, "I think it's great for web development!")
        self.assertContains(response, "I agree, Django is excellent!")

    def test_tweet_with_image_workflow(self):
        """Test complete workflow with image upload"""
        # Login user
        self.client.login(username="testuser", password="testpass123")

        # Create image file
        image_content = b"valid-image-content"
        image = SimpleUploadedFile(
            "test_image.jpg", image_content, content_type="image/jpeg"
        )

        # Create tweet with image
        response = self.client.post(
            reverse("tweets:tweet_create"),
            {"text": "Tweet with image"},
            files={"image": image},
        )
        self.assertEqual(response.status_code, 302)

        # Check tweet was created with image
        tweet = Tweet.objects.get(text="Tweet with image")
        self.assertIsNotNone(tweet.image)

        # View the tweet
        response = self.client.get(
            reverse("tweets:tweet_detail", kwargs={"pk": tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tweet with image")

    def test_unauthorized_access_workflow(self):
        """Test workflow with unauthorized access attempts"""
        # Create a tweet as user1
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("tweets:tweet_create"), {"text": "Private tweet"}
        )
        self.assertEqual(response.status_code, 302)

        tweet = Tweet.objects.get(text="Private tweet")

        # Try to access as user2 (should fail)
        self.client.login(username="testuser2", password="testpass123")

        # Try to update (should fail)
        response = self.client.get(
            reverse("tweets:tweet_update", kwargs={"pk": tweet.pk})
        )
        self.assertEqual(response.status_code, 404)

        # Try to delete (should fail)
        response = self.client.get(
            reverse("tweets:tweet_delete", kwargs={"pk": tweet.pk})
        )
        self.assertEqual(response.status_code, 404)

        # But should be able to view and reply
        response = self.client.get(
            reverse("tweets:tweet_detail", kwargs={"pk": tweet.pk})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("tweets:tweet_reply", kwargs={"pk": tweet.pk}),
            {"text": "I can reply to this"},
        )
        self.assertEqual(response.status_code, 302)

    def test_error_handling_workflow(self):
        """Test workflow with error conditions"""
        # Login user
        self.client.login(username="testuser", password="testpass123")

        # Try to create tweet with empty text
        response = self.client.post(reverse("tweets:tweet_create"), {"text": ""})
        self.assertEqual(response.status_code, 200)  # Should return to form

        # Try to create tweet with text too long
        long_text = "x" * 281
        response = self.client.post(reverse("tweets:tweet_create"), {"text": long_text})
        self.assertEqual(response.status_code, 200)  # Should return to form

        # Try to create tweet with invalid image
        invalid_file = SimpleUploadedFile(
            "invalid.txt", b"invalid content", content_type="text/plain"
        )
        response = self.client.post(
            reverse("tweets:tweet_create"),
            {"text": "Tweet with invalid image"},
            files={"image": invalid_file},
        )
        self.assertEqual(response.status_code, 200)  # Should return to form

    def test_tweet_list_workflow(self):
        """Test workflow for viewing and creating tweets from list view"""
        # Login user
        self.client.login(username="testuser", password="testpass123")

        # Create some tweets
        response = self.client.post(
            reverse("tweets:tweet_list"), {"text": "First tweet from list view"}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse("tweets:tweet_list"), {"text": "Second tweet from list view"}
        )
        self.assertEqual(response.status_code, 302)

        # View the list
        response = self.client.get(reverse("tweets:tweet_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First tweet from list view")
        self.assertContains(response, "Second tweet from list view")

        # Check tweets are ordered correctly (newest first)
        tweets = response.context["tweets"]
        self.assertEqual(tweets[0].text, "Second tweet from list view")
        self.assertEqual(tweets[1].text, "First tweet from list view")

    def test_concurrent_user_workflow(self):
        """Test workflow with multiple users working simultaneously"""
        # User 1 creates a tweet
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("tweets:tweet_create"), {"text": "User 1 tweet"}
        )
        self.assertEqual(response.status_code, 302)

        user1_tweet = Tweet.objects.get(text="User 1 tweet")

        # User 2 creates a tweet
        self.client.login(username="testuser2", password="testpass123")
        response = self.client.post(
            reverse("tweets:tweet_create"), {"text": "User 2 tweet"}
        )
        self.assertEqual(response.status_code, 302)

        user2_tweet = Tweet.objects.get(text="User 2 tweet")

        # Both users should see each other's tweets in the list
        response = self.client.get(reverse("tweets:tweet_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User 1 tweet")
        self.assertContains(response, "User 2 tweet")

        # User 2 replies to User 1's tweet
        response = self.client.post(
            reverse("tweets:tweet_reply", kwargs={"pk": user1_tweet.pk}),
            {"text": "User 2 reply to User 1"},
        )
        self.assertEqual(response.status_code, 302)

        # User 1 should see the reply
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("tweets:tweet_detail", kwargs={"pk": user1_tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User 2 reply to User 1")
