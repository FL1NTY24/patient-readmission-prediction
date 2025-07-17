# Summary of executed PowerShell Commands for Cloud Setup

# 1. Installed and Configured WSL2 (for Docker)

Installed WSL2 and Virtual Machine Platform:

wsl --install

wsl --set-default-version 2

Installed Ubuntu:

wsl --install -d Ubuntu

Updated WSL:

wsl --update

Verified:

wsl --version

wsl -l -v

# 2. Installed Docker Desktop

Downloaded from docker.com and installed manually.
Configured WSL2 integration in Docker Desktop Settings > Resources > WSL Integration.

Verified:

docker --version

docker run hello-world

docker-compose --version

# 3. Installed Terraform
Downloaded from terraform.io/downloads (e.g., terraform_1.9.4_windows_amd64.zip).
Unzipped and moved terraform.exe to C:\Program Files\Terraform.

Added to PATH (manual via System > Environment Variables > Path)

Verified:

terraform -version

# 4. Installed LocalStack

Verified Python and pip:

python --version

pip --version

Installed LocalStack:

pip install localstack --user

Added Python Scripts to PATH (e.g., C:\Users\GabrielF\AppData\Roaming\Python\Python313\Scripts):

Verified:

localstack --version

Tested with Docker running:

localstack start -d

localstack stop

# 5. Installed and Configured AWS CLI

Installed (download from aws.amazon.com/cli, run .msi)

Verified:
aws --version

Configured:

aws configure

Entered: Required information (Access keys + region etc)

Tested (after adding S3 permissions to IAM user GabrielFlint24):

aws s3 ls
