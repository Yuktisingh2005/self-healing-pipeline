pipeline {
    agent any

    environment {
        IMAGE_NAME = "self-healing-pipeline"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Yuktisingh2005/self-healing-pipeline.git'
            }
        }

        stage('Get SHA') {
            steps {
                script {
                    env.GIT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    echo "Deploying SHA: ${env.GIT_SHA}"
                }
            }
        }

        stage('Build Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${env.GIT_SHA} ./backend"
            }
        }

        stage('Shadow Deploy + Health Check + Promote/Rollback') {
            steps {
                script {
                    def exitCode = sh(script: "python3 backend/scripts/deploy.py --sha ${env.GIT_SHA}", returnStatus: true)

                    if (exitCode == 0) {
                        echo "PROMOTED: ${env.GIT_SHA} is now live"
                        env.DEPLOY_RESULT = "promoted"
                    } else if (exitCode == 1) {
                        echo "ROLLED BACK: ${env.GIT_SHA} failed health checks"
                        env.DEPLOY_RESULT = "rolled_back"
                    } else {
                        echo "CRITICAL: pipeline crashed during promotion — needs manual check"
                        env.DEPLOY_RESULT = "crashed"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline finished. SHA: ${env.GIT_SHA}, Result: ${env.DEPLOY_RESULT}"
        }
    }
}