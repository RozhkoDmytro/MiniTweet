#!/usr/bin/env python3
"""
Script to clean up test files created during Django tests
"""

import os
import shutil
import glob


def cleanup_test_files():
    """Clean up test files from various locations"""

    # Clean up test media files
    media_paths = ["media/tweets", "tweets/media", "static/media/tweets"]

    for path in media_paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"🧹 Cleaned up: {path}")
            except Exception as e:
                print(f"⚠️  Could not clean {path}: {e}")

    # Clean up test image files in current directory
    test_files = (
        glob.glob("test_*.jpg") + glob.glob("test_*.png") + glob.glob("test_*.gif")
    )
    for file in test_files:
        try:
            os.remove(file)
            print(f"🧹 Removed test file: {file}")
        except Exception as e:
            print(f"⚠️  Could not remove {file}: {e}")

    # Clean up pytest cache
    if os.path.exists(".pytest_cache"):
        try:
            shutil.rmtree(".pytest_cache")
            print("🧹 Cleaned up pytest cache")
        except Exception as e:
            print(f"⚠️  Could not clean pytest cache: {e}")


if __name__ == "__main__":
    print("🧹 Starting test file cleanup...")
    cleanup_test_files()
    print("✅ Cleanup completed!")
