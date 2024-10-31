---
title: "Infrastructure as Code with AWS CDK: A Success Story"
authorId: "mufaddal"
date: 2024-10-30
draft: false
featured: true
weight: 1
---

When it comes to writing infrastructure as code, selecting the appropriate tool is critical. In my experience, Terraform is frequently the first choice for Infrastructure as Code (IAC) projects. However, as time passes and new scenarios emerge, we may discover that Terraform isn't the best option after all.

This is exactly what happened in my case, prompting me to consider other options. That's when I discovered the AWS Cloud Development Kit (CDK), which was released in 2019 and perfectly matched my use case. But what makes the AWS CDK so unique? In this blog, we'll go over the specifics and explain why it's a good choice in certain situations.

## What is AWS CDK?

The AWS Cloud Development Kit (CDK) is an open-source software development framework that allows us to define and provision cloud infrastructure resources with a variety of programming languages.

AWS CDK, which is built on TypeScript, is tightly integrated with AWS CloudFormation, allowing it to leverage its strengths in infrastructure state management. In fact, CDK handles state management in the same way that CloudFormation does, making it easier to manage cloud resources.

## AWS CDK Key Concepts

To get the most out of AWS CDK, it's essential to understand three fundamental concepts: Apps, Stacks, and Constructs. These concepts are the foundation of CDK, and understanding them will help us decide when to use the tool and how to structure our infrastructure as code.

###  Apps (CDK Apps)

A CDK App represents the root of our infrastructure as code, an entry point of our program. It's a composite of all the required resources for our application. Think of it as the top-level container that holds everything together. An App can contain multiple Stacks, which we'll discuss next.

### Stacks (CloudFormation Stacks)

In CDK, a Stack is the unit of deployment. It represents a single cloudformation Stack, which is a collection of resources that are deployed together. A Stack is a root Construct that contains multiple Constructs, which represent the actual cloud components. An App can have multiple Stacks, each representing a separate deployment unit. Use Stacks to group resources that should be deployed and destroyed together.

### Constructs (Cloud Components)

A Construct represents a "cloud component" and encapsulates everything AWS CloudFormation needs to create or update a resource or a combination of resources. A Construct can have multiple resources that are coupled together, and a Stack can have multiple Constructs. Think of a Construct as a self-contained module that defines a specific piece of our infrastructure.

Here's a simple analogy to help illustrate these concepts:
* An App is like a city, which contains multiple neighborhoods (Stacks).
* A Stack is like a neighborhood, which contains multiple houses (Constructs) and other infrastructure (resources).
* A Construct is like a house, which is composed of multiple rooms (resources) and has its own architecture and configuration.

## Architecture Diagram

Here's a simple diagram to illustrate the relationships between these concepts:
![aws cdk concepts](/images/blog/infrastructure-as-code-with-aws-cdk/aws-cdk-concepts.png)

As we discussed about CDK, there is much more information available in the official CDK documentation. Coming back to the main point of the blog, why did I choose the CDK as the best option for my situation? So, what was the scenario?

## The Scenario: Deploying Applications with Isolation and Scale

Our use case involves deploying multiple applications on AWS ECS, with each application using RDS Postgres as its database. The twist was that we had to deploy these applications multiple times for different clients, with each client requiring database isolation. This meant that we needed a solution that could efficiently manage multiple deployments with minimal effort.

### The Requirements:
* Deploy applications on AWS ECS
* Use RDS Postgres as the database
* Ensure database isolation for each client
* Deploy the same application multiple times for different clients
* Minimize onboarding effort for each new client
* Manage multiple environments (lower and higher) with similar infrastructure components, but with configuration changes

### The Challenge:
To illustrate the challenge, let's consider an example. Suppose we have a bill generator service that needs to be deployed for multiple clients. The application code remains the same, but each client requires its own isolated database. We could either deploy the application on our own AWS infrastructure or on the client's AWS environment. However, this would require manual effort and configuration for each new client, which wasn't scalable.

