---
title: "ClickHouse Deployment and Performance Benchmarking on ECS"
authorId: "rohit"
date: 2024-10-21
draft: false
featured: true
weight: 1
---

"Imagine being a Formula One driver, racing at breakneck speeds, but without any telemetry data to guide you. It’s a thrilling ride, but one wrong turn or overheating engine could lead to disaster. Just like a pit crew relies on performance metrics to optimize the car's speed and handling, we utilize observability in ClickHouse to monitor our data system's health. These metrics provide crucial insights, allowing us to identify bottlenecks, prevent outages, and fine-tune performance, ensuring our data engine runs as smoothly and efficiently as a championship-winning race car."

<p align="center">
  <img width="480" height="600" src="/images/blog/clickhouse-benchmarking/clickhouse-storage.jpeg" alt="Clickhouse Storage">
</p>

In this blog, we'll dive into the process of deploying ClickHouse on AWS Elastic Container Service (ECS). We’ll also look at performance benchmarking to evaluate ClickHouse as a high-performance log storage backend. Our focus will be on its ingestion rates, query performance, scalability, and resource utilization.

## Architecture: Replication for Fault Tolerance

In this architecture, we utilize five servers to ensure data availability and reliability. Two of these servers are dedicated to hosting copies of the data, while the remaining three serve to coordinate the replication process. We will create a database and a table using the **ReplicatedMergeTree** engine, which allows for seamless data replication across the two data nodes.

### Key Terms

- **Replica:** In ClickHouse, a replica refers to a copy of your data. There is always at least one copy (the original), and adding a second replica enhances fault tolerance. This ensures that if one copy fails, the other remains accessible.

- **Shard:** A shard is a subset of your data. If you do not split the data across multiple servers, all data resides in a single shard. Sharding helps distribute the load when a single server's capacity is exceeded. The destination server for the data is determined by a sharding key, which can be random or derived from a hash function. In our examples, we will use a random key for simplicity.

