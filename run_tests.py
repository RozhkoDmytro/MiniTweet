#!/usr/bin/env python3
"""
Test runner script for MiniTweet Django application
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print("✅ SUCCESS")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        return False


def main():
    """Main test runner function"""
    print("🚀 MiniTweet Test Runner")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print(
            "❌ Error: manage.py not found. Please run this script from the project root."
        )
        sys.exit(1)

    # Check if virtual environment is activated
    if not os.environ.get("VIRTUAL_ENV"):
        print("⚠️  Warning: Virtual environment not detected.")
        print("   Consider activating your virtual environment first.")

    # Install test dependencies
    print("\n📦 Installing test dependencies...")
    if not run_command(
        "pip install -r requirements-test.txt", "Installing test dependencies"
    ):
        print(
            "❌ Failed to install test dependencies. Please check requirements-test.txt"
        )
        sys.exit(1)

    # Set Django settings module
    os.environ["DJANGO_SETTINGS_MODULE"] = "minitweet.settings"

    # Run unit tests
    print("\n🧪 Running Unit Tests...")
    if not run_command(
        "python3 -m pytest tweets/tests/unit/ -v --tb=short", "Unit tests"
    ):
        print("❌ Unit tests failed!")
        unit_failed = True
    else:
        unit_failed = False

    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    if not run_command(
        "python3 -m pytest tweets/tests/integration/ -v --tb=short", "Integration tests"
    ):
        print("❌ Integration tests failed!")
        integration_failed = True
    else:
        integration_failed = False

    # Run all tests with coverage
    print("\n📊 Running All Tests with Coverage...")
    if not run_command(
        "python3 -m pytest --cov=tweets --cov-report=html --cov-report=term-missing",
        "All tests with coverage",
    ):
        print("❌ Coverage tests failed!")
        coverage_failed = True
    else:
        coverage_failed = False

    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)

    if unit_failed:
        print("❌ Unit Tests: FAILED")
    else:
        print("✅ Unit Tests: PASSED")

    if integration_failed:
        print("❌ Integration Tests: FAILED")
    else:
        print("✅ Integration Tests: PASSED")

    if coverage_failed:
        print("❌ Coverage Tests: FAILED")
    else:
        print("✅ Coverage Tests: PASSED")

    if not any([unit_failed, integration_failed, coverage_failed]):
        print("\n🎉 All tests passed successfully!")
        print("\n📁 Coverage report generated in htmlcov/ directory")
        print("📊 View coverage report: open htmlcov/index.html")
    else:
        print("\n💥 Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
