"""
Django management command to set up the database with proper extensions and initial data.
This command should be run after the PostgreSQL container is started.
"""

import logging
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Set up database with proper extensions and initial data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force setup even if database already exists",
        )

    def handle(self, *args, **options):
        force = options["force"]

        self.stdout.write(self.style.SUCCESS("🚀 Setting up database for MiniTweet..."))

        try:
            # Create database if it doesn't exist
            self.create_database_if_not_exists()

            # Enable required extensions
            self.enable_extensions()

            # Run migrations
            self.run_migrations()

            # Create superuser if needed
            self.create_superuser_if_needed()

            self.stdout.write(
                self.style.SUCCESS("🎉 Database setup completed successfully!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Database setup failed: {e}"))
            raise e

    def create_database_if_not_exists(self):
        """Create the database if it doesn't exist."""
        self.stdout.write("🗄️  Checking database existence...")

        # Connect to default postgres database first
        default_db_settings = connection.settings_dict.copy()
        default_db_settings["NAME"] = "postgres"

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:
            # If we can't connect to postgres database, try to create it
            self.stdout.write(
                "⚠️  Cannot connect to postgres database, trying to create tweet_db directly..."
            )
            return

        # Check if our database exists
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM pg_database WHERE datname = %s
            """,
                [connection.settings_dict["NAME"]],
            )

            if cursor.fetchone():
                self.stdout.write(
                    f'✅ Database {connection.settings_dict["NAME"]} already exists'
                )
                return

        # Create the database
        self.stdout.write(f'🔧 Creating database {connection.settings_dict["NAME"]}...')

        # Close current connection
        connection.close()

        # Connect to postgres database to create our database
        from django.db import connections

        postgres_connection = connections.create_connection(default_db_settings)

        with postgres_connection.cursor() as cursor:
            cursor.execute(
                f"""
                CREATE DATABASE "{connection.settings_dict['NAME']}"
                WITH 
                OWNER = postgres
                ENCODING = 'UTF8'
                LC_COLLATE = 'C'
                LC_CTYPE = 'C'
                TEMPLATE = template0
            """
            )

        postgres_connection.close()

        # Reconnect to our database
        connection.ensure_connection()
        self.stdout.write(
            f'✅ Database {connection.settings_dict["NAME"]} created successfully'
        )

    def enable_extensions(self):
        """Enable required PostgreSQL extensions."""
        self.stdout.write("🔌 Enabling PostgreSQL extensions...")

        extensions = [
            "uuid-ossp",  # For UUID generation
            "pg_trgm",  # For text search
            "btree_gin",  # For better indexing
        ]

        with connection.cursor() as cursor:
            for extension in extensions:
                try:
                    cursor.execute(f'CREATE EXTENSION IF NOT EXISTS "{extension}"')
                    self.stdout.write(f"  ✅ {extension}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ⚠️  {extension}: {e}"))

    def run_migrations(self):
        """Run Django migrations."""
        self.stdout.write("🔄 Running Django migrations...")

        try:
            call_command("migrate", verbosity=0)
            self.stdout.write("✅ Migrations completed successfully")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Migrations failed: {e}"))
            raise e

    def create_superuser_if_needed(self):
        """Create a superuser if none exists."""
        self.stdout.write("👤 Checking for superuser...")

        from django.contrib.auth.models import User

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("✅ Superuser already exists")
            return

        self.stdout.write("🔧 No superuser found. Creating one...")
        self.stdout.write(
            "💡 You can create a superuser manually with: python manage.py createsuperuser"
        )

        # Optionally create a default superuser
        try:
            User.objects.create_superuser(
                username="admin", email="admin@minitweet.com", password="admin123"
            )
            self.stdout.write(
                "✅ Default superuser created (username: admin, password: admin123)"
            )
            self.stdout.write("⚠️  Remember to change the password in production!")
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Could not create default superuser: {e}")
            )


