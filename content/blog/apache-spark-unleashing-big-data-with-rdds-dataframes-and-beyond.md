---
title: "Apache Spark: Unleashing Big Data with Rdds, DataFrames and Beyond."
authorId: "shivani"
date: 2024-11-24
draft: false
featured: true
weight: 1
---

Have you ever wondered how companies like Netflix recommend your favourite movies or how e-commerce platforms handle vast amounts of data to personalize your shopping experience 🤔?

Behind the scenes, these capabilities often rely on **Apache Spark**, a powerful distributed computing system designed for big data processing. Spark simplifies working with massive datasets by enabling fast and scalable data processing across clusters of computers.

Let’s dive into Spark to understand its core,

## Introduction

Apache Spark is a unified, multi-language (Python, Java, Scala, and R)computing engine for executing data engineering, data science, and machine learning on single-node machines or clusters and a set of libraries for parallel data processing.

Let’s break down our description:

`Unified`: It is designed to handle a wide range of data analytics tasks, from simple SQL queries to machine learning and streaming, all within a single engine using consistent APIs. This unified approach simplifies building complex applications and ensures high performance by optimizing different tasks.

`Computing Engine`: It focuses on computation rather than storage, allowing it to work with various storage systems like Hadoop, Amazon S3, and Apache Cassandra. This flexibility makes Spark suitable for diverse environments, including cloud and streaming applications.

`Libraries`: It provides a unified API for common data analysis tasks. It supports both standard libraries that ship with the engine as well as external libraries published as third-party packages by the open-source communities. The standard libraries includes libraries for SQL (Spark SQL), machine learning (MLlib), stream processing (Structured Streaming), and graph analytics (GraphX).

## Where to Run Spark ?

1. **Run Spark Locally**
    

* Install Java (required as Spark is written in Scala and runs on the JVM) and Python (if using the Python API).
    
