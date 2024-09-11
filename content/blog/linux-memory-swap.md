---
title: "Understanding memory and swap usage in Linux"
authorId: "nimisha"
date: 2024-04-15
draft: false
featured: true
weight: 1
---


## Introduction

<p style='text-align: justify;'>This blog will help you figure out how to check how much memory is left on your Linux machine. Knowing this will tell you if your server is running low on memory and needs attention, or if everything is fine. Following this, an explanation will be provided regarding the concept of swap and its relevance for the operation of a Linux machine or server.</p>

### Output of ` htop ` command

<img src="/images/blog/linux-memory-swap/htop.png" alt="My Collection" width="100%">

## What is htop?

<p style='text-align: justify;'>Htop is a resource monitoring utility, here we can see the amount of resources being used and how much memory is being used htop also shows the number of CPUs, the average CPU usage, and the amount of swap usage</p>

<p style='text-align: justify;'>The issue is that most of the times htop is not always available in Linux servers, but most distributions make the htop available to install, but some Linux distributions don't offer htop to install even in the standard repository</p>

<p style='text-align: justify;'>Next, we will explore how to view the amount of memory usage without relying on third-party utilities. This leads us to the first command, the free command. The free command provides information on the amount of free memory available.</p>

### Output of  ` free `  command

```bash

  user@machineHost:~$ free
                      total       used        free        shared      buff/cache      available
  Mem:             16148256    4191812        4560        619412         2315200       11956444
  Swap:                2048          0        2048
 
```
<p style='text-align: justify;'>However, these numbers may not be immediately comprehensible. Therefore, we will utilize the -m option with the free command, which presents the memory statistics in megabytes, making them easier to interpret.</p>

### Output of ` free -m ` command

```bash

  user@machineHost:~$ free
                      total       used        free        shared      buff/cache      available
  Mem:                15769       4191         456           522            2178          11593
  Swap:                2048          0        2048
 
```

<p style='text-align: justify;'>Determining the amount of free memory in Linux can be confusing. We might initially look at the <b>free</b> field and feel concerned if we see only 100MB of free memory. However, focusing on the <b>available</b> field provides a better picture. If we find 1000MB of available memory, we can feel reassured. </p>

<p style='text-align: justify;'>Simply checking the <b>available</b> field in the free command gives us an idea of available memory, but it's not the whole story. Let's explore how Linux manages memory.</p>

<p style='text-align: justify;'>The <b>total</b> field indicates the total memory installed, while <b>used</b> shows current memory usage by processes. <b>Free</b> indicates unused memory, and <b>available</b> represents memory ready for use, including cached data.</p>

<p style='text-align: justify;'>In Linux, <b>unused RAM is Wasted RAM</b>. Linux caches data in RAM for quicker access, meaning the <b>available</b> field includes memory used for caching but is ready for immediate use if needed.</p>

<p style='text-align: justify;'>In summary, Linux optimizes RAM usage by caching data, ensuring efficient memory utilization for better system performance.</p>

Now, we'll shift our focus to swap usage.

## What is Swap?

<p style='text-align: justify;'>Swap memory, also known as swap space, is a section of a computer's hard disk or SSD that the operating system (OS) uses to store inactive data from Random Access Memory (RAM). Because swap exists on the hard disk, accessing swap memory is slower compared to accessing RAM.
While swap is something we hope to avoid using, it serves as a safety net for when RAM becomes full. It's debated whether it's okay to run a Linux server or workstation without swap, but having some swap space, even sparingly like 1GB, doesn't heavily impact the hard disk. Additionally, some applications require swap even if there's available memory.</p>

Linux determines whether to use swap with the swappiness value. This value helps the system decide how much swap to use at any given time.

To check the swappiness value, you can use the command:

`   sysctl vm.swappiness`

### Output of sysctl vm.swappiness command

```bash

  user@machineHost:~$ sysctl vm.swappiness
  vm.swappiness = 60
 
```

<p style='text-align: justify;'>Lowering the swappiness value means that the system is less likely to use swap. However, setting it to zero doesn't guarantee that the swap won't be used; instead, it indicates that the system aggressively avoids using the swap unless necessary.</p>

There isn't a universal value for setting swappiness, it varies depending on the server and its workload.

## Conclusion

<p style='text-align: justify;'>In conclusion, the comprehension of memory and swap usage is deemed paramount for the optimization of Linux system performance. By understanding memory management techniques and understanding the role of swap, efficient allocation of resources can be ensured, and system responsiveness </p>

## Question

So, do you prefer using swap memory in your Linux distro, or do you opt to run without it?
