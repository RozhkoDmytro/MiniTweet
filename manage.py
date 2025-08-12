#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

Quick Start:
1. Activate virtual environment: source env/bin/activate
2. Run server: python manage.py runserver
3. Access: http://127.0.0.1:8000/
4. Admin: http://127.0.0.1:8000/admin/ (admin/admin)

PostgreSQL: tweet_db (postgres/admin)
"""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "minitweet.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
