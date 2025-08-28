pipeline {
    agent any
    
    environment {
        DJANGO_SETTINGS_MODULE = 'minitweet.docker_settings'
        PYTHONPATH = '/workspace/terraform'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                git url: 'https://github.com/RozhkoDmytro/MiniTweet.git', branch: 'main'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh 'pip3 install -r requirements.txt'
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running Django tests with pytest...'
                sh 'python3 -m pytest tweets/tests/ -v --tb=short'
            }
        }
        
        stage('Terraform Plan') {
            steps {
                echo 'Planning Terraform changes...'
                dir('/workspace/terraform') {
                    sh 'terraform init'
                    sh 'terraform plan -out=tfplan'
                }
            }
        }
        
        stage('Terraform Apply') {
            when {
                branch 'main'
            }
            steps {
                echo 'Applying Terraform changes...'
                dir('/workspace/terraform') {
                    sh 'terraform apply tfplan'
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed!'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}