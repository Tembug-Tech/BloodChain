pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('docker-hub-credentials')
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE_NAME = 'bloodchain'
        DOCKER_IMAGE_TAG = "${BUILD_NUMBER}"
        KUBECONFIG = credentials('kubeconfig')
        GITHUB_REPO = 'https://github.com/yourusername/bloodchain.git'
        PYTHON_VERSION = '3.11'
        COVERAGE_THRESHOLD = '80'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "========== Checking out code from GitHub =========="
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: '*/main']],
                        userRemoteConfigs: [[url: env.GITHUB_REPO]]
                    ])
                    echo "✓ Code checked out successfully"
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    echo "========== Installing Dependencies =========="
                    try {
                        sh '''
                            # Create virtual environment
                            python${PYTHON_VERSION} -m venv venv
                            
                            # Activate virtual environment and install dependencies
                            . venv/bin/activate
                            
                            # Upgrade pip
                            pip install --upgrade pip setuptools wheel
                            
                            # Install requirements
                            pip install -r requirements.txt
                            pip install pytest pytest-cov pytest-django
                            
                            echo "✓ Dependencies installed successfully"
                        '''
                    } catch (Exception e) {
                        echo "✗ Failed to install dependencies: ${e.message}"
                        currentBuild.result = 'FAILURE'
                        error("Dependency installation failed")
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "========== Running Tests with Coverage =========="
                    try {
                        sh '''
                            . venv/bin/activate
                            
                            # Create test reports directory
                            mkdir -p test-reports
                            
                            # Run pytest with coverage
                            pytest \
                                --cov=donor \
                                --cov=hospital \
                                --cov=blood_tracking \
                                --cov=notifications \
                                --cov=rewards \
                                --cov=blockchain \
                                --cov-report=html:test-reports/coverage \
                                --cov-report=xml:test-reports/coverage.xml \
                                --cov-report=term \
                                --junitxml=test-reports/junit.xml \
                                -v
                        '''
                        
                        // Parse coverage report
                        sh '''
                            . venv/bin/activate
                            COVERAGE=$(python -c "
                            import xml.etree.ElementTree as ET
                            tree = ET.parse('test-reports/coverage.xml')
                            root = tree.getroot()
                            coverage = float(root.attrib['line-rate']) * 100
                            print(f'{coverage:.2f}')
                            ")
                            
                            echo "Code Coverage: ${COVERAGE}%"
                            
                            # Compare with threshold
                            if (( $(echo "${COVERAGE} < ${COVERAGE_THRESHOLD}" | bc -l) )); then
                                echo "✗ Coverage ${COVERAGE}% is below threshold ${COVERAGE_THRESHOLD}%"
                                exit 1
                            fi
                            
                            echo "✓ Coverage ${COVERAGE}% meets threshold ${COVERAGE_THRESHOLD}%"
                        '''
                        
                    } catch (Exception e) {
                        echo "✗ Tests failed or coverage below threshold: ${e.message}"
                        currentBuild.result = 'FAILURE'
                        error("Test execution or coverage check failed")
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "========== Building Docker Image =========="
                    try {
                        sh '''
                            # Build Docker image with build number tag
                            docker build \
                                --tag ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} \
                                --tag ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:latest \
                                --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VCS_REF=$(git rev-parse --short HEAD) \
                                --build-arg BUILD_NUMBER=${BUILD_NUMBER} \
                                .
                            
                            echo "✓ Docker image built successfully"
                            docker images | grep ${DOCKER_IMAGE_NAME}
                        '''
                    } catch (Exception e) {
                        echo "✗ Docker build failed: ${e.message}"
                        currentBuild.result = 'FAILURE'
                        error("Docker image build failed")
                    }
                }
            }
        }

        stage('Push to Registry') {
            steps {
                script {
                    echo "========== Pushing Docker Image to Registry =========="
                    try {
                        sh '''
                            # Login to Docker Hub
                            echo "${DOCKER_HUB_CREDENTIALS_PSW}" | docker login \
                                --username ${DOCKER_HUB_CREDENTIALS_USR} \
                                --password-stdin ${DOCKER_REGISTRY}
                            
                            # Push image with build number tag
                            docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
                            
                            # Push latest tag
                            docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:latest
                            
                            # Logout
                            docker logout ${DOCKER_REGISTRY}
                            
                            echo "✓ Docker image pushed to registry successfully"
                        '''
                    } catch (Exception e) {
                        echo "✗ Docker push failed: ${e.message}"
                        currentBuild.result = 'FAILURE'
                        error("Docker image push to registry failed")
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "========== Deploying to Kubernetes =========="
                    try {
                        sh '''
                            # Set kubeconfig
                            export KUBECONFIG=${KUBECONFIG}
                            
                            # Apply namespace
                            kubectl apply -f devops/kubernetes/namespace.yaml
                            
                            # Apply ConfigMap and Secrets
                            kubectl apply -f devops/kubernetes/configmap.yaml
                            kubectl apply -f devops/kubernetes/secret.yaml
                            
                            # Apply database and cache deployments
                            kubectl apply -f devops/kubernetes/postgres-deployment.yaml
                            kubectl apply -f devops/kubernetes/redis-deployment.yaml
                            
                            # Update web deployment image
                            kubectl set image deployment/web \
                                django=${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} \
                                -n bloodchain \
                                --record || \
                            kubectl apply -f devops/kubernetes/web-deployment.yaml
                            
                            # Apply nginx and services
                            kubectl apply -f devops/kubernetes/nginx-deployment.yaml
                            kubectl apply -f devops/kubernetes/services.yaml
                            
                            echo "✓ Kubernetes deployment applied successfully"
                        '''
                    } catch (Exception e) {
                        echo "✗ Kubernetes deployment failed: ${e.message}"
                        currentBuild.result = 'FAILURE'
                        error("Kubernetes deployment failed")
                    }
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo "========== Verifying Deployment Health =========="
                    try {
                        sh '''
                            export KUBECONFIG=${KUBECONFIG}
                            
                            # Wait for deployments to be ready
                            echo "Waiting for deployments to be ready..."
                            kubectl rollout status deployment/web -n bloodchain --timeout=5m
                            kubectl rollout status deployment/postgres -n bloodchain --timeout=5m
                            kubectl rollout status deployment/redis -n bloodchain --timeout=5m
                            kubectl rollout status deployment/nginx -n bloodchain --timeout=5m
                            
                            # Check pod status
                            echo ""
                            echo "Pod Status:"
                            kubectl get pods -n bloodchain -o wide
                            
                            # Check service status
                            echo ""
                            echo "Service Status:"
                            kubectl get svc -n bloodchain
                            
                            # Check for any pod errors
                            FAILED_PODS=$(kubectl get pods -n bloodchain --field-selector=status.phase!=Running,status.phase!=Succeeded)
                            if [ ! -z "$FAILED_PODS" ]; then
                                echo "✗ Some pods are not running:"
                                kubectl get pods -n bloodchain
                                exit 1
                            fi
                            
                            echo "✓ All deployments are healthy"
                            
                            # Get LoadBalancer external IP/port
                            echo ""
                            echo "Application Access Information:"
                            kubectl get svc nginx-service -n bloodchain
                        '''
                    } catch (Exception e) {
                        echo "✗ Health check failed: ${e.message}"
                        currentBuild.result = 'FAILURE'
                        error("Health check failed")
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                echo "========== Collecting Artifacts =========="
                
                // Archive test reports
                junit testResults: 'test-reports/junit.xml', allowEmptyResults: true
                
                // Archive coverage reports
                publishHTML([
                    reportDir: 'test-reports/coverage',
                    reportFiles: 'index.html',
                    reportName: 'Code Coverage Report'
                ])
                
                // Clean up
                cleanWs(
                    deleteDirs: true,
                    patterns: [
                        [pattern: 'venv/', type: 'INCLUDE'],
                        [pattern: '.pytest_cache/', type: 'INCLUDE'],
                        [pattern: '__pycache__/', type: 'INCLUDE']
                    ]
                )
            }
        }

        success {
            script {
                echo "========== PIPELINE SUCCESS =========="
                sh '''
                    echo "✓ Pipeline completed successfully"
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Docker Image: ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
                '''
                
                // Send success notification (Slack example)
                // slackSend(
                //     color: 'good',
                //     message: "BloodChain Pipeline #${BUILD_NUMBER} Succeeded\n" +
                //              "Docker Image: ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}\n" +
                //              "View: ${BUILD_URL}",
                //     channel: '#deployments'
                // )
                
                // Send success notification (Email example)
                // emailext(
                //     subject: "BloodChain Pipeline #${BUILD_NUMBER} - SUCCESS",
                //     body: """
                //         Pipeline Execution: SUCCESS
                //         Build Number: ${BUILD_NUMBER}
                //         Docker Image: ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
                //         View Details: ${BUILD_URL}
                //     """,
                //     to: 'devops@bloodchain.dev'
                // )
            }
        }

        failure {
            script {
                echo "========== PIPELINE FAILURE =========="
                sh '''
                    echo "✗ Pipeline failed"
                    echo "Build Number: ${BUILD_NUMBER}"
                '''
                
                // Send failure notification (Slack example)
                // slackSend(
                //     color: 'danger',
                //     message: "BloodChain Pipeline #${BUILD_NUMBER} Failed\n" +
                //              "View: ${BUILD_URL}console",
                //     channel: '#deployments'
                // )
                
                // Send failure notification (Email example)
                // emailext(
                //     subject: "BloodChain Pipeline #${BUILD_NUMBER} - FAILURE",
                //     body: """
                //         Pipeline Execution: FAILURE
                //         Build Number: ${BUILD_NUMBER}
                //         Console Output: ${BUILD_URL}console
                //         View Details: ${BUILD_URL}
                //     """,
                //     to: 'devops@bloodchain.dev'
                // )
            }
        }

        unstable {
            script {
                echo "========== PIPELINE UNSTABLE =========="
                echo "Pipeline completed with warnings"
            }
        }

        cleanup {
            script {
                echo "========== Pipeline Cleanup =========="
                sh '''
                    # Remove kubeconfig if it was created
                    if [ -f "${KUBECONFIG}" ]; then
                        rm -f "${KUBECONFIG}"
                    fi
                    
                    # Cleanup old Docker images (keep last 5)
                    docker image prune -a -f --filter "until=168h" || true
                '''
            }
        }
    }
}
