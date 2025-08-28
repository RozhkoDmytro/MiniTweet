import os
import django
import shutil
from django.conf import settings

# Set Django settings module BEFORE any Django imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "minitweet.settings")

# Configure Django
django.setup()


def pytest_configure(config):
    """Register custom pytest markers to eliminate warnings"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "models: mark test as testing models")
    config.addinivalue_line("markers", "views: mark test as testing views")
    config.addinivalue_line("markers", "forms: mark test as testing forms")


def pytest_sessionfinish(session, exitstatus):
    """Clean up test files after all tests finish"""
    # Clean up test media files
    if hasattr(settings, "MEDIA_ROOT") and settings.MEDIA_ROOT:
        test_media_path = os.path.join(settings.MEDIA_ROOT, "tweets")
        if os.path.exists(test_media_path):
            try:
                shutil.rmtree(test_media_path)
                print(f"🧹 Cleaned up test media files from: {test_media_path}")
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up test files: {e}")


def pytest_runtest_teardown(item, nextitem):
    """Clean up after each test"""
    # Clean up any test files created during individual tests
    if hasattr(settings, "MEDIA_ROOT") and settings.MEDIA_ROOT:
        test_media_path = os.path.join(settings.MEDIA_ROOT, "tweets")
        if os.path.exists(test_media_path):
            # Remove only test files (with test_ prefix or specific patterns)
            for filename in os.listdir(test_media_path):
                if filename.startswith("test_") or "test" in filename.lower():
                    file_path = os.path.join(test_media_path, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception:
                        pass  # Ignore cleanup errors for individual files
