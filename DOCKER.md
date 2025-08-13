# Docker Setup for MiniTweet

This document explains how to run MiniTweet using Docker containers.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

### 1. Set up environment variables
```bash
cp env.example .env
# Edit .env with your desired values
```

### 2. Build and start the containers
```bash
docker-compose up --build
```

### 3. Access the application
- Web app: http://localhost:8000
- PostgreSQL: localhost:5432

### 4. Stop the containers
```bash
docker-compose down
```

## Environment Variables

The `docker-compose.yml` automatically loads environment variables from the `.env` file using the `env_file` directive.

Copy `env.example` to `.env` and customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_NAME` | `tweet_db` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `admin` | Database password |
| `DB_PORT` | `5432` | Database port |
| `WEB_PORT` | `8000` | Web application port |
| `DEBUG` | `1` | Django debug mode |
| `DOCKERFILE` | `Dockerfile` | Which Dockerfile to use |
| `SECRET_KEY` | Django default | Django secret key |

**Note**: Docker Compose automatically loads the `.env` file, so you don't need to export variables manually.

## Switching Between Development and Production

### Development Mode
```bash
# Use default settings in .env
DEBUG=1
DOCKERFILE=Dockerfile
```

### Production Mode
```bash
# Edit .env file
DEBUG=0
DOCKERFILE=Dockerfile.prod
SECRET_KEY=your-secure-secret-key-here
DB_PASSWORD=your-secure-db-password
```

## Container Architecture

- **web**: Django application container
- **postgres**: PostgreSQL database container

## Database Connection

The Django application automatically connects to the PostgreSQL container using:
- Host: `postgres` (container name)
- Port: `5432`
- Database: From `DB_NAME` environment variable
- User: From `DB_USER` environment variable
- Password: From `DB_PASSWORD` environment variable

## Volumes

- `postgres_data`: Persistent PostgreSQL data
- `media_data`: Persistent media files (user uploads)
- `static_data`: Persistent static files

## Media Files Management

### Important: Media Files Storage

When running MiniTweet in Docker containers, media files (user uploads) are stored in Docker volumes, not in your local `media/` directory. This ensures:

- Files persist between container restarts
- Files are isolated from your local development environment
- Proper separation of concerns

### Media File Operations

```bash
# Backup media files
./docker-commands.sh media-backup

# Restore media files from backup
./docker-commands.sh media-restore backup_file.tar.gz

# Clean up volumes (WARNING: This will delete all media files)
./docker-commands.sh clean-volumes
```

### Troubleshooting Media Files

If you experience issues with media files not being saved or accessed:

1. **Restart with cleanup:**
   ```bash
   ./docker-restart.sh
   ```

2. **Check volume status:**
   ```bash
   docker volume ls | grep minitweet
   ```

3. **Access files directly in container:**
   ```bash
   docker-compose exec web ls -la /app/media
   ```

4. **Reset everything:**
   ```bash
   ./docker-commands.sh reset
   ./docker-start.sh
   ```

## Health Checks

Both containers include health checks:
- PostgreSQL: Checks if database is ready to accept connections
- Web: Checks if Django application is responding

## Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build

# View specific service logs
docker-compose logs web
docker-compose logs postgres
```

### Application Management
```bash
# Start full application with cleanup
./docker-start.sh

# Restart application with volume cleanup
./docker-restart.sh

# Use management commands
./docker-commands.sh full-start
./docker-commands.sh full-restart
./docker-commands.sh clean-volumes
```

### Database Operations
```bash
# Access PostgreSQL shell
docker-compose exec postgres psql -U postgres -d tweet_db

# Run Django management commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   - Change ports in `.env` file
   - Stop other services using the same ports

2. **Database connection failed:**
   - Wait for PostgreSQL container to be healthy
   - Check environment variables in `.env`
   - Verify network configuration

3. **Permission denied:**
   - Check file permissions
   - Ensure Docker has access to project directory

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f
```

## Security Notes

- **NEVER commit `.env` file to version control**
- Change default passwords in production
- Use strong, unique passwords for production
- Consider using Docker secrets for production
- Restrict network access in production environments
