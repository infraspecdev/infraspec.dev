---
title: "Cache Strategies"
authorIds: ["sanjay"]
date: 2024-09-25
draft: false
featured: true
weight: 1
sitemap:
changefreq: "monthly"
priority: 1
---

## What is Caching?

Caching is a technique that enhances application performance by temporarily storing frequently accessed data in high-speed data storage hardware like RAM. This temporary storage is called a Cache. Instead of repeatedly retrieving data from the original/primary Data source, the application can quickly access it from the Cache. This reduces response time and improves the overall throughput of the application.

## Why do we need Caching?

There are various benefits of Caching the frequently accessed data at different layers in caching:

- **Reduced Latency:** It helps reduce the latency by storing the frequently accessed data in high-speed data storage hardware making the data retrieval faster.

- **Reduced Load on Backend Systems:** It helps reduce the backend system load by serving the frequently accessed data from the Cache.

- **Cost Efficiency:** It reduces the no. of requests made to the original/primary data source or some external services hence lowering the operating cost.

- **Better User Experience:** It reduces the application's load time, makes it user-friendly, and increases engagement.

- **Improved Scalability:** As it reduces the response time of the request, the caching allows the application to handle more requests simultaneously, improving the overall throughput of the system(read-throughput).

## Various Layers of Caching

Caching can be applied at various levels of an application stack, each serving a specific purpose and enhancing the performance in its way. Understanding these various types of cache and their use cases is essential to design an efficient system.

**CDN(Content Delivery Network) Cache:** A CDN cache is used to store copies of static assets (e.g., images, videos, CSS, JavaScript files)  closer to the end users across geographically distributed servers. The goal is to reduce latency and reduce traffic from the origin server by serving cached content directly from the nearest CDN server.

Imagine a car factory where all cars are produced. If you have to buy directly from the factory, you need to travel far, which takes time and effort. If everyone does this, the factory gets crowded, slowing things down. Now, instead of going to the factory, local showrooms are set up nearby with popular car models ready to go. This saves time for customers and reduces the load on the factory, as fewer people need to go there directly. Similarly, a CDN brings content closer to users, improving speed and reducing strain on the origin server.

Applications with high volumes of static content or media use CDN caching to reduce response time and improve performance for delivering static assets globally. Examples include streaming services, news platforms, and shopping applications.
<br/>
<p align="center">
  <img width="800px" src="/images/blog/cache-strategies/cdn-cache.png" alt="CDN Cache">
</p>

**Browser or Client Side Cache:** The browser or client cache involves storing frequently accessed resources, such as images, scripts, or API responses, locally on the user's device. This helps avoid repeated network requests for the same resources, improving page load times. By setting expiration times for cached items, developers can control how long the data remains valid, ensuring that users receive fresh content while minimizing redundant requests. As a result, pages load faster for users, and server load is reduced.
<br/>
<p align="center">
  <img width="800px" src="/images/blog/cache-strategies/browser-cache.png" alt="Client Side Cache">
</p>

**Database Cache(Query Cache):** Database caching involves storing frequently queried data to reduce the load on the database and speed up query execution. The cache can be managed by the database management system (DBMS), exist within the application, or function as a standalone layer. When a query is executed, the DBMS checks the cache first; if the results are found, they are returned without querying the database. This approach is especially beneficial for high-traffic applications, as it leads to faster query results and improved overall performance. Examples include e-commerce platforms and social media sites, with solutions like MySQL Query Cache or ORM tools like Hibernate for Java that support caching.

**Application/Server Side Cache:** In application-side (server-side) caching, data is cached directly by the server or application layer, either in memory or using external caching systems like Redis or Memcached. This strategy enhances performance by quickly serving frequently accessed data. It is particularly beneficial for backend systems or microservices that often fetch the same data, such as API responses or user profiles. The result is faster access to commonly used data, reduced external API or database calls, and improved application responsiveness. This makes it one of the most commonly used caching layers.
<br/>
<p align="center">
  <img width="800px" src="/images/blog/cache-strategies/server-cache.png" alt="Server Side Cache">
</p>

**Distributed Cache:** A distributed cache works across multiple nodes or servers, making it accessible to different parts of the system in a scalable and fault-tolerant way. It's often used in large applications to ensure high availability and consistent data. Common tools for distributed caching include Redis and Apache Ignite. This approach is useful for microservices architectures, cloud-based applications, and systems that need to share data across instances. The main benefits are scalability, fault tolerance, and having a single source of truth for cached data.
<br/>
<p align="center">
  <img width="800px" src="/images/blog/cache-strategies/distributed-cache.png" alt="Distributed Cache">
</p>

## Cache Strategies(Server Side Caching)

**Cache-Aside:** In this strategy, the application code is responsible for managing the Cache. It handles when to read from the cache or fetch data from the underlying data source. The sequence of actions followed in the Cache-Aside strategy is as follows:

- Check cache for data(Cache-Hit): When a request is made, the application first queries the data in the Cache. If the requested data is found(Cache-Hit), it is directly returned.

