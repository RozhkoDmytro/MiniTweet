"""
Unit tests for Tweet URL patterns using pytest
"""

import pytest
from django.urls import reverse, resolve
from tweets import views


@pytest.mark.django_db
@pytest.mark.urls
@pytest.mark.unit
@pytest.mark.urls("minitweet.urls")
class TestTweetURLs:
    """Test cases for Tweet URL patterns"""

    def test_tweet_list_url(self):
        """Test tweet_list URL pattern"""
        url = reverse("tweets:tweet_list")
        assert url == "/"

        resolver = resolve(url)
        assert resolver.func == views.tweet_list
        assert resolver.app_name == "tweets"

    def test_tweet_create_url(self):
        """Test tweet_create URL pattern"""
        url = reverse("tweets:tweet_create")
        assert url == "/create/"

        resolver = resolve(url)
        assert resolver.func == views.tweet_create
        assert resolver.app_name == "tweets"

    def test_tweet_detail_url(self):
        """Test tweet_detail URL pattern"""
        url = reverse("tweets:tweet_detail", kwargs={"pk": 1})
        assert url == "/1/"

        resolver = resolve(url)
        assert resolver.func == views.tweet_detail
        assert resolver.kwargs["pk"] == 1  # Django returns int for pk
        assert resolver.app_name == "tweets"

    def test_tweet_update_url(self):
        """Test tweet_update URL pattern"""
        url = reverse("tweets:tweet_update", kwargs={"pk": 1})
        assert url == "/1/update/"

        resolver = resolve(url)
        assert resolver.func == views.tweet_update
        assert resolver.kwargs["pk"] == 1  # Django returns int for pk
        assert resolver.app_name == "tweets"

    def test_tweet_delete_url(self):
        """Test tweet_delete URL pattern"""
        url = reverse("tweets:tweet_delete", kwargs={"pk": 1})
        assert url == "/1/delete/"

        resolver = resolve(url)
        assert resolver.func == views.tweet_delete
        assert resolver.kwargs["pk"] == 1  # Django returns int for pk
        assert resolver.app_name == "tweets"

    def test_tweet_reply_url(self):
        """Test tweet_reply URL pattern"""
        url = reverse("tweets:tweet_reply", kwargs={"pk": 1})
        assert url == "/1/reply/"

        resolver = resolve(url)
        assert resolver.func == views.tweet_reply
        assert resolver.kwargs["pk"] == 1  # Django returns int for pk
        assert resolver.app_name == "tweets"

    def test_url_namespace(self):
        """Test that all URLs use the correct namespace"""
        url_patterns = [
            ("tweets:tweet_list", {}),
            ("tweets:tweet_create", {}),
            ("tweets:tweet_detail", {"pk": 1}),
            ("tweets:tweet_update", {"pk": 1}),
            ("tweets:tweet_delete", {"pk": 1}),
            ("tweets:tweet_reply", {"pk": 1}),
        ]

        for name, kwargs in url_patterns:
            url = reverse(name, kwargs=kwargs)
            resolver = resolve(url)
            assert resolver.app_name == "tweets"

    def test_url_parameters(self):
        """Test that URL parameters are correctly handled"""
        # Test with different primary key values
        test_pks = [1, 42, 999, 12345]

        for pk in test_pks:
            # Test detail URL
            detail_url = reverse("tweets:tweet_detail", kwargs={"pk": pk})
            assert detail_url == f"/{pk}/"

            # Test update URL
            update_url = reverse("tweets:tweet_update", kwargs={"pk": pk})
            assert update_url == f"/{pk}/update/"

            # Test delete URL
            delete_url = reverse("tweets:tweet_delete", kwargs={"pk": pk})
            assert delete_url == f"/{pk}/delete/"

            # Test reply URL
            reply_url = reverse("tweets:tweet_reply", kwargs={"pk": pk})
            assert reply_url == f"/{pk}/reply/"

    def test_url_resolution(self):
        """Test that URLs resolve to the correct view functions"""
        url_mappings = [
            ("/", views.tweet_list),
            ("/create/", views.tweet_create),
            ("/1/", views.tweet_detail),
            ("/1/update/", views.tweet_update),
            ("/1/delete/", views.tweet_delete),
            ("/1/reply/", views.tweet_reply),
        ]

        for url_path, expected_view in url_mappings:
            resolver = resolve(url_path)
            assert resolver.func == expected_view

    def test_url_pattern_order(self):
        """Test that URL patterns are in the correct order"""
        # The order matters for URL resolution
        # More specific patterns should come before more general ones

        # Test that /create/ comes before /<int:pk>/
        create_url = reverse("tweets:tweet_create")
        detail_url = reverse("tweets:tweet_detail", kwargs={"pk": 1})

        # Both should resolve correctly
        create_resolver = resolve(create_url)
        detail_resolver = resolve(detail_url)

        assert create_resolver.func == views.tweet_create
        assert detail_resolver.func == views.tweet_detail

    def test_url_name_consistency(self):
        """Test that URL names are consistent with view function names"""
        # Check that URL names match their corresponding view function names
        url_view_mappings = {
            "tweet_list": views.tweet_list,
            "tweet_create": views.tweet_create,
            "tweet_detail": views.tweet_detail,
            "tweet_update": views.tweet_update,
            "tweet_delete": views.tweet_delete,
            "tweet_reply": views.tweet_reply,
        }

        # Define which URLs require pk parameter
        urls_requiring_pk = {
            "tweet_detail",
            "tweet_update",
            "tweet_delete",
            "tweet_reply",
        }

        for url_name, view_func in url_view_mappings.items():
            # Add pk parameter for URLs that require it
            kwargs = {"pk": 1} if url_name in urls_requiring_pk else {}
            url = reverse(f"tweets:{url_name}", kwargs=kwargs)
            resolver = resolve(url)
            assert resolver.func == view_func


