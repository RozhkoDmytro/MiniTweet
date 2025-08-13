#!/bin/bash

# MiniTweet Docker Restart Script with Volume Cleanup

echo "🔄 Restarting MiniTweet with Docker..."

# Stop and remove containers
echo "🛑 Stopping containers..."
docker-compose down

# Remove volumes to ensure clean state
echo "🗑️  Removing volumes to ensure clean state..."
docker volume rm minitweet_media_data minitweet_static_data 2>/dev/null || true

# Clean up local directories
echo "🧹 Cleaning up local media and static directories..."
rm -rf media/ static/ staticfiles/

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose up --build -d

echo "✅ MiniTweet has been restarted!"
echo "🌐 Web app will be available at: http://localhost:8000"
echo "🗄️  PostgreSQL will be available at: localhost:5432"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop: docker-compose down"
echo "  Access web container: docker-compose exec web bash"
echo "  Access database: docker-compose exec postgres psql -U postgres -d tweet_db"
