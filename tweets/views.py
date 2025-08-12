import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Tweet
from .forms import TweetForm, ReplyForm

logger = logging.getLogger(__name__)


def tweet_list(request):
    """Display list of all tweets and handle tweet creation"""
    logger.info(f"tweet_list called with method: {request.method}")

    if request.method == "POST":
        logger.info(f"POST data: {request.POST}")
        logger.info(f"FILES data: {request.FILES}")

        # Check if request is too large before processing
        if request.content_type and "multipart/form-data" in request.content_type:
            content_length = request.META.get("CONTENT_LENGTH", 0)
            if content_length and int(content_length) > 5 * 1024 * 1024:  # 5MB
                messages.error(
                    request,
                    "File too large! Maximum file size is 5MB. Tweet cannot be published.",
                )
                form = TweetForm()
                tweets = Tweet.objects.filter(parent_tweet__isnull=True).order_by(
                    "-created_at"
                )
                return render(
                    request, "tweets/list.html", {"tweets": tweets, "form": form}
                )

        form = TweetForm(request.POST, request.FILES)
        logger.info(f"Form is valid: {form.is_valid()}")
        logger.info(f"Form data: {form.data}")
        logger.info(f"Form fields: {form.fields}")
        logger.info(f"Form errors: {form.errors}")

        if form.is_valid():
            logger.info("Form is valid, creating tweet...")
            # Create tweet without user for now (will be fixed)
            tweet = form.save(commit=False)
            # Use default user (ID 1) if not authenticated
            if request.user.is_authenticated:
                tweet.user = request.user
                logger.info(f"Using authenticated user: {request.user.username}")
            else:
                from django.contrib.auth.models import User

                tweet.user = User.objects.get(id=1)
                logger.info(f"Using default user: {tweet.user.username}")

            tweet.save()
            logger.info(f"Tweet saved successfully with ID: {tweet.id}")
            messages.success(request, "Tweet posted successfully!")
            return redirect("tweets:tweet_list")
        else:
            logger.error(f"Form errors: {form.errors}")
            # Check for specific file size errors
            if "image" in form.errors:
                for error in form.errors["image"]:
                    if "file size" in str(error).lower():
                        messages.error(
                            request,
                            f"Image error: {error}. Tweet cannot be published.",
                        )
                    else:
                        messages.error(request, f"Image error: {error}")
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        form = TweetForm()

    tweets = Tweet.objects.filter(parent_tweet__isnull=True).order_by("-created_at")
    logger.info(f"Found {tweets.count()} tweets")
    logger.info(f"Form bound: {form.is_bound}")
    logger.info(f"Form initial: {form.initial}")

    return render(request, "tweets/list.html", {"tweets": tweets, "form": form})


def tweet_create(request):
    """Create a new tweet"""
    if request.method == "POST":
        # Check if request is too large before processing
        if request.content_type and "multipart/form-data" in request.content_type:
            content_length = request.META.get("CONTENT_LENGTH", 0)
            if content_length and int(content_length) > 5 * 1024 * 1024:  # 5MB
                messages.error(
                    request,
                    "File too large! Maximum file size is 5MB. Tweet cannot be published.",
                )
                form = TweetForm()
                return render(request, "tweets/create.html", {"form": form})

        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            # Use authenticated user or default user
            if request.user.is_authenticated:
                tweet.user = request.user
            else:
                from django.contrib.auth.models import User

                tweet.user = User.objects.get(id=1)

            tweet.save()
            messages.success(request, "Tweet posted successfully!")
            return redirect("tweets:tweet_list")
        else:
            # Check for specific file size errors
            if "image" in form.errors:
                for error in form.errors["image"]:
                    if "file size" in str(error).lower():
                        messages.error(
                            request,
                            f"Image error: {error}. Tweet cannot be published.",
                        )
                    else:
                        messages.error(request, f"Image error: {error}")
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        form = TweetForm()

    return render(request, "tweets/create.html", {"form": form})


