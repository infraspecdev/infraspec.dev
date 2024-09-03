---
title: "Container Networking Deep Dive - Part 1"
authorId: "arihant"
date: 2022-11-19
draft: false
featured: true
weight: 1
sitemap:
   changefreq: 'monthly'
   priority: 0.8
---

In part 1 of this series, we will demystify how a container communicates with the host and vice versa.

## Topics to be covered

1. Isolating containers with network namespaces.
2. Constituent networking elements like network interface, veth pair, and routing rules.
3. Set up container networking from scratch using Linux commands.

## Prerequisites

In this article, we are using the vagrant ubuntu/jammy64 virtual machine. Make sure you have the [vagrant](https://developer.hashicorp.com/vagrant/downloads) installed.
\
Here is the [link](https://github.com/arihant-2310/Container-Networking-Deep-Dive/blob/main/1-single-network-namespace/Vagrantfile) to the vagrant file to set up the VM.

To start the VM, go to the directory where you downloaded the vagrant file and then execute the below commands:

```shell
#To start the VM
vagrant up

#To SSH into the VM
vagrant ssh
```

> **Note:** All the commands in the following articles are run with root privileges. Either you can add `sudo` before each command or switch to different a user with root
> privileges by running `sudo su`

## Isolating containers with network namespaces

Linux [namespaces](https://www.nginx.com/blog/what-are-namespaces-cgroups-how-do-they-work/) are one of the technologies that make up containers and allow process isolation.
We will be using a network namespace to isolate the containers.

A network namespace is logically another copy of a network stack, with its routes, firewall rules, and network devices.
![Network namespaces with their network stack](/images/blog/container-networking-deep-dive-p1/network-namespace.png)

Instead of creating fully-isolated containers, we'd rather restrict the scope to only the network stack.

## Container networking constituent elements

### 1. Network Interface

![Host with a network interface to connect to public/private network](/images/blog/container-networking-deep-dive-p1/network-interface.png)
A network interface is the point of interconnection between a computer and a private or public network.

### 2. Virtual Ethernet Device (veth)

The veth devices are virtual ethernet devices. They can act as tunnels between network namespaces.
![Two namespaces connected by a veth pair](/images/blog/container-networking-deep-dive-p1/veth-pair.png)

In the above, veth1 and veth2 are the names assigned to the two connected endpoints. Packets transmitted on one device in the pair are immediately received on the other device. For e.g., if we transmit packets from `veth1`, they will be immediately received on `veth2` and vice versa, thus allowing communication between network namespaces `ns1` and `ns2`.

### 3. Routing Tables

Routing tables stores information on how packets are to be forwarded from one point to another.
![Routing table with one route entry](/images/blog/container-networking-deep-dive-p1/routing-table.png)

The entry in the above routing table means that any packet destined for the `102.26.67.0` network with a netmask of `255.255.255.0` has to be transmitted via the gateway `10.0.0.2` and goes out through the interface `eth0`.

## Let's set up container networking from scratch with Linux commands

Hope you have set up the fresh VM and ssh into it ✌️.

1. To see the host interfaces and devices' IP addresses, run `ip addr`
![host device IP addresses](/images/blog/container-networking-deep-dive-p1/ip-addr.png)
![Host machine with network interface named enp0s8](/images/blog/container-networking-deep-dive-p1/host-machine-interface.png)
   Initially, our host machine is configured with a network interface of IP address 10.0.0.10. The interface name and IP can be different for your case.
2. To create a network namespace, run `ip netns add container1`  
![Host machine with a single container](/images/blog/container-networking-deep-dive-p1/host-machine-single-container.png)
3. To list the network namespaces, run `ip netns`. It will show container1 as a network namespace in the host.
4. Now we need a way for the host and `container1` to communicate with each other. We already learned that a veth pair can be used to enable communication between two namespaces. The two namespaces are the root namespace (i.e., the host) and the `container1` namespace.

   To create a veth pair, run `ip link add veth1 type veth peer name ceth1`
   ![a veth pair with one end named veth1 and peer name ceth1](/images/blog/container-networking-deep-dive-p1/veth-cable.png)

5. To see the veth pair created, run `ip link`.

   You will see veth1 and ceth1 are created in the host, and they are in a down state.
   ![veth pair created in the host](/images/blog/container-networking-deep-dive-p1/veth-pair-bash.png)

6. Now we need to connect one end of the veth pair to container1 to allow communication between the host and container1.
   To set ceth1 inside container1, run `ip link set ceth1 netns container1`
![container-with-veth-pair](/images/blog/container-networking-deep-dive-p1/container-with-veth-pair.png)

7. To list the interfaces inside `container1`

   ```shell
   #ip netns exec <network namespace name> <command>
   ip netns exec container1 ip link
   ```

   Below you can see the ceth1 interface is set inside container1
![list-interfaces-inside-container](/images/blog/container-networking-deep-dive-p1/list-interfaces-inside-container.png)

8. By default, both ends of the veth pair were down. To enable

   ```shell
   #To set veth1 up
   ip link set veth1 up
   
   #To set ceth1 up
   ip netns exec container1 ip link set ceth1 up
   ```

9. To send packets to container1, we need to assign IP address to ceth1 interface inside `container1`

   ```shell
   ip netns exec container1 ip addr add 172.16.0.2/24 dev ceth1
   ```

   You can check if the IP address was assigned to the `ceth1` interface `ip netns exec container1 ip addr`. When you assigned an IP address to the ceth1 interface, a route was dynamically added inside the `container1` namespace. To check the routes inside `container1`, `ip netns exec container1 ip route`.
   ![route inside container](/images/blog/container-networking-deep-dive-p1/route-inside-container.png)
   This route means that any packet destined for 172.16.0.0/24 will be sent via the ceth1 interface.

10. To ping container1 from the host, run `ping 172.16.0.2`
    The ping hangs infinitely because the host has no route to send packets to container IP `172.16.0.2`.
    ![ping hang](/images/blog/container-networking-deep-dive-p1/ping-hang.png)

11. To send all packets destined for 172.16.0.0/24 via veth1 in the host, run `ip route add 172.16.0.0/24 dev veth1`

12. Ping the container1 again from the host
![ping-unreachable](/images/blog/container-networking-deep-dive-p1/ping-unreachable.png)  
The ping is still unsuccessful! Take a minute thought to understand why 🤔  
\
Okay, if you got the reason why ping was unsuccessful, Congrats 🥂 👏, else I have the answer.  
\
When we send a ping request from host IP `10.0.0.10`, the container needs to send a response back to the host for the ping to be successful. Since there is no route in `container1` for sending the response back to the host, it says the destination host is unreachable.
\
Let's add a route inside `container1`.  

13. Set ceth1 as the default gateway for container1, run `ip netns exec container1 ip route add default via 172.16.0.2 dev ceth1`

14. Now if you ping the container1 again
![ping-container-success](/images/blog/container-networking-deep-dive-p1/ping-container-success.png)
The ping is successful 😃✌️

15. Let's try to ping the host from the container1
![ping host success](/images/blog/container-networking-deep-dive-p1/ping-host-success.png)
voila 🎊😃, you made it.

## The final networking setup for a single container running on a host machine

![single-network-namespace](/images/blog/container-networking-deep-dive-p1/single-network-namespace.png)

## Conclusion

You just learned about network namespaces and about the elements that constitute container networking. You also set up the container networking from scratch using Linux commands. Both `container1` and the host can send packets to each other.

In [part 2](/blog/container-networking-deep-dive-p2/), we will see how we can have multiple containers running on a single host communicate with each other.

## Other related articles

- [Container Networking Deep Dive - Part 2](/blog/container-networking-deep-dive-p2/)
- [Container Networking Deep Dive - Part 3](/blog/container-networking-deep-dive-p3/)
