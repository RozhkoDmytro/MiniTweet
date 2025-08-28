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

# =============================================================================
# JENKINS INFRASTRUCTURE
# =============================================================================

# Create Jenkins Master image
resource "docker_image" "jenkins_master" {
  name = "jenkins/jenkins:lts-jdk17"
}

# Create Jenkins Master container
resource "docker_container" "jenkins_master" {
  name  = "jenkins_master"
  image = docker_image.jenkins_master.name

  # Port mapping
  ports {
    internal = 8080
    external = 8080
  }
  ports {
    internal = 50000
    external = 50000
  }

  # Environment variables
  env = [
    "JENKINS_OPTS=--httpPort=8080",
    "JAVA_OPTS=-Djenkins.install.runSetupWizard=false -Duser.language=en -Duser.country=US -Dhudson.model.Language=en",
    "LANG=en_US.UTF-8",
    "LC_ALL=en_US.UTF-8",
    "JENKINS_LANG=en"
  ]

  # Volume for Jenkins data persistence
  volumes {
    host_path      = abspath("${path.root}/jenkins_data")
    container_path = "/var/jenkins_home"
  }

  # Network configuration
  networks_advanced {
    name = docker_network.minitweet_network.name
  }

  # Restart policy
  restart = "unless-stopped"

  # Health check
  healthcheck {
    test        = ["CMD", "curl", "-f", "http://localhost:8080/login"]
    interval    = "30s"
    timeout     = "10s"
    retries     = 3
    start_period = "60s"
  }
}

# Create Jenkins Agent image (with Docker support)
resource "docker_image" "jenkins_agent" {
  name = "jenkins/inbound-agent:latest"
}

# Create Jenkins Agent container
resource "docker_container" "jenkins_agent" {
  name  = "jenkins_agent"
  image = docker_image.jenkins_agent.name

  # Environment variables for agent connection
  env = [
    "JENKINS_URL=http://jenkins_master:8080",
    "JENKINS_SECRET=${var.jenkins_agent_secret}",
    "JENKINS_NAME=jenkins-agent-1",
    "JENKINS_WORKDIR=/home/jenkins/agent",
  ]

  # Critical volumes for Docker access and Terraform state
  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }
  volumes {
    host_path      = abspath("${path.root}")
    container_path = "/workspace/terraform"
  }
  volumes {
    host_path      = abspath("${path.root}/jenkins_agent_data")
    container_path = "/home/jenkins/agent"
  }

  # Network configuration
  networks_advanced {
    name = docker_network.minitweet_network.name
  }

  # Dependencies
  depends_on = [
    docker_container.jenkins_master,
  ]

  # Restart policy
  restart = "unless-stopped"

  # Health check
  healthcheck {
    test        = ["CMD", "pgrep", "-f", "java"]
    interval    = "30s"
    timeout     = "10s"
    retries     = 3
    start_period = "30s"
  }
}

# Variables
variable "jenkins_agent_secret" {
  description = "Jenkins agent secret for connection (will be generated)"
  type        = string
  default     = "placeholder-secret-change-in-jenkins-ui"
}

# Outputs
output "jenkins_master_url" {
  description = "Jenkins Master URL"
  value       = "http://localhost:8080"
}

output "jenkins_agent_name" {
  description = "Jenkins Agent container name"
  value       = docker_container.jenkins_agent.name
}

output "jenkins_network" {
  description = "Jenkins network name"
  value       = docker_network.minitweet_network.name
}