def tweet_detail(request, pk):
    """Display tweet detail with replies"""
    tweet = get_object_or_404(Tweet, pk=pk)
    replies = tweet.replies.all().order_by("created_at")
    reply_form = ReplyForm()

    return render(
        request,
        "tweets/detail.html",
        {"tweet": tweet, "replies": replies, "reply_form": reply_form},
    )


def tweet_reply(request, pk):
    """Reply to a tweet"""
    parent_tweet = get_object_or_404(Tweet, pk=pk)
    logger.info(f"tweet_reply called for tweet {pk} with method: {request.method}")

    if request.method == "POST":
        logger.info(f"POST data: {request.POST}")
        logger.info(f"FILES data: {request.FILES}")

        # Check if request is too large before processing
        if request.content_type and "multipart/form-data" in request.content_type:
            content_length = request.META.get("CONTENT_LENGTH", 0)
            if content_length and int(content_length) > 5 * 1024 * 1024:  # 5MB
                messages.error(
                    request,
                    "File too large! Maximum file size is 5MB. Reply cannot be published.",
                )
                return redirect("tweets:tweet_detail", pk=pk)

        form = ReplyForm(request.POST, request.FILES)
        logger.info(f"Form is valid: {form.is_valid()}")
        logger.info(f"Form errors: {form.errors}")

        if form.is_valid():
            reply = form.save(commit=False)
            # Use authenticated user or default user
            if request.user.is_authenticated:
                reply.user = request.user
            else:
                from django.contrib.auth.models import User

                reply.user = User.objects.get(id=1)

            reply.parent_tweet = parent_tweet
            reply.save()
            logger.info(f"Reply saved successfully with ID: {reply.id}")
            messages.success(request, "Reply posted successfully!")
            return redirect("tweets:tweet_detail", pk=pk)
        else:
            # Check for specific file size errors
            if "image" in form.errors:
                for error in form.errors["image"]:
                    if "file size" in str(error).lower():
                        messages.error(
                            request,
                            f"Image error: {error}. Reply cannot be published.",
                        )
                    else:
                        messages.error(request, f"Image error: {error}")
            else:
                messages.error(request, "Please correct the errors below.")

    return redirect("tweets:tweet_detail", pk=pk)


@login_required
def tweet_update(request, pk):
    """Update existing tweet"""
    tweet = get_object_or_404(Tweet, pk=pk, user=request.user)

    if request.method == "POST":
        # Check if request is too large before processing
        if request.content_type and "multipart/form-data" in request.content_type:
            content_length = request.META.get("CONTENT_LENGTH", 0)
            if content_length and int(content_length) > 5 * 1024 * 1024:  # 5MB
                messages.error(
                    request,
                    "File too large! Maximum file size is 5MB. Tweet cannot be updated.",
                )
                form = TweetForm(instance=tweet)
                return render(
                    request, "tweets/update.html", {"form": form, "tweet": tweet}
                )

        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            form.save()
            messages.success(request, "Tweet updated successfully!")
            return redirect("tweet_detail", pk=pk)
        else:
            # Check for specific file size errors
            if "image" in form.errors:
                for error in form.errors["image"]:
                    if "file size" in str(error).lower():
                        messages.error(
                            request,
                            f"Image error: {error}. Tweet cannot be updated.",
                        )
                    else:
                        messages.error(request, f"Image error: {error}")
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        form = TweetForm(instance=tweet)

    return render(request, "tweets/update.html", {"form": form, "tweet": tweet})


@login_required
def tweet_delete(request, pk):
    """Delete tweet"""
    tweet = get_object_or_404(Tweet, pk=pk, user=request.user)

    if request.method == "POST":
        tweet.delete()
        messages.success(request, "Tweet deleted successfully!")
        return redirect("tweet_list")

    return render(request, "tweets/delete.html", {"tweet": tweet})
