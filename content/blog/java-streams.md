---
title: "Unleashing the Power of Streams in Java"
authorIds: ["rahul"]
date: 2024-03-05
draft: false
featured: true
weight: 1
---

# Java Streams: A Paradigm Shift in Data Processing

## What are Streams?

Imagine a lazy river carrying data elements one by one. That's essentially what a stream is – a sequence of elements that you can process on the fly, without storing everything in memory at once. This makes them ideal for handling huge datasets without overwhelming your computer.

**Scenario:** Imagine you have a basket of apples. You want to count all the red apples. Traditionally, you might pick each apple, check its color, and increment a counter if it's red. This is similar to iterating through a list using a loop. With streams, it's like having a conveyor belt carrying the apples. You set up a "filter" that only lets red apples through. Then, you have a "counter" that automatically counts each red apple that passes through. You don't have to touch each apple individually, and you only process the red ones you're interested in.

Let's break down the magic with some code snippets and explanations:

## 1. Immutability: Ensuring Strong and Safe Code

**What is Immutability in Streams?**
Immutability ensures that the original data stays the same during stream operations. With Java Streams, it means making new streams without changing the existing data.

**How it Benefits:**
- **Predictable Behavior:** Immutability helps avoid accidental changes, making sure that one part of the code doesn't mess up another.
- **Thread Safety:** In places with lots of things happening at once (multi-threaded), immutability acts like a safety net. Many threads can use the original data at the same time without causing problems.

**Code Snippet and Benchmark Output:**

```java
// Immutability with Streams
List<Integer> values = Arrays.asList(1, 10, 3, 4, 2);

Stream<Integer> mappedValues = values.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n + 1);

List<Integer> modifiedList = mappedValues.toList();

System.out.println("Original List: " + values);
System.out.println("Modified List: " + modifiedList);
System.out.println("The above two lists are equal? " + (mappedValues.count() == values.size()));
```

**Analysis:**

- The starting list stays the same; nothing is changed, proving that streams keep things unchanged.
- When we filter and map, it's like making a fresh stream, leaving the original data intact.
- Using `toList()` helps make a new list without messing up anything. It's like a safety feature for threads.

**Benchmark Output:**

```
Original List: [1, 10, 3, 4, 2]
Modified List: [11, 5]
Lists Equality: true
```

## 2. One-Time Use: Ensuring Stream Integrity

**What is the One-Time Use of Streams?**
Streams, once consumed, cannot be reused. This design ensures that each stream operation, especially terminal operations, represents a distinct processing step. Once a terminal operation is invoked on a stream, it marks the end of its usability for further operations.

**How it Benefits:**

- **Efficient Resource Management:** When you have a large amount of data, utilizing streams in Java aligns with the practice of processing data and closing resources promptly. This practice helps prevent data leakage and minimizes the presence of unused resources.
- **Prevention of Unintended Behavior:** The inability to reuse streams after terminal operations minimizes the risk of unintended side effects, promoting safer and more controlled data manipulation. Attempting to use a consumed stream again results in an `IllegalStateException`, ensuring a clear and intentional data processing flow.

**Code Snippet and Benchmark Output:**

```java
// Creating a stream from the list
Stream<Integer> mappedValues = list.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n + 1);

// Using a terminal operation 'count'
long count = mappedValues.count();

// Attempting to reuse the stream will result in an exception
try {
    // This line attempts to reuse the 'mappedValues' stream
    System.out.println("Reused Stream: " + mappedValues.toList());
} catch (IllegalStateException e) {
    System.out.println("Error: " + e.getMessage());
}
```

**Analysis:**

- The code begins by creating a stream, `mappedValues`, from the original list.
- The stream is processed with an intermediate operation (`filter` and `map`) and a terminal operation (`count`).
- Attempting to reuse the `mappedValues` stream (here with `toList()`) after the terminal operation will result in an `IllegalStateException`. This error occurs because once a stream is consumed by a terminal operation, it cannot be reused for another terminal operation.
- The use of `count()` serves as a point of consumption, making the stream no longer available for further terminal operations.

**Output:**

```shell
Error: stream has already been operated upon or closed
```

## 3. Parallel Streams: Leveraging Multi Core Power for Performance

**What are Parallel Streams?**
Parallel streams divide the workload among multiple threads, leveraging the power of multicore processors for concurrent execution. They are designed for efficient processing of large datasets.

**How it Benefits:**

- **Reduced Execution Time:** Parallel processing leads to shorter execution times compared to sequential streams, especially when dealing with massive datasets.
- **Optimal Resource Utilization:** Multicore processors are fully utilized, making parallel streams ideal for performance optimization.

**Code Snippet and Benchmark Output:**

