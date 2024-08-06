---
title: "Managing Credentials and Secrets in Terraform"
authorId: "rahul"
date: 2024-08-06
draft: false
featured: true
weight: 1
---

When working with Terraform, managing credentials and secrets securely is crucial. In this blog, we'll explore several methods for managing secrets and credentials securely, including environment variables, GitHub Secrets, encrypted files with AWS KMS, and AWS Secrets Manager. We’ll also compare these methods to help you choose the best approach for your needs.

### Method 1: Environment Variables

Using environment variables to manage secrets in Terraform is straightforward and commonly used. This approach keeps sensitive data like usernames and passwords out of your codebase and allows for easy integration with your CI/CD pipelines.

#### Step-by-Step Guide

Imagine you need to create an AWS RDS instance, and you want to keep the database username and password secure.

**1. Define Sensitive Variables in Terraform:**

First, define your sensitive variables in your Terraform configuration file. Marking them as sensitive ensures that Terraform treats them securely.

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_username" {
  type      = string
  sensitive = true
}
```

**2. Use Variables in Resource Definitions:**

Use these variables in your resource definitions. Here’s an example of an AWS RDS instance where the database username and password are sourced from the defined variables.

```hcl
resource "aws_db_instance" "example" {
  identifier          = "mydbinstance"
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  allocated_storage   = 10
  publicly_accessible = true
  skip_final_snapshot = true
  username            = var.db_username
  password            = var.db_password
}
```

**3. Set Environment Variables:**

Before applying your Terraform configuration, set the environment variables for the database username and password. This can be done in your shell or CI/CD pipeline configuration.

```sh
export TF_VAR_db_username="my_db_username"
export TF_VAR_db_password="my_db_password"
```

**4. Apply Terraform Configuration:**

Finally, run your Terraform commands as usual. Terraform will read the environment variables and use them to configure your resources.

```sh
terraform init
terraform plan
terraform apply
```

### Method 2: Encrypted Files (KMS)

Using encrypted files to manage secrets in Terraform is a robust approach that enhances security by leveraging AWS Key Management Service (KMS). This method ensures that sensitive information is stored in an encrypted format and decrypted only when needed by Terraform.

#### Step-by-Step Guide

Imagine you need to create an AWS RDS instance, and you want to keep the database username and password secure by storing them in an encrypted file.

**1. Create a YAML File with Credentials:**

First, create a YAML file (db-creds.yml) that contains your database credentials:

```yaml
db_username: my_db_username
db_password: my_db_password
```

**2. Encrypt the YAML File Using AWS KMS:**

*Alternative 1: Using AWS CLI*

You can use the AWS CLI to manually encrypt your YAML file:

```sh
aws kms encrypt --key-id <your-kms-key-id> --region <your-region> --plaintext fileb://db-creds.yml --output text --query CiphertextBlob > db-creds.yml.encrypted
```

Replace `<your-kms-key-id>` and `<your-region>` with your KMS key ID and AWS region, respectively.

*Alternative 2: Using Terraform*

You can also handle encryption through Terraform:

```hcl
variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_kms_key" "db_creds_key" {
  description = "KMS key for encrypting database credentials"
  tags = {
    Name = "db_creds_key"
  }
}

resource "aws_kms_ciphertext" "db_creds" {
  key_id     = aws_kms_key.db_creds_key.id
  plaintext  = jsonencode({
    db_username = var.db_username
    db_password = var.db_password
  })
  context = {
    "Purpose" = "Encrypting database credentials"
  }
}

resource "aws_secretsmanager_secret" "db_creds" {
  name = "db-credentials"
}

resource "aws_secretsmanager_secret_version" "db_creds_version" {
  secret_id     = aws_secretsmanager_secret.db_creds.id
  secret_string = aws_kms_ciphertext.db_creds.ciphertext_blob
}
```

Note: Store your secrets in a `terraform.tfvars` file or pass them as environment variables:

```hcl
# terraform.tfvars
db_username = "my_db_username"
db_password = "my_db_password"
```

Alternatively, set environment variables before running Terraform commands:

```sh
export TF_VAR_db_username="my_db_username"
export TF_VAR_db_password="my_db_password"
```

**3. Define KMS Data Source in Terraform:**

Use the `aws_secretsmanager_secret_version` data source in your Terraform configuration to retrieve and decrypt the encrypted file:

```hcl
data "aws_secretsmanager_secret_version" "creds" {
  secret_id = aws_secretsmanager_secret.db_creds.id
  depends_on = [aws_secretsmanager_secret.db_creds, aws_secretsmanager_secret_version.db_creds_version]
}

