---
title: "Essential AWS Tagging Strategies for Better Cloud Control"
authorId: "rohit"
date: 2024-07-29
draft: false
featured: true
weight: 1
---

## Introduction

Managing cloud resources efficiently in AWS requires a robust tagging strategy. Tags are key-value pairs attached to resources, providing crucial metadata for resource management, cost allocation, security, and automation. This blog will guide you through defining mandatory and discretionary tags and establishing detection and enforcement mechanisms to ensure compliance across your AWS environment.

## The Problem: Untracked Resources and Rising Costs

At Infraspec, we started noticing some major issues with how we were managing our AWS resources. We had several AWS accounts in use, but no tagging standards were enforced. This meant that anyone could create resources, and sometimes, these resources were left running long after they were needed. 

As a result, our cloud costs were steadily increasing each month, and we had no clear way to track who was responsible for which resources. Without any tags, it was impossible to tie costs back to specific teams or projects, leaving us in the dark about where our budget was really going. This lack of accountability was causing both operational and financial headaches.

## Our Approach: Structuring AWS Accounts and Enforcing a Tagging Policy

Realizing that we needed a way to get things under control, we started exploring how AWS tags could help. By enforcing a tagging policy across all our AWS accounts, we could ensure that every resource was labeled with essential information like the owner, team, and environment.

But we didn’t stop there. To make sure everyone followed the rules, we implemented Service Control Policies (SCPs) that would block the creation of any resources that didn’t have the necessary tags. This added a layer of enforcement that gave us confidence that our tagging strategy would actually be used.

<p align="center">
  <img src="/images/blog/tag-strat-aws/aws-organization.png" alt="AWS Organization">
</p>

### Step 1: Organizing Accounts

Our first step was to create an AWS Organizations structure that mirrored our operational needs. We separated our accounts into two main Organizational Units (OUs): `Infraspec OU` and `Core OU`. The `Infraspec OU` contains all the accounts related to our primary operations, including `Dev`, `Staging`, and `Prod`. The `Core OU` contains our `Core Account`, which handles shared services such as networking and also handles policy management instead of root account.

This structure allowed us to clearly distinguish between different environments and core services, making it easier to enforce policies and manage resources.

### Step 2: Implementing Tagging Policy

With our accounts organized, we moved on to enforce a tagging policy across all our AWS accounts. We established a set of mandatory tags that would be required for specific resource, ensuring that resources were labeled with essential information like the owner, management of the rescource etc.

To ensure compliance, we implemented Service Control Policies (SCPs) that blocked the creation of any resources without the necessary tags. This enforcement layer gave us the confidence that our tagging strategy would be consistently applied across all environments.

We defined the following tags as mandatory across our AWS environment and implemented them using AWS Organizations Tag Policies. Below is an example of how these tags were structured and enforced:

```json
{
  "tags": {
    "Owner": {
      "tag_key": {
        "@@assign": "Owner"
      },
      "enforced_for": {
        "@@assign": [
          "ec2:instance",
          "ec2:vpc",
          "ec2:subnet",
          "ec2:natgateway",
          "ec2:security-group",
          "ec2:route-table",
          "ec2:internet-gateway"
        ]
      }
    },
    "ManagedBy": {
      "tag_key": {
        "@@assign": "ManagedBy"
      },
      "tag_value": {
        "@@assign": [
          "Terraform",
          "Manual"
        ]
      },
      "enforced_for": {
        "@@assign": [
          "ec2:instance",
          "ec2:vpc",
          "ec2:subnet",
          "ec2:natgateway",
          "ec2:security-group",
          "ec2:route-table",
          "ec2:internet-gateway"
        ]
      }
    }
  }
}
```

### Step 2: Implementing Service Control Policy

