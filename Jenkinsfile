pipeline {
    agent any // Specifies that Jenkins can use any available agent to run the pipeline

    environment {
        // It's good practice to define the Python version or path if necessary
        // For simplicity, we assume python3 and pip are in the PATH
        // VENV_DIR = '.venv' // Define virtual environment directory
    }

    stages {
        stage('Checkout') {
            steps {
                // This step checks out the code from version control
                // For a multibranch pipeline or Jenkins job configured with SCM,
                // this is often handled automatically or by a simple `checkout scm`
                git branch: env.BRANCH_NAME, url: env.GIT_URL // Assumes GIT_URL and BRANCH_NAME are available Jenkins environment variables
                                                            // For a simple Jenkinsfile in SCM, `checkout scm` is more common.
                                                            // Let's use `checkout scm` for broader compatibility.
                checkout scm
                echo "Checked out code from ${scm.getUserRemoteConfigs()[0].getUrl()} on branch ${scm.getBranches()[0].getName()}"
            }
        }

        stage('Setup Python Environment') {
            steps {
                script {
                    // Check if python3 is available
                    sh 'python3 --version'
                    // Create a virtual environment
                    // Using a timestamp or build number for uniqueness if needed, but '.venv' is common
                    sh 'python3 -m venv .venv'
                    // Activate virtual environment and ensure pip is upgraded
                    // Activation within a sh step is tricky as it doesn't persist across sh steps.
                    // So, we'll prefix commands with the venv path.
                    sh ".venv/bin/pip install --upgrade pip"
                    echo "Python virtual environment created and pip upgraded."
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                // Install dependencies using pip from the virtual environment
                sh ".venv/bin/pip install -r requirements.txt"
                echo "Dependencies installed."
            }
        }

        stage('Run Tests') {
            steps {
                // Run pytest tests using python from the virtual environment
                sh ".venv/bin/pytest"
                echo "Pytest tests executed."
            }
        }
    }

    post {
        always {
            // Clean up the virtual environment
            // deleteDir() // This can be problematic if not careful, ensure it only deletes .venv
            // sh 'rm -rf .venv' // More direct, but ensure it's safe
            echo "Pipeline finished. Workspace cleanup can be added here if necessary."
        }
        // Example:
        // success {
        //     echo 'Pipeline successful!'
        // }
        // failure {
        //     echo 'Pipeline failed.'
        //     // mail to: 'team@example.com', subject: "Build FAILED: ${currentBuild.fullDisplayName}"
        // }
    }
}
