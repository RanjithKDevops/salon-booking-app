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
        
        stage('CI: Setup Virtual Environment') {
            steps {
                sh '''
                    # Clean and create fresh virtual environment
                    rm -rf venv
                    python3 -m venv venv
                    . venv/bin/activate
                    
                    # Install Python packages with compatible versions
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                    
                    # Install specific versions that work with Python 3.12
                    pip install bandit==1.7.5
                    pip install safety==2.3.5
                    pip install flake8==6.1.0
                    pip install pytest-cov==4.1.0
                    
                    echo "✅ Virtual environment setup complete"
                '''
            }
        }
        
        stage('CI: Static Code Analysis') {
            parallel {
                stage('Security Scan with Bandit') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            bandit -r . -f html -o bandit-report.html || echo "Bandit found issues"
                        '''
                        publishHTML([
                            reportDir: '.',
                            reportFiles: 'bandit-report.html',
                            reportName: 'Bandit Security Report',
                            allowMissing: true,
                            alwaysLinkToLastBuild: true,
                            keepAll: true
                        ])
                    }
                }
                
                stage('Dependency Scan with Safety') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            safety check --full-report || echo "Safety found vulnerabilities"
                        '''
                    }
                }
                
                stage('Linting with Flake8') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || echo "Flake8 found issues"
                        '''
                    }
                }
            }
        }
        
        stage('CI: Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 -m pytest tests/ -v --cov=. --junitxml=test-results.xml || true
                '''
                junit 'test-results.xml'
            }
        }
        
        stage('CI: Build Artifact') {
            steps {
                sh '''
                    zip -r ${APP_NAME}.zip . -x "*.git*" "*venv*" "*.pytest_cache*" "*__pycache__*" "*.log"
                '''
                archiveArtifacts artifacts: "${APP_NAME}.zip", allowEmptyArchive: true
            }
        }
        
        stage('CD: Deploy Application') {
            steps {
                sh '''
                    # Kill any existing process
                    sudo fuser -k 5000/tcp || true
                    
                    . venv/bin/activate
                    
                    # Initialize database
                    python3 -c "
from app import app, init_db
with app.app_context():
    init_db()
    print('Database initialized successfully')
"
                    
                    # Run application
                    nohup python3 app.py > app.log 2>&1 &
                    sleep 5
                    
                    # Check if app is running
                    ps aux | grep app.py
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
                    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "3.236.201.10")
                    echo "✅ Application is running at: http://$PUBLIC_IP:5000"
                    
                    # Test homepage
                    curl -I http://localhost:5000/
                '''
            }
        }
    }
    
    post {
        always {
            junit 'test-results.xml'
            cleanWs()
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed! Check logs above for details.'
        }
    }
}
