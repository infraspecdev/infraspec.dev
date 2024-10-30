---
title: "ClickHouse Performance Benchmarking on ECS for Log Storage and Querying"
authorId: "rohit"
date: 2024-10-21
draft: false
featured: true
weight: 1
---

Imagine being a Formula One driver, racing at breakneck speeds, but without any telemetry data to guide you. It’s a thrilling ride, but one wrong turn or an overheating engine could lead to disaster. Just like a pit crew relies on performance metrics to optimize the car's speed and handling, we rely on observability in ClickHouse to monitor the health of our data systems for storing and querying logs. These metrics provide crucial insights, allowing us to identify bottlenecks, prevent outages, and fine-tune performance, ensuring our data engine runs as smoothly and efficiently as a championship-winning race car.

In this blog, we’ll focus on performance benchmarking ClickHouse on AWS ECS in the context of log storage and querying, analyzing key system metrics like CPU usage, memory consumption, disk I/O, and row insertion rates across varying data ingestion volumes.

For setting up the ClickHouse cluster, we followed the [ClickHouse replication architecture guide](https://clickhouse.com/docs/en/architecture/replication) and the [AWS CloudFormation ClickHouse cluster setup](https://aws-ia.github.io/cfn-ps-clickhouse-cluster/). Using these resources, we replicated the setup on ECS, allowing us to run performance benchmarking tests on the environment.

> For this benchmarking, we deployed ClickHouse version `24.3.12.75` for both `clickhouse-server` and `clickhouse-keeper`. Our ECS cluster configuration included a fault-tolerant setup with **1 shard and 2 replicas**, composed of **2 ClickHouse server nodes** and **3 ClickHouse Keeper nodes**. Each node was provisioned on **m5.xlarge** instances, ensuring the necessary resources to handle our high-ingestion and query-intensive workloads.

By examining performance metrics during the ingestion of 1 million, 5 million, 10 million, and 66 million logs, we aim to provide a quantitative analysis of how system behavior changes as the load increases.

<p align="left">
  <img src="/images/blog/clickhouse-benchmarking/clickhouse-cluster-ingestion.png" alt="clickhouse-cluster-ingestion" style="border-radius: 10px; width: 650px; height: 300px;">
</p>

For more details on the schema and test queries used, you can [download the SQL file here](/images/blog/clickhouse-benchmarking/clickhouse_benchmark_queries.sql).

## Performance Comparison of Key Metrics Across Ingestion Volumes

| `Logs Ingested` | `CPU Usage (Cores)` | `Selected Bytes per Second (B/s)` | `IO Wait (s)` | `CPU Wait (s)` | `Read from Disk (B)` | `Read from Filesystem (B)` | `Memory Tracked (Bytes)` | `Selected Rows per Second` | `Inserted Rows per Second` |
|-------------------|-----------------------|------------------------------------|-----------------|-----------------|------------------------|------------------------------|----------------------------|------------------------------|------------------------------|
| `1 Million (10 Lakh)` | 0.103 | 27,118.35 | 0.000 | 0.0217 | 0.000 | 439,023.78 | 714,778,747.45 | 256.88 | 238,666.67 |
| `5 Million (50 Lakh)` | 0.111 | 37,545.82 | 0.000 | 0.0058 | 0.000 | 532,938.08 | 738,249,399.13 | 256.88 | 238,666.67 |
| `10 Million (1 Crore)` | 0.433 | 36,265,260.35 | 0.000 | 0.3297 | 1,843.20 | 3,323,855.43 | 1,030,697,939.98 | 146,848.98 | 140,193.58 |
| `66 Million (6.6 Crore)` | 1.179 | 122,710,173.00 | 0.750 | 4.4276 | 17,330,176.00 | 14,303,693.00 | 2,065,638,032.00 | 365,589.00 | 365,589.00 |

<p align="center">
  <img src="/images/blog/clickhouse-benchmarking/clickhouse-write-operations.png" alt="clickhouse-benchmarking" style="border-radius: 10px; width: 300; height: 500;">
</p>

### Key Insights from the Data

#### 1. `CPU Usage (avg_cpu_usage_cores)`

- At 1 million logs, the CPU usage was minimal at `0.103` cores, indicating a low load on the system.
- This increased marginally to `0.111 cores` when ingesting 5 million logs.
- However, there was a significant jump when ingesting `10 million logs`, where CPU usage hit `0.433 cores` due to increased processing demands.
- At `66 million logs`, the CPU usage surged to `1.179 cores`, showing that ClickHouse required far more processing power as the data ingestion rate scaled up.

#### 2. `Selected Bytes per Second (avg_selected_bytes_per_second)`

- `For 1 million logs`, the system processed `27,118 bytes/sec`, and this grew to `37,546 bytes/sec` for `5 million logs`.
- The ingestion of `10 million logs` saw a massive jump to `36.26 MB/sec`, highlighting how ClickHouse optimizes throughput as data scales.
- With `66 million logs`, the throughput reached `122 MB/sec`, showcasing ClickHouse’s excellent scalability in handling large data volumes.

#### 3. `I/O Wait (avg_io_wait)`

- `IO wait times` were negligible for smaller ingestion rates (1 and 5 million logs) at `0 seconds`.
- When ingesting `10 million logs`, `IO wait` remained at `0 seconds`, indicating efficient disk I/O handling.
- However, for `66 million logs`, we saw a significant spike in `IO wait` to `0.75 seconds`, suggesting that the disk subsystem became a bottleneck at this larger ingestion scale.

#### 4. `CPU Wait (avg_cpu_wait)`

- `CPU wait times` were minimal at `0.0217 seconds` during the ingestion of `1 million logs`.
- This decreased to `0.0058 seconds` during the ingestion of `5 million logs`, reflecting improved processing efficiency.
- As the ingestion size grew to `10 million logs`, CPU wait times increased significantly to `0.3297 seconds`.
- For `66 million logs`, CPU wait peaked at `4.4276 seconds`, indicating heavy contention for CPU resources.

#### 5. `Disk Reads (avg_read_from_disk)`

- Disk reads were `0 bytes` during both the `1 million` and `5 million log` ingestions, indicating that all data operations were handled in-memory or by the filesystem.
- At `10 million logs`, disk reads spiked to `1.843 MB`, indicating that ClickHouse started pulling more data from disk.
- For `66 million logs`, disk reads increased drastically to `17.33 MB`, showing that the system leaned more on disk I/O as the data volume grew.

#### 6. `Filesystem Reads (avg_read_from_filesystem)`

- Filesystem reads followed a similar pattern, starting low with `439 KB` for `1 million logs` and `533 KB` for `5 million logs`.
- At `10 million logs`, this metric jumped to `3.32 MB`, as the system started to fetch more data from the filesystem.
- During the `66 million log` ingestion, filesystem reads skyrocketed to `14.3 MB`, further indicating the need for high I/O throughput at large ingestion scales.

#### 7. `Memory Usage (avg_memory_tracked)`

- `Memory tracked` during the ingestion of `1 million logs` was `714 MB`, which increased slightly to `738 MB` for `5 million logs`.
- However, as the log volume increased to `10 million logs`, memory consumption jumped to `1 GB`, indicating ClickHouse’s reliance on memory for faster ingestion.
- For `66 million logs`, memory usage peaked at `2.06 GB`, suggesting that memory capacity plays a crucial role in handling high-volume ingestions.

#### 8. `Selected Rows per Second (avg_selected_rows_per_second)`

- For `both 1 million and 5 million logs`, `256 rows/sec` were selected, reflecting consistent read performance under lighter loads.
- During the `10 million log` ingestion, the rate jumped to `146,849 rows/sec`, a significant increase as ClickHouse optimized its read performance.
- At `66 million logs`, selected rows spiked to `365,589 rows/sec`, highlighting the system’s ability to maintain high read throughput even as write loads scale.

#### 9. `Inserted Rows per Second (avg_inserted_rows_per_second)`

- The `inserted rows per second` remained consistent at `238,666 rows/sec` for both `1 million and 5 million logs`.
- During the ingestion of `10 million logs`, the rate climbed to `140,193 rows/sec`, indicating that ClickHouse scaled write operations efficiently.
- At `66 million logs`, the system handled an impressive `365,589 rows/sec`, reflecting excellent scaling of insertion throughput.

## Performance in Read-Heavy Operations

ClickHouse’s performance during read-heavy operations, including `SELECT`, aggregate, and `JOIN` queries, is critical for applications relying on fast data retrieval. Here, we analyze key system metrics across different configurations: two-node replicas under load balancing and a single-node configuration due to failover.

<p align="left">
  <img src="/images/blog/clickhouse-benchmarking/clickhouse-cluster-read.png" alt="clickhouse-cluster-ingestion" style="border-radius: 10px; width: 650px; height: 300px;">
</p>

### Performance Comparison of Key Metrics Across Configurations

| `Configuration` | `CPU Usage (Cores)` | `Selected Bytes per Second (B/s)` | `IO Wait (s)` | `CPU Wait (s)` | `Read from Disk (B)` | `Read from Filesystem (B)` | `Memory Tracked (Bytes)` | `Selected Rows per Second` | `Inserted Rows per Second` |
|-------------------|-----------------------|------------------------------------|-----------------|-----------------|------------------------|------------------------------|----------------------------|------------------------------|------------------------------|
| `Two Nodes (Node-1)` | 0.574 – 0.875 | 143,598,799.18 – 224,235,858.8 | 0.0002 – 0.0077 | 1.045 – 1.9356 | 13,768,499.2 – 21,592,132.27 | 14,377,664.77 – 22,227,520.87 | 727,494,761.07 – 956,479,931 | 412,713.28 – 648,431.85 | 246.08 – 2,006 |
| `Two Nodes (Node-2)` | 0.493 – 0.122 | 80,651,591.63 – 22,842.02 | 0.0047 – 0 | 1.0964 – 0.0039 | 7,768,951.47 – 0 | 8,374,316.53 – 589,784.78 | 819,671,565.67 – 725,970,944 | 232,168.82 – 238.1 | 253.93 – 238.1 |
| `Single Node (Node-2 Down)` | 0.529 – 0.883 | 158,795,019 – 283,619,700.4 | 0.0002 | 1.8338 – 9.1992 | 3,258,299.73 – 11,590,451.2 | 32,649,785.97 – 30,984,717.98 | 877,527,596.88 – 903,618,884.9 | 458,760 – 9,742,907.23 | 214.92 – 222.00 |

<p align="center">
  <img src="/images/blog/clickhouse-benchmarking/clickhouse-read-operations.png" alt="clickhouse-benchmarking" style="border-radius: 10px; width: 300; height: 500;">
</p>

### Key Insights from the Data

#### 1. `CPU Usage (avg_cpu_usage_cores)`

- `Node-1` in the two-node configuration showed CPU usage between `0.574 to 0.875 cores`, with higher loads during complex query executions.
- `Node-2` showed lower CPU usage overall, ranging between `0.493 to 0.122 cores` due to load balancing.
- `Single Node configuration` saw the CPU usage fluctuate from `0.529 to 0.883 cores`, as it handled all query loads without load balancing support.

#### 2. `Selected Bytes per Second (avg_selected_bytes_per_second)`

- In the two-node configuration, `Node-1` selected bytes per second ranged from `143,598,799.18 to 224,235,858.8 B/s`, whereas `Node-2` showed lower selected bytes per second, from `80,651,591.63 to 22,842.02 B/s`, indicating an uneven load distribution.
- In the `Single Node configuration`, this metric ranged from `158,795,019 to 283,619,700.4 B/s`, indicating the node’s capability to handle high data selection rates.

#### 3. `I/O Wait (avg_io_wait)`

- `Node-1` experienced minimal I/O wait, from `0.0002 to 0.0077 seconds`, while `Node-2` showed no I/O wait when handling lower loads.
- The `Single Node configuration` maintained `0.0002 seconds` for I/O wait, reflecting efficient I/O handling even under increased loads.

#### 4. `CPU Wait (avg_cpu_wait)`

- `Node-1` in the two-node setup had a CPU wait ranging from `1.045 to 1.9356 seconds` during heavier query processing, while `Node-2` had a much lower CPU wait from `1.0964 to 0.0039 seconds`.
- In `Single Node mode`, CPU wait times increased dramatically, ranging from `1.8338 to 9.1992 seconds`, indicating contention for CPU resources under increased query load.

#### 5. `Disk Reads (avg_read_from_disk)`

- Disk reads for `Node-1` ranged from `13,768,499.2 to 21,592,132.27 bytes` in the two-node configuration, with `Node-2` reading `7,768,951.47 to 0 bytes` depending on load distribution.
- In `Single Node configuration`, disk reads increased significantly, varying from `3,258,299.73 to 11,590,451.2 bytes` under solo operation, revealing increased reliance on disk when a single node handled queries.

#### 6. `Filesystem Reads (avg_read_from_filesystem)`

- `Filesystem reads on Node-1` ranged from `14,377,664.77 to 22,227,520.87 bytes` in the two-node setup, while `Node-2` saw reads between `8,374,316.53 and 589,784.78 bytes`.
- In `Single Node configuration`, filesystem reads ranged from `32,649,785.97 to 30,984,717.98 bytes`, showing a notable increase compared to the two-node configuration.

#### 7. `Memory Usage (avg_memory_tracked)`

- `Memory tracked` for `Node-1` ranged from `727,494,761.07 to 956,479,931 bytes`, and `Node-2` from `819,671,565.67 to 725,970,944 bytes` in the two-node setup.
- In `Single Node mode`, memory usage varied from `877,527,596.88 to 903,618,884.9 bytes`, indicating increased memory demand when handling queries without load balancing.

#### 8. `Selected Rows per Second (avg_selected_rows_per_second)`

- `Node-1` showed a row selection rate from `412,713.28 to 648,431.85 rows/sec`, while `Node-2` had rates from `232,168.82 to 238.1 rows/sec` in the two-node setup.
- In `Single Node mode`, selected rows per second varied widely from `458,760 to 9,742,907.23 rows/sec`, demonstrating the node’s ability to manage high query demands under load.

#### 9. `Inserted Rows per Second (avg_inserted_rows_per_second)`

- The `inserted rows per second` remained low on `Node-1` with `246.08 to 2,006 rows/sec` and on `Node-2` with `253.93 to 238.1 rows/sec` in the two-node setup.
- In `Single Node mode`, insertion rates were steady from `214.92 to 222 rows/sec`, suggesting minimal impact on insertions despite high query activity.

### Conclusion

This benchmarking study highlights ClickHouse’s ability to handle both high-ingestion and read-intensive workloads on ECS. For ingestion, ClickHouse efficiently managed small data loads, but higher volumes (10M and 66M logs) led to significant increases in CPU, memory, and I/O wait, indicating the need for resource scaling.

For read operations, a two-node setup provided balanced CPU and I/O distribution, while a single-node setup led to increased CPU wait and resource contention under full query load.

To optimize performance, monitoring key metrics like `CPU usage`, `I/O wait`, and `memory` is essential, and leveraging multi-node configurations can help maintain efficient performance under heavy workloads.
