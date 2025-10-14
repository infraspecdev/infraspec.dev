---
title: "From Chaos to Clarity: Managing Environments with Terragrunt"
authorIds: ["nimisha"]
date: 2024-09-10
draft: false
featured: true
weight: 1
---

Managing multiple environments was a never-ending headache for me. Like many others in the DevOps world, I was responsible for deploying applications across various environments—production, staging, and development. Each of these environments required the same infrastructure, but I found myself writing the same Terraform code over and over again in different folders. The repetition felt inefficient, and the potential for human error only grew with each tweak I had to make for a specific environment.

## The Repetition Trap

At first, my solution was simple: copy-paste. I created three separate folders: one for production, one for staging, and one for development. Each folder contained the same Terraform files with minor tweaks, such as different variables or configurations for each environment. It worked, but I soon found myself dealing with the chaos of managing three sets of nearly identical infrastructure code.

Let’s say I needed to update a configuration for my database service. This meant opening each folder, making the same change in three different places, and running Terraform multiple times for each environment. It was a tedious and error-prone process, and as my infrastructure grew, so did the complexity. I knew there had to be a better way.

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

The Terraform files contain identical resources across different environments, with the only variation being the values assigned to the variables.
That is lot of repeated code.

## The Terragrunt Revelation

That’s when I discovered Terragrunt. Terragrunt is a thin wrapper for Terraform that provides extra tools for keeping your Terraform code DRY (Don’t Repeat Yourself). It allows you to manage multiple Terraform modules in a single repository and reuse code across different environments. Terragrunt’s ability to manage remote state, generate configurations, and apply configurations across multiple environments made it the perfect solution for my environment management woes.

How we reduce the repeated code using Terragrunt:

First step was to make a module of the resources with all the changeable variables exposed, Next was to use them in each environment.

> The new folder structure using Terragrunt

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

In the `terragrunt.hcl` file, we define the module to use and the variables to pass to the module.

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

Similarly, in the other terragrunt files, we define the module to use and the variables to pass to the module.
And now for the storing the state file we can use the remote state file.

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

This tells terragrunt to create a new file `backend.tf` with the contents of the `contents` block, Even if backend.tf already exists it will overwrite the contents because we have specified `overwrite_terragrunt`. This is like a defining a function, Now we need to call it in the files i.e `terragrunt.hcl` files.

> This would look like this

```hcl
include "root" {
  path = find_in_parent_folders()
}
```

Here the `find_in_parent_folders` returns the absolute path to the first `terragrunt.hcl` file it finds in the parent folders above the current `terragrunt.hcl` file.
and the include block tells terragrunt to include all the cofigurations from the file with the path returned by the `find_in_parent_folders` function.

## The Terragrunt Workflow

Here is a high-level overview of the terragrunt workflow:

> We run the command `terragrunt run-all plan` in the root directory.

Output

```bash
22:03:23.710 INFO   The stack at . will be processed in the following order for command plan:
Group 1
- Module .
- Module ./production/app
- Module ./production/database
- Module ./production/redis
- Module ./qa/app
- Module ./qa/database
- Module ./qa/redis
- Module ./staging/app
- Module ./staging/database
- Module ./staging/redis
```

This will run the terragrunt plan in each sub directory it finds, Then it reads the `terragrunt.hcl` file in the current directory and does the following:

1. Terragrunt reads the `terraform` block and downloads the specified Terraform module
2. Terragrunt reads the `inputs` block and passes the variables to the Terraform module
3. Terragrunt reads the `generate` block and creates the `backend.tf` file
4. Terragrunt runs Terraform with the specified configurations
5. Terragrunt stores the Terraform state in the remote state file
6. Terragrunt returns the output of the Terraform run

This workflow allows me to manage multiple environments with ease. I am able to make changes to my infrastructure code in one place and then apply those changes across all environments with just one command. Terragrunt's capability to keep my Terraform code DRY has saved me time and effort, eliminating the need to manage multiple sets of nearly identical infrastructure code.

## How Terragrunt worked for me

1. **Centralized Modules**: I now have a shared repository of modules that are environment-agnostic. The modules are reusable and cover things like VPCs, ECS clusters, RDS instances, and IAM roles. I no longer need to maintain three different sets of Terraform code.

2. **Per-Environment Configurations**: For each environment, I have a terragrunt.hcl file that passes environment-specific configurations like the number of instances or database types. These configurations override default values in the shared modules, ensuring that each environment gets what it needs without redundant code.

3. **Automated Initialization**: Running Terraform in multiple environments is now a breeze. Terragrunt automatically handles running terraform init, terraform plan, and terraform apply for each environment. No more manually navigating into each folder and executing commands multiple times. Terragrunt takes care of initializing each environment’s backend configuration (e.g., for state storage in S3 and locking with DynamoDB).

4. **Dependency Management**: Another Terragrunt superpower is managing dependencies between infrastructure components. For example, my ECS service depends on the VPC and subnets being provisioned first. Terragrunt’s dependencies block ensures that I deploy resources in the correct order, so my ECS service doesn’t attempt to launch before the network is ready.

## Obvious Question: Why to use terragrunt instead of directly using terraform modules or terraform workspaces?

While terraform workspaces can be used for multiple environments , [hashicorp does not recommend it](https://developer.hashicorp.com/terraform/cli/workspaces)

> CLI workspaces within a working directory use the same backend, so they are not a suitable isolation mechanism for this scenario.

Even with Terraform modules, you can simply pass the variable and use it. However, this adds more boilerplate, making it more complex to maintain in the long run. I'm not suggesting that you should use Terragrunt; I'm just pointing out the facts. Ultimately, the decision depends on the type of project you are working on.

## Wrapping Up

Terragrunt goes beyond just making Terraform easier, it’s about scaling your infrastructure management without much hassle. It keeps your configurations DRY, handles dependencies, and automates workflows, so you don’t have to worry about misconfigurations or tedious manual updates. If you’re frustrated with managing repetitive Terraform code across multiple environments, Terragrunt might just be the tool that simplifies your workflow and brings order to your infrastructure management. Give it a try; it’s been a game-changer for me, and it could be for you too.
