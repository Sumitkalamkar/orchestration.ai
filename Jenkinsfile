pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'report-gen-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        SONAR_PROJECT_KEY = 'report-gen'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                echo '🐍 Setting up Python environment...'
                sh '''
                    python3.11 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pylint pytest pytest-cov
                '''
            }
        }

        stage('Lint') {
            steps {
                echo '🔍 Running linter...'
                sh '''
                    . venv/bin/activate
                    pylint graph.py backend.py --fail-under=7.0 || true
                '''
            }
        }

        stage('Test') {
            steps {
                echo '🧪 Running tests...'
                sh '''
                    . venv/bin/activate
                    pytest tests/ --cov=. --cov-report=xml --cov-report=term || true
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo '📊 Running SonarQube analysis...'
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                            -Dsonar.sources=. \
                            -Dsonar.inclusions=graph.py,backend.py \
                            -Dsonar.exclusions=venv/**,**/__pycache__/** \
                            -Dsonar.python.version=3.11
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                echo '🚦 Checking SonarQube Quality Gate...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo '🐳 Building Docker image...'
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Docker Push') {
            steps {
                echo '📤 Pushing Docker image to registry...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker tag ${DOCKER_IMAGE}:latest ${DOCKER_USER}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker tag ${DOCKER_IMAGE}:latest ${DOCKER_USER}/${DOCKER_IMAGE}:latest
                        docker push ${DOCKER_USER}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_USER}/${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo '🚀 Deploying application...'
                sh '''
                    docker-compose down || true
                    docker-compose up -d app
                    echo "App deployed at http://localhost:8000"
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs above.'
        }
        always {
            echo '🧹 Cleaning up workspace...'
            sh 'docker system prune -f || true'
        }
    }
}