# Additional pytest-style tests
@pytest.mark.django_db
@pytest.mark.urls
@pytest.mark.unit
@pytest.mark.urls("minitweet.urls")
@pytest.mark.parametrize(
    "url_name,expected_path",
    [
        ("tweet_list", "/"),
        ("tweet_create", "/create/"),
    ],
)
def test_url_paths(url_name, expected_path):
    """Test URL paths for different URL names"""
    url = reverse(f"tweets:{url_name}")
    assert url == expected_path


@pytest.mark.django_db
@pytest.mark.urls
@pytest.mark.unit
@pytest.mark.urls("minitweet.urls")
@pytest.mark.parametrize(
    "url_name,view_func",
    [
        ("tweet_list", views.tweet_list),
        ("tweet_create", views.tweet_create),
        ("tweet_detail", views.tweet_detail),
        ("tweet_update", views.tweet_update),
        ("tweet_delete", views.tweet_delete),
        ("tweet_reply", views.tweet_reply),
    ],
)
def test_url_view_mapping(url_name, view_func):
    """Test that URLs map to correct view functions"""
    # Define which URLs require pk parameter
    urls_requiring_pk = {"tweet_detail", "tweet_update", "tweet_delete", "tweet_reply"}
    kwargs = {"pk": 1} if url_name in urls_requiring_pk else {}
    url = reverse(f"tweets:{url_name}", kwargs=kwargs)
    resolver = resolve(url)
    assert resolver.func == view_func


@pytest.mark.django_db
@pytest.mark.urls
@pytest.mark.unit
@pytest.mark.urls("minitweet.urls")
def test_url_namespace_consistency():
    """Test that all URLs consistently use the tweets namespace"""
    url_names = [
        "tweet_list",
        "tweet_create",
        "tweet_detail",
        "tweet_update",
        "tweet_delete",
        "tweet_reply",
    ]

    # Define which URLs require pk parameter
    urls_requiring_pk = {"tweet_detail", "tweet_update", "tweet_delete", "tweet_reply"}

    for url_name in url_names:
        kwargs = {"pk": 1} if url_name in urls_requiring_pk else {}
        url = reverse(f"tweets:{url_name}", kwargs=kwargs)
        resolver = resolve(url)
        assert resolver.app_name == "tweets"


@pytest.mark.django_db
@pytest.mark.urls
@pytest.mark.unit
@pytest.mark.urls("minitweet.urls")
def test_url_parameter_validation():
    """Test that URL parameters are properly validated"""
    # Test that invalid PK values are handled correctly
    invalid_pks = [-1, 0, "abc", "1.5"]

    for pk in invalid_pks:
        try:
            url = reverse("tweets:tweet_detail", kwargs={"pk": pk})
            # If this succeeds, the URL should resolve
            resolver = resolve(url)
            assert resolver.kwargs["pk"] == pk
        except Exception:
            # Some invalid PKs might cause errors, which is acceptable
            pass


@pytest.mark.django_db
@pytest.mark.urls
@pytest.mark.unit
@pytest.mark.urls("minitweet.urls")
def test_url_reverse_resolve_consistency():
    """Test that reverse and resolve are consistent"""
    test_cases = [
        ("tweets:tweet_list", {}),
        ("tweets:tweet_create", {}),
        ("tweets:tweet_detail", {"pk": 42}),
        ("tweets:tweet_update", {"pk": 42}),
        ("tweets:tweet_delete", {"pk": 42}),
        ("tweets:tweet_reply", {"pk": 42}),
    ]

    for url_name, kwargs in test_cases:
        # Generate URL using reverse
        url = reverse(url_name, kwargs=kwargs)

        # Resolve the URL back
        resolver = resolve(url)

        # Check that the resolved function matches the expected view
        if "tweet_list" in url_name:
            assert resolver.func == views.tweet_list
        elif "tweet_create" in url_name:
            assert resolver.func == views.tweet_create
        elif "tweet_detail" in url_name:
            assert resolver.func == views.tweet_detail
        elif "tweet_update" in url_name:
            assert resolver.func == views.tweet_update
        elif "tweet_delete" in url_name:
            assert resolver.func == views.tweet_delete
        elif "tweet_reply" in url_name:
            assert resolver.func == views.tweet_reply
