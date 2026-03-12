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
                    
                    # Install Python packages in virtual env
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                    pip install pylint pytest-cov
                    
                    echo "✅ Virtual environment setup complete"
                '''
            }
        }
        
        stage('CI: Static Code Analysis') {
            parallel {
                stage('Security Scan with Bandit') {
                    steps {
                        sh '''
                            bandit -r . -f html -o bandit-report.html || true
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
                            safety check --full-report || true
                        '''
                    }
                }
                
                stage('Linting with Flake8') {
                    steps {
                        sh '''
                            flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                        '''
                    }
                }
                
                stage('Linting with Pylint') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            pylint app.py --exit-zero || echo "Pylint completed with issues"
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
                    
                    # Initialize database using app.py's built-in function
                    python3 -c "
from app import app, init_db
with app.app_context():
    init_db()
    print('Database initialized successfully')
"
                    
                    # Run application
                    nohup python3 app.py > app.log 2>&1 &
                    sleep 5
                '''
            }
        }
        
        stage('CD: Health Check') {
            steps {
                sh '''
                    curl -f http://localhost:5000/health || exit 1
                    echo "✅ Application is healthy!"
                    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "3.236.201.10")
                    echo "✅ Application is running at: http://$PUBLIC_IP:5000"
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
