pipeline {
    agent any
    
    environment {
        APP_NAME = 'salon-booking'
        APP_PORT = '5000'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                    url: 'https://github.com/RanjithKDevops/salon-booking-app.git',
                    credentialsId: 'github-credentials'
            }
        }
        
        stage('CI: Static Code Analysis') {
            parallel {
                stage('Security Scan with Bandit') {
                    steps {
                        sh '''
                            python3 -m pip install bandit --user || true
                            ~/.local/bin/bandit -r . -f html -o bandit-report.html || true
                        '''
                        publishHTML([
                            reportDir: '.',
                            reportFiles: 'bandit-report.html',
                            reportName: 'Bandit Security Report',
                            allowMissing: true
                        ])
                    }
                }
                
                stage('Dependency Scan with Safety') {
                    steps {
                        sh '''
                            python3 -m pip install safety --user || true
                            ~/.local/bin/safety check --full-report || true
                        '''
                    }
                }
                
                stage('Linting with Flake8') {
                    steps {
                        sh '''
                            python3 -m pip install flake8 --user || true
                            ~/.local/bin/flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                        '''
                    }
                }
            }
        }
        
        stage('CI: Unit Tests') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    python3 -m pip install --upgrade pip
                    python3 -m pip install -r requirements.txt
                    python3 -m pip install pytest pytest-cov
                    python3 -m pytest tests/ --cov=. --junitxml=test-results.xml || true
                '''
                junit 'test-results.xml'
            }
        }
        
        stage('CI: Build Artifact') {
            steps {
                sh '''
                    # Create deployment package
                    zip -r ${APP_NAME}.zip . -x "*.git*" "*venv*" "*.pytest_cache*" "*__pycache__*"
                '''
                archiveArtifacts artifacts: "${APP_NAME}.zip"
            }
        }
        
        stage('CD: Deploy Application') {
            steps {
                sh '''
                    # Kill any existing process on port 5000
                    fuser -k 5000/tcp || true
                    
                    # Setup virtual environment
                    if [ ! -d "venv" ]; then
                        python3 -m venv venv
                    fi
                    . venv/bin/activate
                    python3 -m pip install -r requirements.txt
                    
                    # Run application in background
                    nohup python3 app.py > app.log 2>&1 &
                    
                    # Wait for app to start
                    sleep 5
                '''
            }
        }
        
        stage('CD: Health Check') {
            steps {
                sh '''
                    # Test if application is running
                    curl -f http://localhost:5000/health || exit 1
                    echo "✅ Application is healthy!"
                    
                    # Get public IP
                    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
                    echo "✅ Application is running at: http://$PUBLIC_IP:5000"
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}