- Fetch from Data Source(Cache-Miss): If the data is not found in the Cache(Cache-Miss), the application retrieves the required data from the underlying data source(e.g., Database or API).

- Update Cache with Fresh Data: After fetching the data from the primary data source, the application updates the cache with fresh data for future requests.

- Return the data to the client/caller: Finally, the application returns the data to the client/caller,  whether from the cache or after being fetched from the data source.

<br/>
<p align="center">
  <img width="800px" src="/images/blog/cache-strategies/cache-aside.png" alt="Cache Aside Cache Strategy">
</p>

**Read Through:** In this strategy, the responsibility for managing the cache lies with the cache layer rather than the application code. The application layer calls the cache layer to request data, and the cache layer handles whether to read from the cache or fetch data from the underlying data source. The sequence of actions followed in the Read-Through strategy is as follows:

- Check cache for Data (Cache-Hit): When a request is made, the cache layer first checks for the requested data in the cache. If the data is found (Cache Hit), it is directly returned from the cache.

- Fetch from Data Source (Cache-Miss): If the data is not found in the cache (Cache Miss), the cache layer automatically fetches the data from the underlying data source (e.g., a database or API).

- Update Cache with Fresh Data: Once the data is retrieved from the primary data source, the cache layer updates the cache with the fresh data for future requests.

- Return the Data to the Client/Caller: Finally, the data is returned to the client/caller, whether it was retrieved from the cache or fetched from the data source.

<br/>
<p align="center">
  <img width="800px" src="/images/blog/cache-strategies/read-through.png" alt="Read Through Cache Strategy">
</p>

**Write Around:** In this strategy, the application code is responsible for managing the Cache. When data is written or updated, it is directly sent to the primary data source, and the corresponding cache entry is cleared if present.

- On the next read request, the process follows the same as the Cache-Aside strategy. The sequence of actions followed in the Write Around strategy is as follows:

- Write/Update to Data Source and Clear Cache: When new data is written or existing data is updated, the application stores it in the primary data source and clears the relevant cache entry, if present.

- Check Cache for Data (Cache-Hit on Read): When a read request is made, the application first checks the cache. If the data is available (Cache-Hit), it is returned immediately.

- Fetch from Data Source (Cache-Miss on Read): If the requested data is not found in the cache (Cache-Miss), the application retrieves it from the underlying data source (e.g., database, API).

- Update Cache with Fresh Data: After fetching the data, the application updates the cache for quicker future access.

- Return the Data to the Client/Caller: The fetched data, whether from the cache or the primary data source, is returned to the client/caller.

<br/>
<p align="center">
  <img width="800px" src="/images/blog/cache-strategies/write-around.png" alt="Write Around Cache Strategy">
</p>

**Write Through:** In this strategy, the cache layer manages the data in the cache and the underlying data source. When data is written or updated, the cache layer ensures the changes are synchronized in both locations. The sequence of actions followed in the Write-Through strategy is as follows:

- Write/Update to Cache: When new data is written or existing data is updated, the application layer calls the cache layer, which first writes or updates the data in the cache.

- Synchronously Write/Update to Data Source: After updating the cache, the cache layer immediately writes or updates the data in the underlying data source (e.g., a database or API) in a synchronous manner to ensure consistency between the cache and the data source.

<br/>
<p align="center">
  <img width="800px" src="/images/blog/cache-strategies/write-through.png" alt="Write Through Cache Strategy">
</p>

**Write Behind:** In this strategy, the cache layer manages data updates asynchronously. When data is written or updated, the application layer calls the cache layer, which immediately updates the cache while delaying the write to the primary data source. The data is then written to the underlying data source after a specified interval, with the cache maintaining a buffer of changes until the update occurs. The sequence of actions followed in the Write-Behind strategy is as follows:

- Write/Update to Cache: When new data is written or existing data is updated, the application layer calls the cache layer, which immediately updates the data in the cache.

- Buffer Data in Cache: The cache layer maintains a buffer of the updated data in the cache, temporarily holding the changes before committing them to the primary data source.

- Asynchronously Write/Update to Data Source: After a specified interval, the cache layer writes or updates the buffered data in the primary data source (e.g., a database or API), ensuring eventual consistency between the cache and the data source.

<br/>
<p align="center">
  <img width="800px" src="/images/blog/cache-strategies/write-behind.png" alt="Write Behind Cache Strategy">
</p>

## Conclusion

In this article, we discussed what is caching, why we need caching, different levels of caching, and various caching strategies that we use for server-side caching.
Finally, I would say where to cache the data and what strategy to use for caching entirely depends on the application’s requirements.

That was all for this article. I hope you found it useful!

## References

[Oracle Documentation](https://docs.oracle.com/cd/E16459_01/coh.350/e14510/readthrough.htm)
<br/>
[Other Resource](https://www.alachisoft.com/resources/articles/readthru-writethru-writebehind.html)
