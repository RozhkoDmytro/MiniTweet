from django.test import TestCase
from .models import Tweet

# Create your tests here.

class TweetTest(TestCase):
    def test_create_tweet(self):
        tweet = Tweet.objects.create(text="Hello test!")
        self.assertEqual(str(tweet), "Hello test!")
