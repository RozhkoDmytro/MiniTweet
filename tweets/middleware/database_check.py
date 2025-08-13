"""
Database connectivity check middleware.
This middleware ensures the database is ready before processing requests.
"""

import logging
from django.core.management import call_command
from django.db import connection, DatabaseError
from django.db.utils import OperationalError
from django.http import HttpResponseServerError
from django.conf import settings

logger = logging.getLogger(__name__)


class DatabaseCheckMiddleware:
    """
    Middleware to check database connectivity on first request.
    This ensures the database is ready before processing any requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._db_checked = False
        self._db_healthy = False

    def __call__(self, request):
        # Check database only once per server startup
        if not self._db_checked:
            print("🔍 DatabaseCheckMiddleware: First request, checking database...")
            self._check_database()
            self._db_checked = True

        # If database is unhealthy, return error
        if not self._db_healthy:
            print("❌ DatabaseCheckMiddleware: Database is unhealthy, returning error")
            return HttpResponseServerError(
                "Database is not available. Please check your database connection.",
                content_type="text/plain",
            )

        return self.get_response(request)

    def _check_database(self):
        """Check database connectivity and health."""
        logger.info("🔍 DatabaseCheckMiddleware: Starting database health check...")
        try:
            # Test basic connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            # Check if Django tables exist
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'django_migrations'
                """
                )
                has_migrations_table = cursor.fetchone()[0] > 0

            if not has_migrations_table:
                logger.warning(
                    "Django migrations table not found. Running migrations..."
                )
                call_command("migrate", verbosity=0)
                logger.info("Migrations completed successfully")

            self._db_healthy = True
            logger.info("Database connectivity check passed")

        except (OperationalError, DatabaseError) as e:
            self._db_healthy = False
            logger.error(
                f"❌ DatabaseCheckMiddleware: Database connectivity check failed: {e}"
            )

            # Log detailed error information
            if hasattr(settings, "DATABASES"):
                db_config = settings.DATABASES.get("default", {})
                logger.error(
                    f"Database config: {db_config.get('HOST', 'Unknown')}:{db_config.get('PORT', 'Unknown')}"
                )

        except Exception as e:
            self._db_healthy = False
            logger.error(f"Unexpected error during database check: {e}")

    def process_exception(self, request, exception):
        """Handle database-related exceptions."""
        if isinstance(exception, (OperationalError, DatabaseError)):
            logger.error(f"Database error in request: {exception}")
            return HttpResponseServerError(
                "Database error occurred. Please try again later.",
                content_type="text/plain",
            )
        return None
