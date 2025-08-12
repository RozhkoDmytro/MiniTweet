"""
Integration tests for database operations and data integrity
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.core.exceptions import ValidationError
from tweets.models import Tweet


class DatabaseOperationsTest(TestCase):
    """Integration tests for database operations"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

    def test_bulk_tweet_creation(self):
        """Test creating multiple tweets in bulk"""
        tweets_data = [
            {"text": f"Tweet number {i}", "user": self.user} for i in range(1, 11)
        ]

        # Create tweets in bulk
        tweets = []
        for data in tweets_data:
            tweet = Tweet(**data)
            tweet.save()
            tweets.append(tweet)

        # Verify all tweets were created
        self.assertEqual(Tweet.objects.count(), 10)

        # Verify tweets are ordered correctly
        all_tweets = Tweet.objects.all()
        self.assertEqual(all_tweets[0].text, "Tweet number 10")  # Newest first
        self.assertEqual(all_tweets[9].text, "Tweet number 1")  # Oldest last

    def test_tweet_reply_hierarchy(self):
        """Test complex reply hierarchy"""
        # Create a chain of replies
        root_tweet = Tweet.objects.create(text="Root tweet", user=self.user)

        reply1 = Tweet.objects.create(
            text="First level reply", user=self.user, parent_tweet=root_tweet
        )

        reply2 = Tweet.objects.create(
            text="Second level reply", user=self.user2, parent_tweet=reply1
        )

        reply3 = Tweet.objects.create(
            text="Third level reply", user=self.user, parent_tweet=reply2
        )

        # Verify relationships
        self.assertEqual(reply1.parent_tweet, root_tweet)
        self.assertEqual(reply2.parent_tweet, reply1)
        self.assertEqual(reply3.parent_tweet, reply2)

        # Verify reverse relationships
        self.assertIn(reply1, root_tweet.replies.all())
        self.assertIn(reply2, reply1.replies.all())
        self.assertIn(reply3, reply2.replies.all())

        # Verify cascade behavior
        reply1.delete()
        self.assertEqual(Tweet.objects.count(), 1)  # Only root_tweet remains
        self.assertEqual(root_tweet.replies.count(), 0)

    def test_concurrent_tweet_creation(self):
        """Test concurrent tweet creation by multiple users"""
        from concurrent.futures import ThreadPoolExecutor

        # Create tweets from multiple users simultaneously
        def create_tweet(user_id):
            user = User.objects.get(id=user_id)
            return Tweet.objects.create(
                text=f"Tweet from user {user.username}", user=user
            )

        # Create tweets concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(create_tweet, self.user.id),
                executor.submit(create_tweet, self.user2.id),
                executor.submit(create_tweet, self.user.id),
            ]

            tweets = [future.result() for future in futures]

        # Verify all tweets were created
        self.assertEqual(Tweet.objects.count(), 3)

        # Verify each tweet has correct user
        for tweet in tweets:
            self.assertIn(tweet.user, [self.user, self.user2])

    def test_tweet_data_integrity(self):
        """Test data integrity constraints"""
        # Test unique constraints (if any)
        # Test foreign key constraints
        # Test field constraints

        # Test that we can't create tweet without user
        with self.assertRaises(Exception):
            Tweet.objects.create(text="Tweet without user")

        # Test that we can't create tweet without text
        with self.assertRaises(Exception):
            Tweet.objects.create(user=self.user)

        # Test that we can't create tweet with text too long
        long_text = "x" * 281
        with self.assertRaises(Exception):
            Tweet.objects.create(text=long_text, user=self.user)

    def test_tweet_image_operations(self):
        """Test tweet image operations and storage"""
        # Create tweets with different image types
        image_types = [
            ("image/jpeg", "test.jpg"),
            ("image/png", "test.png"),
            ("image/gif", "test.gif"),
            ("image/webp", "test.webp"),
        ]

        tweets = []
        for content_type, filename in image_types:
            image_content = b"valid-image-content"
            image = SimpleUploadedFile(
                filename, image_content, content_type=content_type
            )

            tweet = Tweet.objects.create(
                text=f"Tweet with {content_type}", user=self.user, image=image
            )
            tweets.append(tweet)

        # Verify all tweets were created with images
        for tweet in tweets:
            self.assertIsNotNone(tweet.image)
            self.assertTrue(tweet.image.name.startswith("tweets/"))

        # Test image validation
        large_image = SimpleUploadedFile(
            "large.jpg", b"x" * (6 * 1024 * 1024), content_type="image/jpeg"  # 6MB
        )

        with self.assertRaises(ValidationError):
            tweet = Tweet(
                text="Tweet with large image", user=self.user, image=large_image
            )
            tweet.full_clean()

    def test_tweet_user_relationships(self):
        """Test user-tweet relationships and cascading"""
        # Create multiple tweets for each user
        for i in range(5):
            Tweet.objects.create(text=f"User 1 tweet {i}", user=self.user)
            Tweet.objects.create(text=f"User 2 tweet {i}", user=self.user2)

        # Verify user-tweet relationships
        self.assertEqual(self.user.tweets.count(), 5)
        self.assertEqual(self.user2.tweets.count(), 5)

        # Test cascade delete
        self.user.delete()

        # All tweets from user1 should be deleted
        self.assertEqual(Tweet.objects.count(), 5)  # Only user2 tweets remain
        self.assertEqual(Tweet.objects.filter(user=self.user2).count(), 5)

    def test_tweet_ordering_and_pagination(self):
        """Test tweet ordering and pagination scenarios"""
        # Create tweets with specific timestamps
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()

        for i in range(20):
            tweet = Tweet.objects.create(text=f"Tweet {i}", user=self.user)
            # Manually set created_at to control ordering
            tweet.created_at = now - timedelta(hours=i)
            tweet.save()

        # Test ordering (newest first)
        tweets = Tweet.objects.all()
        self.assertEqual(tweets[0].text, "Tweet 0")  # Most recent
        self.assertEqual(tweets[19].text, "Tweet 19")  # Oldest

        # Test filtering by user
        user_tweets = Tweet.objects.filter(user=self.user)
        self.assertEqual(user_tweets.count(), 20)

        # Test filtering by parent_tweet (only root tweets)
        root_tweets = Tweet.objects.filter(parent_tweet__isnull=True)
        self.assertEqual(root_tweets.count(), 20)

        # Test filtering by date range
        recent_tweets = Tweet.objects.filter(created_at__gte=now - timedelta(hours=10))
        self.assertEqual(recent_tweets.count(), 11)  # 0-10 hours ago


