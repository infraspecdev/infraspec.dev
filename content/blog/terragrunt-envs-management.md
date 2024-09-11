---
title: "From Chaos to Clarity: Managing Environments with Terragrunt"
authorId: "nimisha"
date: 2024-09-10
draft: true
featured: true
weight: 1
---

Managing multiple environments was a never-ending headache for me. Like many others in the DevOps world, I was responsible for deploying applications across various environments—production, staging, and development. Each of these environments required the same infrastructure, but I found myself writing the same Terraform code over and over again in different folders. The repetition felt inefficient, and the potential for human error only grew with each tweak I had to make for a specific environment.

## The Repetition Trap

At first, my solution was simple: copy-paste. I created three separate folders: one for production, one for staging, and one for development. In each folder, I had the same Terraform files with minor tweaks like different variables or configurations for each environment. It worked, but I soon found myself dealing with the chaos of managing three sets of nearly identical infrastructure code.

Let’s say I needed to update a configuration for my database service. This meant that I had to open each folder, make the same change in three different places, and run Terraform multiple times for each environment. It was a tedious and error-prone process, and as my infrastructure grew, so did the complexity. I knew there had to be a better way.

> My Initial Setup was like this

```text
.
├── production
│   ├── app.tf
│   ├── database.tf
│   └── redis.tf
├── qa
│   ├── app.tf
│   ├── database.tf
│   └── redis.tf
└── staging
    ├── app.tf
    ├── database.tf
    └── redis.tf
```

The terraform files are contains same resources in different environment but the only difference was the values of the variables.
That is lot of Repeated Code.

## The Terragrunt Revelation

That’s when I discovered Terragrunt. Terragrunt is a thin wrapper for Terraform that provides extra tools for keeping your Terraform code DRY (Don’t Repeat Yourself). It allows you to manage multiple Terraform modules in a single repository and reuse code across different environments. Terragrunt’s ability to manage remote state, generate configurations, and apply configurations across multiple environments made it the perfect solution for my environment management woes.

How we reduce the repeated code using Terragrunt:
First step was to make a module of the resources with all the changeable variables exposed, Next was to use them in each environment.

> The new setup with Terragrunt

```text
.
├── terragrunt.hcl
├── production
│   ├── app
│   │   └── terragrunt.hcl
│   ├── database
│   │   └── terragrunt.hcl
│   └── redis
│       └── terragrunt.hcl
├── staging
│   ├── app
│   │   └── terragrunt.hcl
│   ├── database
│   │   └── terragrunt.hcl
│   └── redis
│       └── terragrunt.hcl
└── qa
    ├── app
    │   └── terragrunt.hcl
    ├── database
    │   └── terragrunt.hcl
    └── redis
        └── terragrunt.hcl
```

In the `terragrunt.hcl` file, we define the module to use and the
variables to pass to the module.

```hcl
# terragrunt.hcl
terraform {
  source = "gittfr:///exampleorg/app/aws?version=5.8.1"
}
inputs = {
  app_name = "my-app"
  environment = "production"
}
```

Similarly in the other terragrunt files we define the module to use and the variables to pass to the module.
and now for the storing the state file we can use the remote state file.

```hcl
# terragrunt.hcl
generate "backend" {
  path      = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "my-lock-table"
  }
}
EOF
}
```

This tells terragrunt to create a new file `backend.tf` with the contents of the `contents` block, Even if backend.tf already exists it will overwrite the contents because we have specified `overwrite_terragrunt`.
This is like a defining a function, Now we need to call it in the files i.e `terragrunt.hcl` files.

> This would look like this

```hcl
include "root" {
  path = find_in_parent_folders()
}
```

here the `find_in_parent_folders` returns the absolute path to the first `terragrunt.hcl` file it finds in the parent folders above the current `terragrunt.hcl` file.
and the include block tells terragrunt to include all the cofigurations from the file with the path returned by the `find_in_parent_folders` function.

## The Terragrunt Workflow

Here is a high-level overview of the terragrunt workflow:

> We run the command `terragrunt run-all plan` in the root directory.

This will run the terragrunt plan in each sub directory it finds, Then it reads the `terragrunt.hcl` file in the current directory and does the following:

1. Terragrunt reads the `terraform` block and downloads the specified Terraform module
2. Terragrunt reads the `inputs` block and passes the variables to the Terraform module
3. Terragrunt reads the `generate` block and creates the `backend.tf` file
4. Terragrunt runs Terraform with the specified configurations
5. Terragrunt stores the Terraform state in the remote state file
6. Terragrunt returns the output of the Terraform run

This workflow allows me to manage multiple environments with ease. I can make changes to my infrastructure code in a single place and apply those changes across all environments with a single command. Terragrunt’s ability to keep my Terraform code DRY has saved me time and effort, and I no longer have to worry about managing multiple sets of nearly identical infrastructure code.

## How Terragrunt worked for me

1. Centralized Modules: I now have a shared repository of modules that are environment-agnostic. The modules are reusable and cover things like VPCs, ECS clusters, RDS instances, and IAM roles. I no longer need to maintain three different sets of Terraform code.

2. Per-Environment Configurations: For each environment, I have a terragrunt.hcl file that passes environment-specific configurations like the number of instances or database types. These configurations override default values in the shared modules, ensuring that each environment gets what it needs without redundant code.

3. Automated Initialization: Running Terraform in multiple environments is now a breeze. Terragrunt automatically handles running terraform init, terraform plan, and terraform apply for each environment. No more manually navigating into each folder and executing commands multiple times. Terragrunt takes care of initializing each environment’s backend configuration (e.g., for state storage in S3 and locking with DynamoDB).

4. Dependency Management: Another Terragrunt superpower is managing dependencies between infrastructure components. For example, my ECS service depends on the VPC and subnets being provisioned first. Terragrunt’s dependencies block ensures that I deploy resources in the correct order, so my ECS service doesn’t attempt to launch before the network is ready.

## Final Thoughts

Terragrunt isn’t just about making Terraform easier to use. It’s about enabling you to manage infrastructure at scale without the chaos. I no longer have to worry about accidentally mismatching configurations between environments or spending hours applying changes manually.

If you’re tired of duplicating Terraform code across environments, I highly recommend giving Terragrunt a try. It’s been a game-changer in my workflow, and it just might bring the clarity you need in your infrastructure management journey.