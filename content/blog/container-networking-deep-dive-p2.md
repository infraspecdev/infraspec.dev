---
title: "Container Networking Deep Dive - Part 2"
authorId: "arihant"
date: 2022-11-20
draft: false
featured: true
weight: 1
---

In part 2 of this series, we will demystify how multiple containers running on the same host communicates with the host and vice versa.

# Topics to be covered
1. Setting up multiple containers on the host
2. We will understand about Linux bridge
3. Set up container networking from scratch using Linux commands

## Setting up the multiple containers on the host

In [part 1](/blog/container-networking-deep-dive-p1/), we had single container running on the host, and it was able to communicate with the host. The
implementation of it is shown below.

![Single container host](/images/blog/container-networking-deep-dive-p2/single-container-host.png)

Now consider that we want to have one more container named container 2 as shown below. We created veth pair named veth2 and ceth2, attached
one end (ceth2) inside the container and another end (veth2) in the host. This way the container 2 will be able to talk with the host.

![Container 2](/images/blog/container-networking-deep-dive-p2/container-2.png)

But with this, how will container1 and container2 will communicate with each other? One possible way which I could think of now is to create
another veth pair and connect two containers with each other as shown below.

![Two container connected with veth pair](/images/blog/container-networking-deep-dive-p2/two-containers-with-veth-pair-connected.png)

You might now have a question is what was so difficult with this. Think of having one more container named container3, and further more containers.
Now if all the containers wants to communicate with each other, we will end up creating many veth pairs which is not the ideal way.

### How can we achieve that 🤔?. Think for few minutes  ....
\
Okay, it's the right time to introduce one more container networking constituent element.

## Linux Bridge

Linux bridge is a virtual device which allow forwarding packets to the interfaces that are connected to it.

![Linux Bridge](/images/blog/container-networking-deep-dive-p2/linux-bridge.png)

In the above diagram, we have two networks LAN1 and LAN2 connected by a bridge allowing host1 in LAN1 to send packets to host4 in LAN2.
Any devices connected with bridge can communicate with each other by forwarding packets.

In our multi container scenario, we can create a bridge and attach our containers to it that will facilitate all containers to communicate with each other.

## Continuing with setting up the multiple containers on the host

We will create a bridge and to attach containers to it, we can put one end of veth pair in container and attach other end with the bridge as shown.

![Multiple container attached to linux bridge](/images/blog/container-networking-deep-dive-p2/containers-attached-to-bridge.png)

Now inside the containers we can set bridge as the default gateway to send packets to each other and the host. If any packets are sent to the bridge,
the bridge can forward to the destination connected to it.

Now let's switch back to the terminal and write some scripts 😎

# Prerequisites
In this article also, we are using the vagrant ubuntu/jammy64 virtual machine. Make sure you have the
[vagrant](https://developer.hashicorp.com/vagrant/downloads) installed.
Here is the [link](https://github.com/arihant-2310/Container-Networking-Deep-Dive/blob/main/1-single-network-namespace/Vagrantfile) to the vagrant
file to set up the VM.

To start the VM, go to the directory where you downloaded the vagrant file and then execute the below commands:
```shell
#To start the VM
vagrant up

#To SSH into the VM
vagrant ssh
```

> **Note:** All the commands in the following articles are run with root privileges. Either you can add `sudo` before each command or switch to different a user with root
> privileges by running `sudo su`

## Set up container networking from scratch using Linux commands

In part 1 of this series, we already saw how to create network namespaces, add routes, run command inside network namespace etc. In this 
I will quickly run the commands. We will focus more on the bridge part to help you understand how containers are attached to it and how packets are sent via it.

1. To create two network namespace container1 and container2
    ```shell
    ip netns add container1
    ip netns add containe2
    ```

2. To create two veth pairs
    ```shell
    ip link add veth1 type veth peer name ceth1
    ip link add veth2 type veth peer name ceth2
    ```

3. To attach one end of each veth pair with containers
    ```shell
    ip link set ceth1 netns container1
    ip link set ceth2 netns container2
    ```

4. To enables the interfaces inside the containers
    ```shell
    ip netns exec container1 ip link set lo up
    ip netns exec container2 ip link set lo up
    ip netns exec container1 ip link set ceth1 up
    ip netns exec container2 ip link set ceth2 up
    ```

5. To assign ip address to interface inside containers
   ```shell
   ip netns exec container1 ip addr add 172.16.0.2/24 dev ceth1
   ip netns exec container2 ip addr add 172.16.0.3/24 dev ceth2
   ```

6. To create a bridge, run `ip link add br0 type bridge`  
\
This will create a bridge named br0. Run `ip link` to list the bridge.
![Bridge](/images/blog/container-networking-deep-dive-p2/terminal-bridge.png)

7. To attach the veth1 and veth2 to the bridge
   ```shell
   ip link set veth1 master br0
   ip link set veth2 master br0
   ```
   ![Veth pair attached to bridge](/images/blog/container-networking-deep-dive-p2/veth-pair-bridge-terminal.png)

8. To enable veth1, veth2 and bridge br0
   ```shell
   ip link set veth1 up
   ip link set veth2 up
   ip link set br0 up
   ```

9. To assign an ip address to the bridge, Run `ip addr add 172.16.0.1/24 dev br0`  
\
A route is added in the host, it means any traffic which is destined for 172.16.0.0/24 send it via bridge and
the source ip of the packet will the bridge ip address 172.16.0.1
![Bridge created default route](/images/blog/container-networking-deep-dive-p2/bridge-default-route.png)

10. To ping container2 form container1, Run `ip netns exec container1 ping 172.16.0.3`   
\
You can now ping container 1 and container 2 from the host, ping containers from each other. But if 
you try to ping host from any containers (`ip netns exec container1 ping 10.0.0.10`), it will fail saying the host is unreachable
because there is no route in containers saying how to forward packets destined for host.

11. To add a default route in containers    
\
For container1, Run `ip netns exec container1 ip route add default via 172.16.0.1 dev ceth1`  
For container2, Run `ip netns exec container2 ip route add default via 172.16.0.1 dev ceth2`  
\
This adds a default route in the containers saying if no route matches for the destination, use
bridge(172.16.0.1) as the default gateway to forward all packets and the out interface is ceth1 and ceth2.

12. To ping to internet from container 1, Run `ip netns exec container1 ping 1.1.1.1`  
![Ping internet](/images/blog/container-networking-deep-dive-p2/ping-internet.png)
The ping to internet did not succeed!!   
Give yourself some time to think why cannot the containers reach to the internet....  
\
**In part 3, we will see how the containers can connect to the internet.**

## Conclusion
In this, you learned how multiple containers running on a single host can communicate with each other.
You also learned about linux bridges and created a linux bridge to attach containers to it.

In part 3, we will try to resolve the connection between the containers and the internet. You will learn about
iptables, network address translation etc. 

## Other related articles
   - [Container Networking Deep Dive - Part 1](/blog/container-networking-deep-dive-p1/)
   - [Container Networking Deep Dive - Part 3](/blog/container-networking-deep-dive-p3/)
