#!/bin/bash

# MiniTweet Docker Startup Script

echo "🐳 Starting MiniTweet with Docker..."

# Check if .env exists, if not create from template
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. You can edit it to customize settings."
fi

# Clean up local media and static directories to avoid conflicts
echo "🧹 Cleaning up local media and static directories..."
rm -rf media/ static/ staticfiles/
echo "✅ Local directories cleaned up"

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose up --build -d

echo "✅ MiniTweet is starting up!"
echo "🌐 Web app will be available at: http://localhost:8000"
echo "🗄️  PostgreSQL will be available at: localhost:5432"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop: docker-compose down"
echo "  Restart: docker-compose restart"
echo "  Access web container: docker-compose exec web bash"
echo "  Access database: docker-compose exec postgres psql -U postgres -d tweet_db"
