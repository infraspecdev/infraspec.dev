---
title: "Getting Started with GitHub Runners"
authorId: "rahul"
date: 2024-04-25
draft: false
featured: true
weight: 1
---

# Introduction

In today's fast-paced world of software development, automation is key to staying competitive. GitHub, a leading platform for collaboration and version control, offers an extensive set of tools to automate Continuous Integration and Continuous Deployment (CI/CD) pipelines. At the heart of this automation are GitHub Runners, which execute CI/CD tasks to streamline the development process. Let's dive into the world of GitHub Runners and explore how they can enhance your projects.

# GitHub Runners: Your DevOps Assistants

GitHub Runners handle repetitive, time-consuming tasks, allowing you to focus on creating innovative software. By automating test runs, builds, and deployments, they streamline your workflow and boost productivity. These runners work seamlessly in the background to keep your projects on track and ensure smooth operations.

## GitHub-hosted Runners

Think of GitHub-hosted runners as the all-inclusive resorts of the CI/CD world. These virtual environments are provided by GitHub, pre-loaded with everything you need. Need a Linux machine to build your app? They've got it. How about a Windows environment for your .NET project? Check. With GitHub-hosted runners, you can hit the ground running without worrying about setting up infrastructure.

**No setup required!** Simply define your workflows in `.github/workflows`, and GitHub will take care of the rest. It's as easy as writing a recipe and letting GitHub do the cooking.

## Self-hosted Runners

If you prefer to take control of your setup and fine-tune your execution environment, self-hosted runners are a great option. These are machines you manage within your own infrastructure, giving you full control. They are perfect for projects with specific requirements or security constraints.

Self-hosted runners can connect directly with your internal network, enabling access to applications and services hosted within your office environment or on-premises servers. This direct interaction allows your workflows to access databases, APIs, and other internal resources securely, reducing reliance on external connections and ensuring your CI/CD processes have controlled, secure access to the resources they need for successful workflows.

### Setting Up self-hosted Runners

To set up self-hosted runners, follow these steps:

1. **Create a Folder:**
    ```bash
        $ mkdir actions-runner && cd actions-runner
    ```

2. **Download the Latest Runner Package:**
    - Visit the [GitHub Actions runner releases page](https://github.com/actions/runner/releases).
    - Download the appropriate runner package for your operating system (Linux, Windows, or macOS) and architecture (x64 or ARM).
    - Save the package to the `actions-runner` folder.

3. **Extract the Installer:**
    - For Linux and macOS, use the command:
        ```bash
            $ tar xzf actions-runner-{os}-{arch}-{version}.tar.gz
        ```

    - For Windows, use the command:
        ```bash
            $ tar -xzf actions-runner-{os}-{arch}-{version}.tar.gz
        ```

4. **Configure the Runner:**
    ```bash
        $ ./config.sh --url https://github.com/{username}/{repo} --token {token}
    ```
    - Run the configuration script for the runner, specifying your GitHub repository URL and the registration token provided by GitHub. Replace `{username}` and `{repo}` with your GitHub username and repository name, and replace `{token}` with your registration token.

5. **Run the Runner:**
    - For Linux and macOS, use the command:
        ```bash
            $ ./run.sh
        ```

    - For Windows, use the command:
        ```bash
            $ run.cmd
        ```

By following these steps and using the appropriate commands for your operating system, you can set up your self-hosted runner and use it in your GitHub Actions workflows.

# Setting Up GitHub Runners in CI/CD Workflow

Using GitHub-hosted runners requires no setup on your part. All you need to do is define your workflows in your `.github/workflows` directory, and GitHub will handle the execution of your workflows using hosted runners.

## Example YAML File

Here is an example YAML file demonstrating how to use both GitHub-hosted and self-hosted runners in a CI/CD workflow:

```yaml
    name: CI/CD Workflow
    
    on:
      push:
        branches:
          - main
    
    jobs:
      # Job using GitHub-hosted runners
      build_and_test:
        # Specify GitHub-hosted runner (in this case, Ubuntu)
        runs-on: ubuntu-latest
    
        steps:
          # Checkout the repository code
          - name: Checkout code
            uses: actions/checkout@v2
    
          # Install dependencies (example using npm, customize as needed)
          - name: Install dependencies
            run: npm install
    
          # Run tests (customize this step for your testing needs)
          - name: Run tests
            run: npm test
    
          # Build the project (customize as needed)
          - name: Build project
            run: npm run build
    
      # Job using self-hosted runners
      deploy:
        # Specify the job runs on a self-hosted runner
        runs-on: self-hosted
    
        # Specify the job will run after the previous job
        needs: build_and_test
    
        steps:
          # Checkout the repository code
          - name: Checkout code
            uses: actions/checkout@v2
    
          # Deploy the application (customize this step for your deployment method)
          - name: Deploy application
            run: |
              echo "Deploying application..."
              # Add your deployment commands here
    
          # Verify the deployment
          - name: Verify deployment
            run: |
              echo "Verifying deployment..."
              # Add your verification commands here
```

### Overview of the YAML File

- The file is set up to trigger on pushes to the `main` branch.
- The `build_and_test` job uses GitHub-hosted runners (`ubuntu-latest`) to check out the code, install dependencies, run tests, and build the project.
- The `deploy` job uses self-hosted runners (`self-hosted`) and specifies a dependency on the `build_and_test` job.
- In the `deploy` job, the workflow checks out the code and deploys the application using a custom deployment method, which you can tailor to your specific needs.

# Customizing GitHub Notifications for CI/CD Workflow Status Updates

GitHub automatically sends notifications about CI/CD workflow status updates to the individuals who triggered the workflow. However, GitHub offers the flexibility to customize notification settings at the repository level.

## How to Customize Notifications

1. **Access Notification Settings**:  
    Go to the settings of your GitHub repository and navigate to the "Notifications" section. This is where you can control how you receive updates about your repository.

2. **Choose Notification Preferences**:  
    Specify the types of events you want to be notified about, such as all workflow runs, specific events like failures, or only certain workflows. Customize your preferences to receive only the notifications you care about.

3. **Specify Recipients**:  
    Customize who receives notifications by specifying email addresses or choosing to receive notifications via GitHub itself. You can adjust these settings for individuals or teams, making it easy to keep the right people informed about your workflow status.

# Conclusion

GitHub Runners are the backbone of modern CI/CD pipelines, enabling developers to automate their workflows with ease and efficiency. Whether you opt for GitHub-hosted runners for convenience or self-hosted runners for control, GitHub provides the tools and infrastructure to support your automation needs.

By embracing GitHub Runners, you can unlock new levels of productivity and innovation, allowing your projects to reach their full potential. So, don't wait any longer! Dive into the world of GitHub Runners and elevate your CI/CD workflow today!