* Visit [Spark's download page](http://spark.apache.org/downloads.html), choose "Pre-built for Hadoop 2.7 and later," and download the TAR file.
    
* Extract the TAR file and navigate to the directory.
    
* Launch consoles in the preferred language:
    
    * Python: `./bin/pyspark`
        
    * Scala: `./bin/spark-shell`
        
    * SQL: `./bin/spark-sql`
        

2. **Run Spark in the Cloud**
    

* No installation required; provides a web-based interactive notebook environment.
    
* **Option**: Use [Databricks Community Edition \[free\]](https://www.databricks.com/try-databricks#account)
    

3. **Building Spark from Source**
    

* **Source**: Download the source code from the [Apache Spark download page](http://spark.apache.org/downloads.html).
    
* **Instructions**: Follow the README file in the source package for building Spark.
    

## Spark Components

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1732356652608/fe1bec32-214f-4784-aab3-8c2d1798c01a.png align="center")

## High-Level Components (Spark Applications)

At a high level, Spark provides several libraries that extend its functionality and are used in specialized data processing tasks.

1. **SparkSQL**: SparkSQL allows users to run SQL queries on large datasets using Spark’s distributed infrastructure. Whether interacting with structured or semi-structured data, SparkSQL makes querying data easy, using either SQL syntax or the DataFrame API.
    
2. **MLlib**: It provides distributed algorithms for a variety of machine learning tasks such as classification, regression, clustering, recommendation systems, etc.
    
3. **GraphX**: GraphX is Spark’s API for graph-based computations. Whether you're working with social networks or recommendation systems, GraphX allows you to process and analyze graph data efficiently using distributed processing.
    
4. **Spark Streaming**: It enables the processing of live data streams from sources like Kafka, or TCP sockets, turning streaming data into real-time analytics.
    

## Spark Core

At the heart of all these specialized libraries is **Spark Core**. Spark Core is responsible for basic functionalities like task scheduling, memory management, fault tolerance, and interactions with storage systems.

### The Core of Spark: RDDs

**RDDs (Resilient Distributed Datasets)** are the fundamental building blocks of Spark Core. They represent an immutable, distributed collection of objects that can be processed in parallel across a cluster. More about RDDs is discussed later.

### DAG Scheduler and Task Scheduler

* **DAG Scheduler**: Spark breaks down complex workflows into smaller stages by creating a Directed Acyclic Graph (DAG). The DAG Scheduler optimizes this execution plan by determining which operations can be performed in parallel and orchestrating how the tasks should be executed.
    
* **Task Scheduler**: After the DAG is scheduled, the Task Scheduler assigns tasks to worker nodes in the cluster. It interacts with the Cluster Manager to distribute tasks across the available resources.
    

### Cluster Managers and Storage Systems

Apache Spark can run on multiple cluster managers like, Standalone which is Spark’s built-in resource manager for small to medium-sized clusters, Hadoop YARN (Yet another resource navigator), Apache Mesos, Kubernetes for orchestrating Spark workloads in containerized environments.

For data storage, Spark integrates with a variety of systems like HDFS (Hadoop Distributed File System), Amazon S3, Cassandra, HBase etc.

Spark's ability to interact with these diverse storage systems allows users to work with data wherever it resides.

## Spark’s Basic Architecture

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1732357077877/d3ac6b43-9b95-48ed-8720-8cedc9c6550b.png align="center")

### 1\. The Spark Driver

The Spark driver(process) is like the “brain” of your Spark application. It’s responsible for controlling everything. The driver makes decisions about what tasks to run, keeps track of the application’s progress, and talks to the cluster manager to get the computing power needed. Essentially, it manages the entire process and checks on the tasks being handled by worker nodes (executors). So basically it manages the lifecycle of the spark application.

### 2\. The Spark Executors

Executors(process)are the “workers” that actually do the processing. They take instructions from the driver, execute the tasks, and send back the results. Every Spark application gets its own set of executors, which run on different machines. They are responsible for completing the tasks, saving data, reporting results, and re-running any tasks that fail.

### 3\. The Cluster Manager

The cluster manager is like a “resource manager.” It manages the machines that make up your cluster and ensures that the Spark driver and executors have enough resources (like CPU and memory) to do their jobs. Spark can work with several types of cluster managers, such as YARN, Mesos, or Kubernetes, or it can use its built-in manager.

### 4\. Execution Modes

Spark can run in different ways, depending on how you want to set it up:

* **Cluster Mode**: In this mode, both the driver and executors run on the cluster. This is the most common way to run Spark in production.
    
* **Client Mode**: The driver runs on your local machine (the client) from where the spark application is submitted, but the executors run on the cluster. This is often used when you're testing or developing.
    
* **Local Mode**: Everything runs on a single machine. Spark uses multiple threads for parallel processing to simulate a cluster. This is useful for learning, testing, or development, but not for big production jobs.
    

## Spark’s Low-Level APIS

### RDDs (Resilient Distributed Datasets)

They are the fundamental building block of Spark's older API, introduced in the Spark 1.x series. While RDDs are still available in Spark 2.x and beyond, they are no longer the default API due to the introduction of higher-level abstractions like DataFrames and Datasets. However, every operation in Spark ultimately gets compiled down to RDDs, making it important to understand their basics. The Spark UI also displays job execution details in terms of RDDs, so having a working knowledge of them is essential for debugging and optimization.

An RDD represents a distributed collection of immutable records that can be processed in parallel across a cluster. Unlike DataFrames(High-Level API), where records are structured and organized into rows with known schemas, RDDs are more flexible. They allow developers to store and manipulate data in any format—whether Java, Scala, or Python objects. This flexibility gives you a lot of control but requires more manual effort compared to using higher-level APIs like DataFrames.

**Key properties of RDDS**

* **Fault Tolerance:** RDDs maintain a lineage graph that tracks the transformations applied to the data. If a partition is lost due to a node failure, Spark can recompute that partition by reapplying the transformations from the original dataset.
    
* **In-Memory Computation:** RDDs are designed for in-memory computation, which allows Spark to process data much faster than traditional disk-based systems. By keeping data in memory, Spark minimizes disk I/O and reduces latency.
    

**Creating RDDs**

Now that we discussed some key RDD properties, let’s begin applying them so that you can better understand how to use them.

One of the easiest ways to get RDDs is from an existing DataFrame or Dataset. Converting these to an RDD is simple: just use the `rdd` method on any of these data types for example in Python, It only supports DataFrame and not Datasets, other languages like Scala, and Java support both DataFrame and Datasets.

```python
from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("DataFrame to RDD Example") \
    .getOrCreate()
# Create a DataFrame using a range of numbers
df = spark.range(10)
# Convert the DataFrame to an RDD
rdd = df.rdd
# Collect the RDD data 
rdd_data = rdd.collect()
```

## Sparks’s Structured APIS

### DataFrame

The Spark DataFrame is one of the most widely used APIs in Spark, offering a high-level abstraction for structured data processing.

It is a powerful Structured API that represents data in a tabular format, similar to a spreadsheet, with named columns defined by a schema. Unlike a traditional spreadsheet, which exists on a single machine, a Spark DataFrame can be distributed across thousands of computers. This distribution is essential for handling large datasets that cannot fit on one machine or for speeding up computations.

While the DataFrame concept is not unique to Spark; R and Python also includes DataFrames—these are typically limited to a single machine's resources. Fortunately, Spark’s language interfaces allow for easy conversion of Pandas DataFrames in Python and R DataFrames to Spark DataFrames, enabling users to leverage distributed computing for enhanced performance.

Below is a comparison of distributed versus single-machine analysis.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1732358269819/a38be331-b107-4065-bdda-ab40b0bcbff9.png align="center")

