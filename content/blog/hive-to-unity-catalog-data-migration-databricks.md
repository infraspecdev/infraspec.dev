---
title: "Efficient Data Migration: From Hive Metastore to Unity Catalog in Databricks"
authorId: "arihant"
date: 2024-11-09
draft: false
featured: true
weight: 1
---

<img src="/images/blog/hive-to-unity-catalog-data-migration-databricks/cover.png" alt="Hive Metastore to Unity Catalog Data Migration in Databricks">

## **TL;DR**

We had to migrate extensive data from Hive Metastore to Unity Catalog in a regulated large-scale enterprise environment.
This task required precise planning, synchronization across teams, and expertise to ensure zero downtime and no data
loss. By removing outdated jobs, cutting costs, and streamlining data workflows, we optimized the data infrastructure
and achieved a robust governance framework. This migration gave us a deep understanding of complex data systems and the
nuances of managing dependencies, aligning stakeholders, and ensuring regulatory compliance.

## **Project Background: Migrating Enterprise-Scale Data**

We recently undertook the task to upgrade data management from Hive Metastore to Unity Catalog within Databricks.
The Hive Metastore system posed challenges in data governance, access control, and lineage tracking. Unity Catalog, with
its advanced security and governance features, was the natural choice to address these limitations and to meet our
standards for compliance and operational efficiency.

## **Initial Setup and Core Challenges**

### **Hive Metastore Constraints**

Existing reliance on Hive Metastore introduced numerous constraints:

- **Limited Security and Governance:** Lack of native auditing, inadequate access controls, and missing lineage tracking
  created compliance challenges.
- **Environment Restrictions:** Hive did not allow sharing schemas across separate environments, complicating the setup
  of development, staging, and production. Unity Catalog, by contrast, supports schema sharing across environments with
  detailed access controls, essential for regulated enterprises.

### **Migration Requirements**

With around **87 schemas** and **1,920-1,950** tables totaling **~22 TB** to migrate, our objective was clear: migrate
active data to Unity Catalog while maintaining zero downtime and safeguarding against data divergence. This meant not
only handling the transfer but also ensuring no production jobs were disrupted.

## **Strategy and Planning**

### **Assessing Existing Data and Stakeholder Engagement**

Our first steps included a thorough data assessment and stakeholder outreach. We leveraged the Databricks utility tools
to catalog and assess tables within the Hive Metastore. This enabled us to filter out obsolete tables and prioritize
essential data.

We collaborated with multiple stakeholders, from schema owners to data engineers, for input on which tables were
critical and required for daily operations. This information-gathering stage identified schemas for migration and
non-essential ones for removal, enhancing the organization's data efficiency.

## **Execution Phase**

### **Detailed Migration Workflow**

- **Schema and Table Identification:**  
  Using scripts, we generated a comprehensive list of schemas and tables, detailing table size, last update time, and
  owner feedback on necessity for migration. This streamlined our focus on only essential data, avoiding the migration
  of dead jobs and outdated test schemas.

  To gather this information efficiently, we reached out to schema owners for their inputs. Here's an example of a Slack
  message we sent to one of the Hive schema owners requesting the necessary details for the migration:

  <img src="/images/blog/hive-to-unity-catalog-data-migration-databricks/sample_slack_message.png" alt="Sample slack message requesting schema owners to update the hive schema details">

- **Scheduling and Timing:**  
  Migrating tables with read-only operations was straightforward, as both Hive and Unity Catalog could be accessed
  simultaneously. However, tables with active write operations presented a challenge. If a job continued to write to
  Hive after migration, the data in Hive and Unity Catalog would diverge, potentially requiring a re-migration—a costly
  and complex task given the volume of tables. To avoid this, we scheduled migrations during job downtime to ensure data
  consistency.

- **Automation and Scalability:**  
  We automated and streamlined a significant part of the migration process by identifying ideal times when jobs were
  inactive and initiating migrations with minimal manual intervention. Our scripts were versatile, handling different
  scenarios based on table types and data sizes, ensuring efficient transfers. This automated approach allowed us to
  manage both large and small datasets with ease, scaling resources as needed to maintain optimal performance.

**Note:** The jobs in this migration were primarily batch-oriented, which allowed us to perform migrations during
scheduled downtimes without impacting production workloads.

