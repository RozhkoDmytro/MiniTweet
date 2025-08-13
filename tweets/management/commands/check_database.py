"""
Django management command to check database connectivity and required tables.
This command ensures the database is ready before starting the application.
"""

import time
import logging
from django.core.management.base import BaseCommand
from django.db import connection, DatabaseError
from django.db.utils import OperationalError
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Check database connectivity and required tables"

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-retries",
            type=int,
            default=30,
            help="Maximum number of connection retries (default: 30)",
        )
        parser.add_argument(
            "--retry-delay",
            type=int,
            default=2,
            help="Delay between retries in seconds (default: 2)",
        )
        parser.add_argument(
            "--create-tables",
            action="store_true",
            help="Create missing tables if they don't exist",
        )

    def handle(self, *args, **options):
        max_retries = options["max_retries"]
        retry_delay = options["retry_delay"]
        create_tables = options["create_tables"]

        self.stdout.write(self.style.SUCCESS("🔍 Checking database connectivity..."))

        # Try to connect to database with retries
        for attempt in range(max_retries):
            try:
                # Test basic connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Database connection successful on attempt {attempt + 1}"
                    )
                )
                break

            except (OperationalError, DatabaseError) as e:
                if attempt < max_retries - 1:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Connection attempt {attempt + 1} failed: {e}"
                        )
                    )
                    self.stdout.write(
                        f"🔄 Retrying in {retry_delay} seconds... ({max_retries - attempt - 1} attempts left)"
                    )
                    time.sleep(retry_delay)
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Failed to connect to database after {max_retries} attempts"
                        )
                    )
                    raise e

        # Check if required tables exist
        self.check_required_tables(create_tables)

        # Check database version and extensions
        self.check_database_info()

        self.stdout.write(
            self.style.SUCCESS("🎉 Database check completed successfully!")
        )

    def check_required_tables(self, create_tables):
        """Check if required Django tables exist."""
        self.stdout.write("📋 Checking required tables...")

        required_tables = [
            "django_migrations",
            "django_content_type",
            "django_admin_log",
            "django_session",
            "auth_user",
            "auth_group",
            "auth_permission",
            "tweets_tweet",  # Your app's main table
        ]

        missing_tables = []

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            )
            existing_tables = {row[0] for row in cursor.fetchall()}

        for table in required_tables:
            if table in existing_tables:
                self.stdout.write(f"  ✅ {table}")
            else:
                self.stdout.write(f"  ❌ {table} (missing)")
                missing_tables.append(table)

        if missing_tables:
            if create_tables:
                self.stdout.write("🔧 Creating missing tables...")
                from django.core.management import call_command

                call_command("migrate", verbosity=0)
                self.stdout.write("✅ Tables created successfully")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Missing tables: {", ".join(missing_tables)}'
                    )
                )
                self.stdout.write(
                    '💡 Run "python manage.py migrate" to create missing tables'
                )

    def check_database_info(self):
        """Check database version and available extensions."""
        self.stdout.write("ℹ️  Checking database information...")

        with connection.cursor() as cursor:
            # Check PostgreSQL version
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            self.stdout.write(f"  📊 PostgreSQL: {version.split()[1]}")

            # Check available extensions
            cursor.execute(
                """
                SELECT extname, extversion 
                FROM pg_extension 
                WHERE extname IN ('uuid-ossp', 'pg_trgm', 'btree_gin')
            """
            )
            extensions = cursor.fetchall()

            if extensions:
                self.stdout.write("  🔌 Extensions:")
                for ext_name, ext_version in extensions:
                    self.stdout.write(f"    - {ext_name} v{ext_version}")
            else:
                self.stdout.write("  🔌 No custom extensions found")

            # Check database size
            cursor.execute(
                """
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """
            )
            db_size = cursor.fetchone()[0]
            self.stdout.write(f"  💾 Database size: {db_size}")

            # Check connection info
            db_name = connection.settings_dict.get("NAME", "Unknown")
            db_host = connection.settings_dict.get("HOST", "Unknown")
            db_port = connection.settings_dict.get("PORT", "Unknown")
            self.stdout.write(f"  🗄️  Connected to: {db_name} on {db_host}:{db_port}")
