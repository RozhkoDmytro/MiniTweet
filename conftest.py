"""
Main pytest configuration for MiniTweet project
"""

import pytest


# Pytest markers for test categorization
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "database: Database intensive tests")
    config.addinivalue_line("markers", "models: Model tests")
    config.addinivalue_line("markers", "forms: Form tests")
    config.addinivalue_line("markers", "views: View tests")
    config.addinivalue_line("markers", "urls: URL tests")
    config.addinivalue_line("markers", "workflows: User workflow tests")
