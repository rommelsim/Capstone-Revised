pipeline{
    agent any

    stages{
        stage('Checkout'){
            steps{
                checkout scm
            }
        }
        stage('Checking Python Version'){
            steps{
                script{
                    bat "python --version"
                }
            }
        }
        stage('Installing Virtual Environment'){
            steps{
                script{
                    bat "python -m venv venv"   // Create venv
                }
            }
        }
        stage('Install Dependencies'){
            steps{
                script{
                    bat """
                        call venv\\Scripts\\activate
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                    """
                }
            }
        }
        stage('Run Robot'){
            steps{
                script{
                    bat """
                        call venv\\Scripts\\activate
                        robot --outputdir results Robot\inferencer.robot
                    """
                }
            }
        }
    }
}