### The Solution: AWS CDK to the Rescue

* Define our infrastructure as code, making it easy to manage and version-control
* Create a one-click solution for onboarding new clients, minimizing manual effort
* Manage multiple environments with similar infrastructure components, but with configuration changes
* Package our CI/CD pipeline, application deployment, configuration management, and container image management into a single CDK codebase

## Key Abilities of AWS CDK

1. **Sensible Defaults**: Reduces the number of code lines we need to write, making it easier to define infrastructure.
2. **Reusable Libraries**: Allows us to build reusable libraries, reducing the amount of copy-pasting and making it easier to manage complex infrastructure.
3. **Automated Rollback**: Automatically rolls back resource creation if it fails, ensuring that our infrastructure is always in a consistent state.
4. **Event Logging**: Shows the events of logs while resource creation, providing visibility into the deployment process.
5. **Single-Stack Deployment**: Useful for application and service deployments, CDK uses CloudFormation under the hood to deploy a single Stack, reducing conflicts and parallel deployments per environment.

## Important Considerations Before Choosing AWS CDK

1. **Provider Limitations**: We can't switch providers within the same application. This means that if we’re deploying our application to a single AWS account and region, we can't create resources in another region or account in the same run.
2. **No Cross-Account or Cross-Region Support**: Unlike Terraform, CDK doesn't support assuming roles or accessing resources from other accounts or regions.
3. **Unstable Development Stage**: Many CDK services are still in the unstable development stage, which means we can expect breaking changes with every update.
4. **Limited CDK Modules**: Some key AWS services still don't have CDK modules available. This may force us to use a hybrid approach, combining CDK with other tools.
5. **Incomplete Documentation and Examples**: CDK documentation and online resources are still limited, making it harder to find solutions to common problems.
6. **No Resource Replacement**: CDK doesn't support replacing resources with the same name. This can lead to conflicts and difficulties when updating resources.
7. **Stateful Resource Updates**: Updating stateful resources can be challenging, as it often requires recreating the resource, which involves destroying the existing one first.

## When to Choose CDK?
1. **Reusable infrastructure**: Bundle infrastructure and reuse across multiple environments with minimal configuration changes.
2. **Infrastructure and app code together**: Keep infrastructure and application code in one place and written in the same programming language.
3. **Multi-tenant deployments**: Easily create deployments for multiple clients with minimal effort.
4. **Alignment with programming best practices**: Leverage existing programming skills and knowledge to manage infrastructure.

## Recommendations

### Modeling with Constructs and Deploying with Stacks
A Stack is the unit of deployment, meaning that everything within it is deployed together.

**Example: Machine Learning Model**
A machine learning model can also be modeled as a Construct and deployed as a Stack. The Constructs that make up this model include an Amazon S3 bucket for storing training data, an Amazon SageMaker notebook instance for model development, and an Amazon SageMaker endpoint for model deployment. These Constructs can be composed into a single high-level Construct, such as MachineLearningModel. This Construct can then be instantiated in one or more tacks for deployment, depending on the environment (e.g., dev, prod, staging).

### Avoid Changing the Logical ID
The logical ID is a unique identifier generated by AWS CDK for each resource in our Stack. Changing the logical ID of a stateful resource can lead to unintended consequences, such as

* **Resource recreation**: If the logical ID changes, AWS CDK may recreate the resource, resulting in data loss or inconsistencies.
* **Resource conflicts**: Changing the logical ID can cause conflicts with existing resources, leading to errors or unexpected behavior.

### Use Generated Resource Names
It's recommended to use generated resource names instead of physical names defined while resource creation which can lead to several issues, including: Resource recreation, Resource conflicts, Tight coupling

## Conclusion
Our experience with AWS CDK, we were able to achieve true "infrastructure as code." Our CDK codebase became the single source of truth for our infrastructure, allowing us to manage and version-control our environments with ease. This approach also enabled us to automate our deployments, reduce manual errors, and improve our overall efficiency.