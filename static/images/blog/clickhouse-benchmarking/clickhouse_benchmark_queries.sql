-- Schema
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
  `referer` String,
  `user_agent` String
)
ENGINE = MergeTree
ORDER BY (toStartOfHour(time_local), status, request_path, remote_addr);

-- Simple Select Queries
SELECT * FROM logs;

SELECT toStartOfInterval(toDateTime(time_local), INTERVAL 900 second) AS time, count() 
FROM logs 
WHERE time_local >= '1548288000' AND time_local <= '1550966400' 
AND status = 404 AND request_path = '/apple-touch-icon-precomposed.png' 
AND remote_addr = '2.185.223.153' AND runtime > 4000 
GROUP BY time 
ORDER BY time ASC 
LIMIT 10000;

-- Join Query
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

-- Aggregation Queries
SELECT uniq(remote_addr) AS `unique ips` 
FROM logs 
WHERE time_local >= '1548288000' 
AND time_local <= '1550966400' 
AND status = 404 
AND request_path = '/apple-touch-icon-precomposed.png' 
AND remote_addr = '2.185.223.153' 
AND runtime > 4000;

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