> Note: Spark also provides the Dataset API, which combines the benefits of RDDs and DataFrames by offering both compile-time type safety and query optimization. However, the Dataset API is only supported in Scala and Java, not in Python.
## Partitions

Spark breaks up data into chunks called partitions, allowing executors to work in parallel. A partition is a collection of rows that reside on a single machine in the cluster. By default, partitions are sized at 128 MB, though this can be adjusted. The number of partitions affects parallelism—fewer partitions can limit performance, even with many executors, and vice versa.

## Transformations

In Spark DataFrames, partitions are usually not managed directly. Instead, high-level transformations are defined, and Spark handles the execution details. Lower-level APIs like RDDs are available for more granular control.

In Spark, the core data structures are immutable, meaning once they’re created, they cannot be changed. This may seem odd at first, but you modify a DataFrame by instructing Spark on how you want to transform it. These instructions are called **transformations**.

For example, to filter out even numbers from a dataframe, you would use:

```python
divisBy2 = myRange.where("number % 2 = 0") # myRange is a dataframe
```

This code performs a transformation but produces no immediate output. That’s because they are **lazy**, meaning they do not execute immediately; instead, Spark builds a Directed Acyclic Graph (DAG) of transformations that will be executed only when an **action** is triggered. Transformations are the heart of Spark’s business logic and can be of two types: narrow and wide.

### Narrow Transformations

In a **narrow transformation**, each partition of the parent RDD/DataFrame contributes to only one partition of the child RDD/DataFrame. Data does not move across partitions, so the operation is **local** to the same worker node. These are efficient because they avoid **shuffling** (data transfer between nodes).

Examples: `map` `filter`

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1732344376978/13ba890a-95c4-4f21-b35f-ac19570daff1.png align="center")

### Wide Transformations

In a **wide transformation**, data from multiple parent RDD/DataFrame partitions must be shuffled (redistributed) to form new partitions. These operations involve **network communication**, making them more expensive.

Examples: `groupByKey` `reduceByKey` `join`

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1732348673655/115212c0-c124-47fa-8c5b-de1f659c0866.png align="center")

## Actions

They are operations that trigger the execution of transformations and return results to the driver program. Actions are the point where Spark evaluates the lazy transformations applied to an RDD, DataFrame, or Dataset.

Examples: `collect` `count`

When an action is invoked, Spark builds a **DAG (Directed Acyclic Graph)** of all preceding transformations and executes the optimized plan.

Key Differences Between Transformations and Actions

|  | **Transformations** | **Actions** |
| --- | --- | --- |
| **Execution** | Lazy (no immediate execution) | Eager (triggers computation) |
| **Output** | New RDD/DataFrame | Result or persisted output |
| **Examples** | `map`, `filter`, `groupBy` | `collect`, `count`, `take` |
| **Purpose** | Defines the computation logic | Finalizes and executes the logic |

Thanks for reading this blog! We’ve covered an overview of Spark’s components and architecture. In the next blog, we’ll explore its functionality in depth and understand how it handles large-scale data processing efficiently. Stay tuned!