This architecture not only protects your data but also allows for better handling of increased loads, making it a robust solution for data management in ClickHouse. For more detailed information, refer to the official documentation on [ClickHouse Replication Architecture](https://clickhouse.com/docs/en/architecture/replication).

## Configuration Changes for ClickHouse Deployment

### Node Descriptions

- **clickhouse-01**: Data node for storing data.
- **clickhouse-02**: Another data node for data storage.
- **clickhouse-keeper-01**: Responsible for distributed coordination.
- **clickhouse-keeper-02**: Responsible for distributed coordination.
- **clickhouse-keeper-03**: Responsible for distributed coordination.

### Installation Steps

- **ClickHouse Server**: We deployed ClickHouse Server and Client on the data nodes, clickhouse-01 and clickhouse-02, using Docker images, specifically `clickhouse/clickhouse-server` for installation.

- **ClickHouse Keeper**: Installed on the three servers (clickhouse-keeper-01, clickhouse-keeper-02, and clickhouse-keeper-03) using Docker image `clickhouse/clickhouse-keeper`.

### Configuration Files and Best Practices

#### General Configuration Guidelines

- Add configuration files to `/etc/clickhouse-server/config.d/`.
- Add user configuration files to `/etc/clickhouse-server/users.d/`.
- Keep the original `/etc/clickhouse-server/config.xml` and `/etc/clickhouse-server/users.xml` files unchanged.

#### clickhouse-01 Configuration

The configuration for clickhouse-01 includes five files for clarity, although they can be combined if desired. Here are key elements:

- **Network and Logging Configuration**:
  - Sets the display name to "cluster_1S_2R node 1."
  - Configures ports for HTTP (8123) and TCP (9000).
  
```xml
<clickhouse>
    <logger>
        <level>debug</level>
        <log>/var/log/clickhouse-server/clickhouse-server.log</log>
        <errorlog>/var/log/clickhouse-server/clickhouse-server.err.log</errorlog>
        <size>1000M</size>
        <count>3</count>
    </logger>
    <display_name>cluster_1S_2R node 1</display_name>
    <listen_host>0.0.0.0</listen_host>
    <http_port>8123</http_port>
    <tcp_port>9000</tcp_port>
</clickhouse>
```

- **Macros Configuration**:
  - Simplifies DDL by using macros for shard and replica numbers.
  
```xml
<clickhouse>
    <macros>
        <shard>01</shard>
        <replica>01</replica>
        <cluster>cluster_1S_2R</cluster>
    </macros>
</clickhouse>
```

- **Replication and Sharding Configuration**:
  - Defines a cluster named `cluster_1S_2R` with one shard and two replicas.
  
```xml
<clickhouse>
    <remote_servers replace="true">
        <cluster_1S_2R>
            <secret>mysecretphrase</secret>
            <shard>
                <internal_replication>true</internal_replication>
                <replica>
                    <host>clickhouse-01.clickhouse</host>
                    <port>9000</port>
                </replica>
                <replica>
                    <host>clickhouse-02.clickhouse</host>
                    <port>9000</port>
                </replica>
            </shard>
        </cluster_1S_2R>
    </remote_servers>
</clickhouse>
```

- **Using ClickHouse Keeper**:
  - Configures ClickHouse Server to coordinate with ClickHouse Keeper.
  
```xml
<clickhouse>
    <zookeeper>
        <node>
            <host>clickhouse-keeper-01.clickhouse</host>
            <port>9181</port>
        </node>
        <node>
            <host>clickhouse-keeper-02.clickhouse</host>
            <port>9181</port>
        </node>
        <node>
            <host>clickhouse-keeper-03.clickhouse</host>
            <port>9181</port>
        </node>
    </zookeeper>
</clickhouse>
```

#### clickhouse-02 Configuration

The configuration is mostly similar to clickhouse-01, with key differences noted:

- **Network and Logging Configuration**:
  - Similar to clickhouse-01 but with a different display name.
  
- **Macros Configuration**:
  - The replica is set to 02 on this node.

#### clickhouse-keeper Configuration

For ClickHouse Keeper, each node configuration includes:

- **General Configuration**:
  - Ensure the server ID is unique across all instances.
  
```xml
<clickhouse>
    <logger>
        <level>trace</level>
        <log>/var/log/clickhouse-keeper/clickhouse-keeper.log</log>
        <errorlog>/var/log/clickhouse-keeper/clickhouse-keeper.err.log</errorlog>
        <size>1000M</size>
        <count>3</count>
    </logger>
    <listen_host>0.0.0.0</listen_host>
    <keeper_server>
        <tcp_port>9181</tcp_port>
        <server_id>1</server_id> <!-- Change for each keeper -->
        <log_storage_path>/var/lib/clickhouse/coordination/log</log_storage_path>
        <snapshot_storage_path>/var/lib/clickhouse/coordination/snapshots</snapshot_storage_path>
    </keeper_server>
</clickhouse>
```

### Image Baking and Deployment

All configuration changes were integrated into the Docker image using the base ClickHouse image. The configured image was then pushed to ECR and utilized in our ECS tasks for efficient deployment.

<p align="center">
  <img src="/images/blog/clickhouse-benchmarking/ecs-clickhouse-deployment.png" alt="ECS Clickhouse Deployment">
</p>

## ECS Cluster Setup and ClickHouse Deployment

### ClickHouse Deployment Overview

- **AWS Partner Solution:** We leveraged the AWS Partner Solution Deployment Guide for ClickHouse to ensure a structured setup.

- **ECS Cluster:** ClickHouse was deployed on Amazon ECS using a multi-node configuration, following best practices to achieve high availability.

#### VPC Configuration

- **Custom VPC:** A dedicated Virtual Private Cloud (VPC) was created with subnets designated for public and private instances. This configuration enhances security and streamlines component communication.

#### Security Measures

- **Security Groups:** Network traffic was restricted by configuring security groups to allow only necessary ports:
  - **8123** for HTTP
  - **9000** for TCP connections

#### Instance Type Selection

- **EC2 Instances:** Instance types were chosen based on the compute and memory needs of ClickHouse nodes, balancing performance and cost-effectiveness.

#### Database Configuration

- **Shards and Replicas:** The ClickHouse database was set up with **2 shards** and **1 replica**, following the static configuration recommended in the ClickHouse horizontal scaling documentation.

#### Container Image

- **Docker Image:** We utilized the `clickhouse/clickhouse-server` container image, which includes both the ClickHouse server and keeper.

#### Auto Scaling Configuration

- **Auto Scaling Group:** An Auto Scaling Group was set up with `m5.large` instances, providing **3 GB of memory** for each container to ensure optimal performance under varying loads.

## Performance Benchmarking Metrics

Now that the deployment architecture is established, let's move on to evaluating ClickHouse's performance through a series of benchmarking metrics.

### Data Ingestion Performance Metrics

- **Average Queries per Second:** This metric measures the sustained query ingestion rate during heavy load, offering insights into how well ClickHouse handles log ingestion.
  
- **CPU Usage (Cores):** Tracking the average CPU cores used during ingestion helps determine the efficiency of resource utilization during data ingestion.

- **IO Wait Time:** Indicates the time ClickHouse spent waiting for I/O operations, such as disk reads or writes, which directly impacts ingestion throughput.

- **OS CPU Usage:** This metric differentiates between user-space and kernel-space CPU usage to offer a clearer picture of where the processing power is consumed during data ingestion.

- **Disk Throughput:** Measures the average read/write throughput from the file system, crucial for understanding how efficiently data is being ingested and written to storage.

- **Memory Usage (Tracked):** Monitoring the memory consumed by ClickHouse over time helps identify potential memory bottlenecks during sustained ingestion loads.

### Query Execution Metrics

- **Response Times:** We measured the average query execution times, especially focusing on complex operations such as joins and aggregations.

- **CPU Wait Time:** This metric captures the latency introduced by waiting for CPU cycles during query execution, giving insight into query performance under load.

- **Average Selected Rows/Second:** This metric tracks how many rows ClickHouse processes per second during `SELECT` queries, offering a gauge for query throughput.

- **Average Merges Running:** In ClickHouse's MergeTree engine, merges are essential for optimizing data. Tracking the number of concurrent merges gives an indication of how well ClickHouse is handling data restructuring.

### Scalability Metrics

- **Load Average:** This metric tracks the system load over a 15-minute window, providing a real-time view of how ClickHouse handles varying loads.

- **Max Parts per Partition:** As part of the merging process, this metric reflects the largest number of parts within a partition, offering insight into how well ClickHouse manages its partitioning strategy.

- **TCP Connections:** The number of active TCP connections to the ClickHouse nodes reflects how well the system can handle network traffic under high query loads.

- **Memory Efficiency:** This metric monitors memory allocation efficiency and tracks peak memory usage during both data ingestion and query execution.

## Log Ingestion Testing

To benchmark log ingestion, we used the following table schema to handle log data:

```sql
CREATE TABLE logs
(
  `remote_addr` String,
  `remote_user` String,
  `runtime` UInt64,
  `time_local` DateTime,
  `request_type` String,
  `request_path` String,
  `request_protocol` String,
  `status` UInt64,
  `size` UInt64,
  `referrer` String,
  `user_agent` String
)
ENGINE = MergeTree
ORDER BY (toStartOfHour(time_local), status, request_path, remote_addr);
```

### Dataset

We used a public dataset containing 66 million records to perform ingestion tests. The dataset can be found at this [link](https://datasets-documentation.s3.eu-west-3.amazonaws.com/http_logs/data-66.csv.gz)

### Baseline Performance Testing

- **Initial Ingestion Rate:** We measured ingestion rates under normal load to evaluate whether real-time log ingestion was achievable.

- **Disk I/O:** Disk throughput was closely monitored to evaluate how well ClickHouse handles log writes and merges during ingestion.

### High Load Performance

- **Stress Testing:** Simulating log bursts under peak traffic allowed us to analyze the stability and performance of the ingestion pipeline.

- **Monitoring:** During high-load testing, key metrics such as CPU, memory, and I/O usage were tracked to ensure no bottlenecks surfaced.

## Query Performance Testing

To evaluate query performance, we designed several test queries ranging from simple `SELECT` statements to more complex join operations and aggregations.

### Test Queries

- **Simple Select Queries:** Evaluating performance for basic queries that retrieve specific fields from the `logs` table.

```sql
SELECT * FROM logs;
```

```sql
SELECT toStartOfInterval(toDateTime(time_local), INTERVAL 900 second) AS time, count() 
FROM logs 
WHERE time_local >= '1548288000' 
  AND time_local <= '1550966400' 
  AND status = 404 
  AND request_path = '/apple-touch-icon-precomposed.png' 
  AND remote_addr = '2.185.223.153' 
  AND runtime > 4000 
GROUP BY time 
ORDER BY time ASC 
LIMIT 10000;
```

- **Joins:** To test more complex queries, we used a join operation between two `logs` tables:

```sql
SELECT toStartOfInterval(toDateTime(l.time_local), INTERVAL 900 second) AS time, count() 
FROM logs l
JOIN logs_local ll ON l.remote_addr = ll.remote_addr AND l.time_local = ll.time_local
WHERE l.time_local >= '1548288000' 
  AND l.time_local <= '1550966400' 
  AND l.status = 404 
  AND l.request_path = '/apple-touch-icon-precomposed.png' 
  AND l.remote_addr = '2.185.223.153' 
  AND l.runtime > 4000 
GROUP BY time 
ORDER BY time ASC 
LIMIT 10000;
```

- **Aggregations:** Performance of aggregate queries was tested on fields like status codes and request paths.

```sql
SELECT uniq(remote_addr) AS `unique ips` 
FROM logs 
WHERE time_local >= '1548288000' 
  AND time_local <= '1550966400' 
  AND status = 404 
  AND request_path = '/apple-touch-icon-precomposed.png' 
  AND remote_addr = '2.185.223.153' 
  AND runtime > 4000;
```

```sql
SELECT toStartOfInterval(toDateTime(time_local), INTERVAL 900 second) AS time, avg(runtime) AS avg_request_time, quantile(0.99)(runtime) AS 99_runtime 
FROM logs 
WHERE time_local >= '1548288000' 
AND time_local <= '1550966400' 
AND status = 404 
AND request_path = '/apple-touch-icon-precomposed.png' 
AND remote_addr = '2.185.223.153' 
AND runtime > 4000 
GROUP BY time 
ORDER BY time ASC 
LIMIT 100000;
```

### Query Benchmarking Results

- **Response Time:** We documented the average response times for each type of query to understand performance under load.

- **Resource Utilization:** We tracked CPU, memory, and I/O usage during the execution of these queries to evaluate resource efficiency.

- **Throughput:** Finally, we measured how many queries could be executed per second under sustained load conditions.

**🔍 For detailed performance metrics and benchmarks, please refer to the full report [**here**](https://infraspec.getoutline.com/doc/clickhouse-deployment-and-performance-benchmarking-on-ecs-Stsim2Uoz1).**