```java
// Populate the list with values
for (int i = 0; i < datasetSize; i++) {
    values.add(random.nextInt(Integer.MAX_VALUE));
}

// Parallel Stream Processing
long parallelStartTime = System.currentTimeMillis();
values.parallelStream()
    .sorted()
    .toList();
long parallelEndTime = System.currentTimeMillis();
long parallelTimeTaken = parallelEndTime - parallelStartTime;

System.out.println("\n");

// Sequential Stream Processing
long sequentialStartTime = System.currentTimeMillis();
values.stream()
    .sorted()
    .toList();
long sequentialEndTime = System.currentTimeMillis();
long sequentialTimeTaken = sequentialEndTime - sequentialStartTime;
```

**Scenario 1: Small Dataset (datasetSize = 10) Analysis:**

- The dataset is deliberately kept small to showcase the impact on performance.
- Parallel processing does not demonstrate a significant advantage due to the overhead of managing parallel threads which overshadows the potential advantages.

**Benchmark Output:**

```
Parallel Time Taken: 9 milliseconds
Sequential Time Taken: 0 milliseconds
```

**Scenario 2: Large Dataset (datasetSize = 1,000,000) Analysis:**

- Parallel streams potentially perform better when dealing with large datasets.
- The process of dividing the work among multiple threads becomes more advantageous for significant workloads.
- Multicore processors are utilized optimally, leading to shorter execution times compared to sequential streams.

**Benchmark Output:**

```
Parallel Time Taken: 2318 milliseconds
Sequential Time Taken: 7789 milliseconds
```

## Parallel Stream and Synchronous Resources

In Java, the use of parallel streams can significantly improve performance for certain operations. However, when dealing with synchronous resources, such as `System.out.println()`, the impact of parallel streams is limited. Let's explore the general concept and illustrate it using an example.

### 1. Synchronous Nature of System.out.println():

- `System.out.println()` is inherently synchronous and operates in a single-threaded manner.
- It's a blocking operation, printing text to the console one line at a time.
- When multiple threads execute `println()` statements, the output becomes sequential.

**Example:**

```java
List<Integer> list = Arrays.asList(1, 2, 3, 4, 5);

// Synchronous output
System.out.println("Sequential Stream:");
list.forEach(value -> {
    System.out.println("Value " + value + " - thread " + Thread.currentThread().getName());
});
```

### 2. Limited Impact on Parallel Streams with Synchronous Resources:

- Parallel streams are designed to parallelize operations on data.
- When using parallel streams with synchronous resources like `System.out.println()`, parallel processing is applied to the data, but the printing remains sequential.
- The synchronous nature of the resource limits the full potential of parallelization.

**Example:**

```java
// Limited impact with parallel streams
System.out.println("\nParallel Stream:");
list.parallelStream()
    .forEach(value -> {
        System.out.println("Value " + value + " - thread " + Thread.currentThread().getName());
    });
```

### 3. Real Benefits of Parallel Streams:

- Parallel streams are most effective for CPU-bound or I/O-bound operations that can be parallelized.
- They shine in scenarios where parallelization can significantly improve performance, such as parallelizing CPU-bound or I/O-bound tasks.

## 4. Lazy Evaluation: Optimal Resource Utilization

**What is Lazy Evaluation in Streams?**
Lazy evaluation means that operations on a stream are not executed until a terminal operation is invoked. This allows for efficient resource usage by processing only the elements necessary for the final result.

**How it Benefits:**

- **Efficient Resource Utilization:** Elements are processed on-demand, saving processing time and memory.
- **Suitable for Large Datasets:** Laziness ensures that the stream doesn't process the entire dataset if it's not required for the final result.

**Code Snippet and Benchmark Output:**

```java
// Leveraging Lazy Evaluation
List<Integer> values = Arrays.asList(1, 2, 5, 10, 15);

Stream<Integer> doubleValues = values.stream()
    .filter(LazyEvaluation::isDivisibleBy5)
    .map(LazyEvaluation::doubleValue);

System.out.println(doubleValues.findFirst().orElse(0));
```

**Analysis:**

- The stream operations, `filter` and `map`, are defined but not immediately executed.
- Processing occurs only when the terminal operation `findFirst()` is invoked.
- The lazy nature ensures that only elements needed for the final result are processed, saving resources.
- The output demonstrates the selective processing of elements that meet the specified criteria.

**Output:**

```
in isDivisibleBy5 1
in isDivisibleBy5 2
in isDivisibleBy5 5
in doubleValue 5
Result: 10
```

## In Summary

Using Java Streams goes beyond just syntax – it's a game-changer in how we handle data. The code snippets we explored dig into the inner workings, showcasing the simplicity, effectiveness, and practical use of Java Streams. Dive into the world of streams, where both imperative and functional approaches blend seamlessly, and watch your Java coding experience evolve.
