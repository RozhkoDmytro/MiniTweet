terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.1"
    }
  }
}

provider "docker" {}

# Create Docker network
resource "docker_network" "minitweet_network" {
  name = "minitweet_network"
}

# Create postgres image
resource "docker_image" "postgres" {
  name = "postgres:15"
}

# Create postgres container
resource "docker_container" "postgres" {
  name  = "minitweet_postgres"
  image = docker_image.postgres.name

  # Environment variables
  env = [
    "POSTGRES_DB=tweet_db",
    "POSTGRES_USER=postgres",
    "POSTGRES_PASSWORD=admin",
    "POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C",
  ]

  # Port mapping
  ports {
    internal = 5432
    external = 5432
  }

  # Volume for data persistence
  volumes {
    host_path      = abspath("${path.root}/postgres_data")
    container_path = "/var/lib/postgresql/data"
  }

  # Network configuration
  networks_advanced {
    name = docker_network.minitweet_network.name
  }

  # Restart policy
  restart = "unless-stopped"

  # Health check
  healthcheck {
    test        = ["CMD", "pg_isready", "-U", "postgres", "-d", "tweet_db"]
    interval    = "10s"
    timeout     = "5s"
    retries     = 5
    start_period = "0s"
  }
}

# Use local Dockerfile to build the image
resource "docker_image" "minitweet_web" {
  name = "minitweet_web:latest"
  build {
    context    = "../"  # Path to the directory with Dockerfile
    dockerfile = "Dockerfile"
    tag        = ["minitweet_web:latest"]
  }
}

# Create web container
resource "docker_container" "minitweet_web" {
  name  = "minitweet_web"
  image = docker_image.minitweet_web.name

  # Port mapping
  ports {
    internal = 8000
    external = 8000
  }

  # Environment variables
  env = [
    "DJANGO_SETTINGS_MODULE=minitweet.docker_settings",
    "DEBUG=1",
    "DB_HOST=minitweet_postgres", # Using the name of the Postgres container
    "DB_PORT=5432",
    "DB_NAME=tweet_db",
    "DB_USER=postgres",
    "DB_PASSWORD=admin",
    "SECRET_KEY=django-insecure-*-yfj-ak#ppp!*h7+4wwnb$hhpop*m+b)c_y0o28#h1dh63594",
  ]

  # Volume declaration
  volumes {
    host_path      = abspath("${path.root}/media_data")
    container_path = "/app/media"
  }
  volumes {
    host_path      = abspath("${path.root}/static_data")
    container_path = "/app/static"
  }

  # Network configuration
  networks_advanced {
    name = docker_network.minitweet_network.name
  }

  # Dependency on PostgreSQL
  depends_on = [
    docker_container.postgres,
  ]

  # Restart policy
  restart = "unless-stopped"
}