We created SCPs in AWS Organizations to prevent the creation of resources without mandatory tags. For example, the following SCP blocks the creation of EC2 instances and other resources if the `Owner` and `ManagedBy` tag is missing:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyEC2CreationWithNoOwnerTag",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "ec2:CreateVpc",
        "ec2:CreateSubnet",
        "ec2:CreateNatGateway",
        "ec2:CreateSecurityGroup",
        "ec2:CreateRouteTable",
        "ec2:CreateInternetGateway"
      ],
      "Resource": [
        "arn:aws:ec2:*:*:vpc/*",
        "arn:aws:ec2:*:*:subnet/*",
        "arn:aws:ec2:*:*:natgateway/*",
        "arn:aws:ec2:*:*:security-group/*",
        "arn:aws:ec2:*:*:route-table/*",
        "arn:aws:ec2:*:*:internet-gateway/*",
        "arn:aws:ec2:*:*:instance/*"
      ],
      "Condition": {
        "Null": {
          "aws:RequestTag/Owner": "true"
        }
      }
    },
    {
      "Sid": "DenyEC2CreationWithNoManagedByTag",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "ec2:CreateVpc",
        "ec2:CreateSubnet",
        "ec2:CreateNatGateway",
        "ec2:CreateSecurityGroup",
        "ec2:CreateRouteTable",
        "ec2:CreateInternetGateway"
      ],
      "Resource": [
        "arn:aws:ec2:*:*:vpc/*",
        "arn:aws:ec2:*:*:subnet/*",
        "arn:aws:ec2:*:*:natgateway/*",
        "arn:aws:ec2:*:*:security-group/*",
        "arn:aws:ec2:*:*:route-table/*",
        "arn:aws:ec2:*:*:internet-gateway/*",
        "arn:aws:ec2:*:*:instance/*"
      ],
      "Condition": {
        "Null": {
          "aws:RequestTag/ManagedBy": "true"
        }
      }
    }
  ]
}
```
### Step 3: Attaching the Service Control Policy and Tag Policy

After defining the policies, the next crucial step is to attach them to the appropriate Organizational Units (OUs) within AWS Organizations. By attaching both the Service Control Policy (SCP) and Tag Policy to the `Infraspec OU`, you ensure that all accounts under this OU enforce the mandatory tagging policy.

#### Attaching the Service Control Policy (SCP) to an OU

- **Navigate to the SCP Policy Section:**
  - Sign in to the AWS Management Console and go to the AWS Organizations console at [https://console.aws.amazon.com/organizations](https://console.aws.amazon.com/organizations).

- **Attach the SCP:**
  - Go to the `Service control policies` tab and click `Create policy` to define your SCP.
  - After creating the policy, click on `Targets` to attach it to the desired OU.

#### Attaching the Tag Policy to an OU

- **Navigate to the Tag Policy Section:**
  - Sign in to the AWS Management Console and go to the AWS Organizations console at [https://console.aws.amazon.com/organizations](https://console.aws.amazon.com/organizations).

- **Attach the Tag Policy:**
  - Go to the `Tag policies` tab and click `Create policy` to define your Tag Policy.
  - After creating the policy, click on `Targets` to attach it to the desired OU.

## Handling Existing Resources Without Tags

Addressing the challenge of existing resources that were created before implementing the tagging policy was crucial. To bring these resources into compliance without causing any unexpected downtime, we followed a structured approach:

- **Tagging Existing Resources**: 
   We utilized the AWS Tag Editor to identify all untagged resources. This tool enabled us to efficiently apply the necessary tags to multiple resources across various regions and accounts, ensuring consistency and compliance.

## Testing the Policy

After implementing the tagging and scp policies, we conducted rigorous testing to ensure compliance across our EC2 resources. We deployed several EC2 instances with and without the mandatory tags to verify the enforcement mechanisms.

- **Success Case**: When an EC2 instance was launched with all mandatory tags (`Owner`, `ManagedBy`), the instance creation proceeded without any issues.
  
- **Failure Case**: When an attempt was made to launch an EC2 instance without the `ManagedBy` tag, the operation was denied, demonstrating the effectiveness of our SCP in enforcing tag compliance.

## The Impact of Tags in Our Organization

### Resource Identification and Ownership

- **Owner Tag**: By tagging each resource with an `Owner`, we could quickly identify who was responsible for any given resource. This became critical when tracking down resources that were running unexpectedly or were no longer needed. The `Owner` tag provided clear accountability, making it easier to manage and decommission resources no longer in use.

### Operational Efficiency and Automation

- **ManagedBy Tag**: The `ManagedBy` tag helped us distinguish between resources managed by Terraform and those managed manually. This was particularly useful for automating resource management and ensuring that Terraform-managed resources were consistent with our infrastructure-as-code policies.

## Tag Naming and Usage Conventions

To ensure consistency and avoid conflicts, adhere to the following conventions:

1. **Tag Limits**: Each resource can have a maximum of 50 tags.
2. **Unique Tags**: Each tag key must be unique per resource, and each tag key can have only one value.
3. **Length Limits**: The maximum tag key length is 128 Unicode characters in UTF-8. The maximum tag value length is 256 Unicode characters in UTF-8.
4. **Allowed Characters**: Allowed characters are letters, numbers, spaces representable in UTF-8, and the following characters: `. : + = @ _ / -` (hyphen). Amazon EC2 resources allow any characters.
5. **Case Sensitivity**: Tag keys and values are case sensitive. Decide on a strategy for capitalizing tags and consistently implement that strategy across all resource types. For example, decide whether to use `Costcenter`, `costcenter`, or `CostCenter`, and use the same convention for all tags.
6. **AWS Prefix**: The `aws:` prefix is prohibited for tags; it's reserved for AWS use. You can't edit or delete tag keys or values with this prefix. Tags with this prefix do not count against your tags per resource quota.

## Best Practices for Tagging

1. **Consistency**: Use a standardized format for tags to avoid discrepancies. Decide on conventions for capitalization and delimiters and stick to them.
2. **Automation**: Automate tagging to reduce manual errors and ensure compliance.
3. **Documentation**: Maintain comprehensive documentation of your tagging strategy and dictionary for reference.
4. **Stakeholder Involvement**: Involve all relevant stakeholders in defining and reviewing the tagging strategy to ensure it meets organizational needs.

## Conclusion

A well-defined tagging strategy is essential for effective cloud resource management. By distinguishing between mandatory and discretionary tags and implementing robust enforcement mechanisms, you can achieve better visibility, cost control, and security in your AWS environment. Start by establishing a clear tagging dictionary and ensure compliance through automation and regular audits.

## Additional Resources

For further reading and deeper insights into AWS tagging strategies, consider the following resources:

- [**AWS Tagging Best Practices and Strategies**](https://docs.aws.amazon.com/tag-editor/latest/userguide/best-practices-and-strats.html) – Comprehensive guide on best practices and strategies for tagging in AWS.

- [**AWS Organizations Tag Policies**](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_tag-policies.html) – Details on implementing and managing tag policies across accounts.

- [**AWS Service Control Policies**](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scp.html) – Guide on using SCPs to enforce tagging standards.