### **Data Consistency and Rollback Strategy**

To ensure data consistency and allow for a smooth rollback if needed, we followed these steps:

- **User Preparation:** Before migration, we shared the new Unity Catalog table paths with users and asked them to
  prepare GitHub pull requests (PRs) for updating their jobs to refer to Unity Catalog.
- **Migration Process:** Once the migration to Unity Catalog was successful, we merged the PRs, ensuring that jobs now
  referred to Unity Catalog tables.
- **Rollback Option:** If the migration had failed, active jobs would have continued referring to the Hive tables,
  ensuring no disruption or data loss.

## **Results and Key Improvements**

### **Enhanced Query Performance and Data Visibility**

Post-migration, we observed significant improvements in query performance due to more efficient data organization and
optimized access controls within Unity Catalog. Additionally, the enhanced visibility provided by Unity Catalog's
lineage tracking allowed us to easily identify upstream and downstream tables, as well as access audit history. This
improved visibility contributed to better management and faster troubleshooting of data workflows.

### **Data and Cost Efficiency Gains**

#### **Data Migration:**

Successfully transferred **~22 TB** to Unity Catalog, with **~75 TB** of deprecated data removed from Hive.

#### **Cost Savings:**

By removing 75 TB of deprecated data, we reduced both storage costs and data handling overheads. Here's a rough
breakdown of cost savings:

| **Cost Type**          | **Details**                                                      | **Annual Cost** |
|------------------------|------------------------------------------------------------------|-----------------|
| **EC2 Compute**        | 20 x i3.xlarge instances, 1 hour/day at $0.252/hour per instance | **$1,840.56**   |
| **Databricks Compute** | 20 instances, 1 hour/day at $0.55/DBU/hour per instance          | **$4,015**      |
| **Storage Cost**       | 75 TB of data stored on AWS S3 at $0.025/GB/month                | **$23,040**     |
| **Total Annual Cost**  | Sum of all costs                                                 | **$28,895.56**  |

**Note:** Additional costs are incurred for reading data from upstream sources like Redshift and writing to S3. These
read/write operations are not included in the above cost breakdown but contribute to the overall data processing costs.

### **Enhanced Governance and Operational Efficiency**

- **Improved Data Governance:** Unity Catalog introduced clear data lineage and granular access control, essential for
  maintaining regulatory compliance. Unity Catalog's centralized governance model also provided the ability to enforce
  consistent access controls across environments, significantly improving both security and compliance management.

- **Operational Efficiency:** Before the migration, engineers spent significant time maintaining outdated or unnecessary
  jobs. Considering ~10 unused jobs required about 1 hour per week to manage, removing those jobs saved approximately
  10 hours of engineering effort each week. This freed up valuable time for engineers to focus on core operational
  tasks, accelerating product delivery and reducing maintenance overheads.

### **Key Migration Metrics**

| **Total Schemas** | **Tables Migrated** | **Data Migrated** | **Data Deleted** | **Job Optimizations**    |
|-------------------|---------------------|-------------------|------------------|--------------------------|
| 87                | 1,920-1,950         | ~22 TB            | ~75 TB           | Significant cost savings |

## **Unseen Challenges: Key Insights We Gained During the Migration**

As with any large-scale project, there were a few unexpected challenges along the way. One critical lesson we learned
was the importance of removing migrated tables from Hive immediately after the successful migration. Initially, we
delayed this
step, which led to users continuing to write to the old tables in Hive, causing data divergence.

The takeaway? **Don't wait to delete migrated tables from Hive**—doing so ensures data consistency and streamlines the
transition to Unity Catalog. This small adjustment made a huge difference in the overall process.

## **Conclusion: Strategic Impact and Future Roadmap**

This large-scale migration for a regulated enterprise required meticulous planning and execution to ensure zero downtime
and maintain data integrity. Every piece of data and workload was critical to operations. Our top priority was
safeguarding production workloads and preventing any data loss. This careful approach required significant effort, but
it was crucial for ensuring operational continuity and preserving data accuracy. The migration optimized the governance
model, reduced costs, and enhanced operational focus.

Stay tuned for an upcoming series of blog posts where we'll dive deep into the technical processes and scripts used,
including enabling Unity Catalog for an existing production Databricks setup. 🚀
