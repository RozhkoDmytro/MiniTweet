# MiniTweet

A lightweight Twitter-like application built with Django and PostgreSQL, designed for easy deployment with Docker.

## 🚀 Features

- **Tweet Management**: Create, read, update, and delete tweets
- **Image Support**: Upload images with tweets (5MB limit)
- **Reply System**: Reply to existing tweets
- **User Authentication**: Built-in Django admin interface
- **PostgreSQL Database**: Robust data storage
- **Docker Ready**: Complete containerization setup

## 🏗️ Project Structure

```
MiniTweet/
├── minitweet/          # Django project settings
├── tweets/             # Main application
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Multi-container setup
├── docker-start.sh     # Startup script
├── docker-restart.sh   # Restart script
├── env.example         # Environment template
└── requirements.txt    # Python dependencies
```

## 🐳 Docker Setup

### Prerequisites

- Docker
- Docker Compose

### Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd MiniTweet
   ```

2. **Start the application:**
   ```bash
   ./docker-start.sh
   ```

3. **Access the application:**
   - Web app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - Database: localhost:5432

### Docker Commands

#### Start the application:
```bash
./docker-start.sh
```
This script:
- Creates `.env` file from template
- Cleans local directories
- Builds and starts containers

#### Restart with cleanup:
```bash
./docker-restart.sh
```
This script:
- Stops containers
- Removes volumes for clean state
- Rebuilds and starts containers

#### Manual Docker commands:
```bash
# Start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild and start
docker-compose up --build -d

# Access web container
docker-compose exec web bash

# Access database
docker-compose exec postgres psql -U postgres -d tweet_db
```

## ⚙️ Configuration

### Environment Variables

Copy `env.example` to `.env` and customize:

```bash
# Database
DB_NAME=tweet_db
DB_USER=postgres
DB_PASSWORD=admin
DB_PORT=5432

# Web Application
WEB_PORT=8000
DEBUG=1

# Django Settings
DJANGO_SETTINGS_MODULE=minitweet.docker_settings
```

### Database Configuration

- **Host**: postgres (Docker service name)
- **Port**: 5432
- **Database**: tweet_db
- **User**: postgres
- **Password**: admin (change in production!)

### File Storage

- **Development**: Files stored in local `./media` and `./static` folders
- **Docker**: Files stored in Docker volumes (`media_data`, `static_data`)

## 🔧 Development

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start development server:**
   ```bash
   python manage.py runserver
   ```

### Docker Development

The Docker setup automatically:
- Runs database migrations
- Creates admin user (admin/admin)
- Collects static files
- Handles database health checks

## 📊 Database

### Models

- **Tweet**: Text content, images, user association, reply functionality
- **User**: Django's built-in user model

### Management Commands

```bash
# Check database connectivity
python manage.py check_database

# Setup database (creates tables, superuser)
python manage.py setup_database
```

## 🚀 Production Deployment

### Security Considerations

1. **Change default passwords** in `.env`
2. **Generate new SECRET_KEY**:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
3. **Set DEBUG=0** in production
4. **Use production database** with strong passwords
5. **Configure proper ALLOWED_HOSTS**

### Environment Variables for Production

```bash
DEBUG=0
DJANGO_SETTINGS_MODULE=minitweet.settings
SECRET_KEY=your-very-long-random-secret-key-here
DB_PASSWORD=your-very-secure-database-password
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Change `WEB_PORT` or `DB_PORT` in `.env`
2. **Database connection**: Ensure PostgreSQL container is healthy
3. **File permissions**: Check Docker volume permissions
4. **Memory issues**: Increase Docker memory limits

### Reset Everything

```bash
# Stop and remove everything
docker-compose down -v

# Remove volumes
docker volume rm minitweet_media_data minitweet_static_data

# Start fresh
./docker-start.sh
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker
5. Submit a pull request

---

**Note**: This is a development setup. For production deployment, ensure proper security configurations and use production-grade databases and web servers.