class DatabaseTransactionTest(TransactionTestCase):
    """Integration tests for database transactions"""

    def test_transaction_rollback(self):
        """Test transaction rollback on error"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        initial_count = Tweet.objects.count()

        try:
            with transaction.atomic():
                # Create first tweet (should succeed)
                Tweet.objects.create(text="First tweet", user=user)

                # Try to create second tweet with invalid data (should fail)
                Tweet.objects.create(text="", user=user)  # Invalid: empty text
        except Exception:
            pass  # Expected to fail

        # Both tweets should be rolled back
        self.assertEqual(Tweet.objects.count(), initial_count)

    def test_concurrent_transactions(self):
        """Test concurrent transactions handling"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        def create_tweet_in_transaction():
            with transaction.atomic():
                tweet = Tweet.objects.create(
                    text=f"Tweet in transaction {threading.current_thread().ident}",
                    user=user,
                )
                return tweet

        import threading

        # Create tweets in concurrent transactions
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_tweet_in_transaction)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all tweets were created
        self.assertEqual(Tweet.objects.count(), 3)

    def test_nested_transactions(self):
        """Test nested transaction handling"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        initial_count = Tweet.objects.count()

        with transaction.atomic():
            # Outer transaction
            Tweet.objects.create(text="Outer tweet", user=user)

            with transaction.atomic():
                # Inner transaction
                Tweet.objects.create(text="Inner tweet", user=user)

            # Both should be committed together
            self.assertEqual(Tweet.objects.count(), initial_count + 2)

        # Verify both tweets are still there
        self.assertEqual(Tweet.objects.count(), initial_count + 2)

    def test_database_constraints(self):
        """Test database-level constraints"""
        _ = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Test that we can't violate database constraints
        with self.assertRaises(Exception):
            # Try to create tweet with non-existent user ID
            Tweet.objects.create(
                text="Invalid tweet", user_id=99999  # Non-existent user
            )

    def test_data_consistency(self):
        """Test data consistency across operations"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create a tweet
        tweet = Tweet.objects.create(text="Original tweet", user=user)

        # Create replies
        reply1 = Tweet.objects.create(text="Reply 1", user=user, parent_tweet=tweet)

        reply2 = Tweet.objects.create(text="Reply 2", user=user, parent_tweet=tweet)

        # Verify data consistency
        tweet.refresh_from_db()
        self.assertEqual(tweet.replies.count(), 2)

        # Update tweet text
        tweet.text = "Updated tweet"
        tweet.save()

        # Verify replies still point to correct parent
        reply1.refresh_from_db()
        reply2.refresh_from_db()
        self.assertEqual(reply1.parent_tweet, tweet)
        self.assertEqual(reply2.parent_tweet, tweet)

        # Verify parent tweet still has correct replies
        tweet.refresh_from_db()
        self.assertEqual(tweet.replies.count(), 2)
        self.assertIn(reply1, tweet.replies.all())
        self.assertIn(reply2, tweet.replies.all())
