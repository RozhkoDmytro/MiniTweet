#!/bin/bash

# Docker commands for MiniTweet PostgreSQL setup

case "$1" in
    "start")
        echo "Starting PostgreSQL container..."
        docker-compose up -d postgres
        echo "PostgreSQL is starting up..."
        echo "Wait a few seconds for the database to be ready"
        ;;
    "stop")
        echo "Stopping PostgreSQL container..."
        docker-compose stop postgres
        ;;
    "restart")
        echo "Restarting PostgreSQL container..."
        docker-compose restart postgres
        ;;
    "status")
        echo "PostgreSQL container status:"
        docker-compose ps postgres
        ;;
    "logs")
        echo "PostgreSQL container logs:"
        docker-compose logs postgres
        ;;
    "connect")
        echo "Connecting to PostgreSQL database..."
        docker exec -it minitweet_postgres psql -U postgres -d tweet_db
        ;;
    "check-db")
        echo "Checking database connectivity and tables..."
        python3 manage.py check_database
        ;;
    "setup-db")
        echo "Setting up database with Django..."
        python3 manage.py setup_database
        ;;
    "reset")
        echo "WARNING: This will remove all data!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Stopping and removing PostgreSQL container and data..."
            docker-compose down -v
            echo "PostgreSQL data has been reset"
        else
            echo "Operation cancelled"
        fi
        ;;
    "setup")
        echo "Setting up PostgreSQL for the first time..."
        docker-compose up -d postgres
        echo "Waiting for PostgreSQL to be ready..."
        sleep 10
        echo "Setting up database with Django..."
        python3 manage.py setup_database
        echo "Setup complete!"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|connect|reset|setup}"
        echo ""
        echo "Commands:"
        echo "  start   - Start PostgreSQL container"
        echo "  stop    - Stop PostgreSQL container"
        echo "  restart - Restart PostgreSQL container"
        echo "  status  - Show container status"
        echo "  logs    - Show container logs"
        echo "  connect - Connect to database via psql"
        echo "  reset   - Remove container and all data"
        echo "  setup   - First-time setup with migrations"
        exit 1
        ;;
esac