locals {
  db_cred = jsondecode(data.aws_secretsmanager_secret_version.creds.secret_string)
}
```

**4. Use Decrypted Credentials in Resource Definitions:**

Use the decrypted credentials in your resource definitions. Here’s an example of an AWS RDS instance where the database username and password are sourced from the decrypted file:

```hcl
resource "aws_db_instance" "example" {
  identifier          = "mydbinstance"
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  allocated_storage   = 10
  publicly_accessible = true
  skip_final_snapshot = true
  username            = local.db_cred.db_username
  password            = local.db_cred.db_password
}
```

**5. Apply Terraform Configuration:**

Finally, run your Terraform commands as usual. Terraform will decrypt the file using AWS KMS and use the credentials to configure your resources:

```sh
terraform init
terraform plan
terraform apply
```

### Method 3: AWS Secrets Manager

AWS Secrets Manager provides a secure way to store and manage sensitive information such as database credentials, API keys, and other secrets. This method allows you to retrieve secrets dynamically within your Terraform configuration, ensuring that sensitive data is never hard-coded in your Terraform files.

#### Step-by-Step Guide

Here’s how you can manage your database credentials using AWS Secrets Manager:

**1. Store Your Secrets in AWS Secrets Manager using Terraform:**

First, use Terraform to create a secret in AWS Secrets Manager. Define the secret in your Terraform configuration, using variables to keep sensitive information secure:

```hcl
variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_secretsmanager_secret" "mysql_cred" {
  name = "mysql-cred"
}

resource "aws_secretsmanager_secret_version" "mysql_cred_version" {
  secret_id     = aws_secretsmanager_secret.mysql_cred.id
  secret_string = jsonencode({
    db_username = var.db_username
    db_password = var.db_password
  })
}
```

Note: Store your secrets in a `terraform.tfvars` file or pass them as environment variables:

```hcl
# terraform.tfvars
db_username = "my_db_username"
db_password = "my_db_password"
```

Alternatively, set environment variables before running Terraform commands:

```sh
export TF_VAR_db_username="my_db_username"
export TF_VAR_db_password="my_db_password"
```

**2. Retrieve Secrets in Terraform:**

Use the `aws_secretsmanager_secret_version` data source to fetch the secret from AWS Secrets Manager:

```hcl
data "aws_secretsmanager_secret_version" "creds" {
  secret_id = aws_secretsmanager_secret.mysql_cred.id
  depends_on = [aws_secretsmanager_secret.mysql_cred, aws_secretsmanager_secret_version.mysql_cred_version]
}

locals {
  db_cred = jsondecode(data.aws_secretsmanager_secret_version.creds.secret_string)
}
```

**3. Use Retrieved Secrets in Resource Definitions:**

Use the retrieved credentials in your resource definitions. Here’s an example of an AWS RDS instance where the database username and password are sourced from AWS Secrets Manager:

```hcl
resource "aws_db_instance" "example" {
  identifier          = "mydbinstance"
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  allocated_storage   = 10
  publicly_accessible = true
  skip_final_snapshot = true
  username            = local.db_cred.db_username
  password            = local.db_cred.db_password
}
```

**Alternative: Store Secrets Using AWS CLI:**

If you prefer, you can also store your secrets in AWS Secrets Manager using the AWS CLI. This can be an alternative to storing secrets directly via Terraform:

```sh
aws secretsmanager create-secret --name mysql-cred --secret-string '{"db_username":"my_db_username","db_password":"my_db_password"}'
```

**4. Apply Terraform Configuration:**

Run your Terraform commands as usual. Terraform will retrieve the secret values from AWS Secrets Manager and use them to configure your resources:

```sh
terraform init
terraform plan
terraform apply
```

### Method 4: GitHub Secrets

For projects managed with GitHub, using GitHub Secrets is a convenient way to store

 and manage secrets securely within GitHub Actions workflows. This method is particularly useful for CI/CD pipelines where you need to keep sensitive data safe while automating deployments.

#### Step-by-Step Guide

Here’s how you can manage your database credentials using GitHub Secrets:

**1. Add Secrets to GitHub Repository:**

Navigate to your GitHub repository, go to **Settings > Secrets and variables > Actions**, and add your secrets. Use names like `DB_USERNAME` and `DB_PASSWORD`.

**2. Access Secrets in GitHub Actions Workflow:**

In your GitHub Actions workflow file (`.github/workflows/your-workflow.yml`), you can access these secrets as environment variables:

```yaml
name: Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: 1.3.6

    - name: Terraform Init
      run: terraform init

    - name: Terraform Apply
      env:
        TF_VAR_db_username: ${{ secrets.DB_USERNAME }}
        TF_VAR_db_password: ${{ secrets.DB_PASSWORD }}
      run: terraform apply -auto-approve
```

**3. Use Secrets in Terraform Configuration:**

Your Terraform configuration file remains unchanged, as it relies on the environment variables provided by GitHub Actions.

### Comparison of Methods

| **Method**              | **Pros**                                      | **Cons**                                       | **Use Case**                                |
|-------------------------|-----------------------------------------------|------------------------------------------------|---------------------------------------------|
| **Environment Variables** | Simple to set up and use.                    | Secrets are exposed in environment variables.  | Suitable for quick setups or local development. |
| **Encrypted Files (KMS)** | High security with encryption at rest.        | Requires additional steps for encryption/decryption. | Ideal for scenarios where KMS is already used. |
| **AWS Secrets Manager** | Secure storage with automatic rotation.       | Costs associated with Secrets Manager.         | Best for production environments needing dynamic secrets. |
| **GitHub Secrets**      | Convenient for CI/CD workflows.                | Limited to GitHub Actions.                     | Good for managing secrets in CI/CD pipelines. |

### Recommendations

- **Development Environments:** Environment variables or encrypted files (KMS) can be sufficient and are easier to set up.
- **Production Environments:** AWS Secrets Manager provides robust security features and is recommended for managing secrets in production.

By understanding and applying these methods, you can ensure that your sensitive information remains secure and your Terraform configurations are well-managed.
