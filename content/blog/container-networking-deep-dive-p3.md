---
title: "Container Networking Deep Dive - Part 3"
date: 2022-11-21
draft: false
featured: true
weight: 1
---

In part 3 of this series, we will see how containers running on the host communicates with the outside world i.e., the internet

> **Note**: This article is continuation of [part 2](/blog/container-networking-deep-dive-p2/), We recommend you to first go through
part 2 and then come back to this.

# Topics to be covered
1. Try to connect containers to the internet
2. We will understand about NAT, ip forwarding and iptables
3. Configure ip forwarding and iptables rules to connect containers to the internet

## Try to connect containers to the internet

In [part 2](/blog/container-networking-deep-dive-p2/), we had multiple containers running which were able to communicate with
each other and the host as shown below.
![Multiple container attached to linux bridge](/images/blog/container-networking-deep-dive-p2/containers-attached-to-bridge.png)

But when we try to connect containers to the internet, it was unsuccessful.
![Ping internet](/images/blog/container-networking-deep-dive-p2/ping-internet.png)

What exactly is happening and what could be the reason that containers are not able to connect to the internet?

We know that for every request we send to the internet, the destination server sends back response in order for the
ping to be successful. In this case, the destination server is not able to send packets back to the containers as the
container's ip address is private. Our containers are assigned private IPs in the range 172.16.0.0/24. A lot of devices or 
the containers in this world can have this ip address range. Then how will the destination server know to whom to send
the response back. This is where network address translation(NAT) and iptables comes to help.

## NAT and iptables

In NAT, any packets originated from the containers, and going to the external network, the packets source ip is replaced by 
the host's external interface address. The host also keep track of this, and on arrival it will be restoring the ip address
before forwarding the packet to the containers. This can be achieved by adding a simple rule in the nat table.

## Configure ip forwarding and iptables rules to connect containers to the internet

```shell
iptables -t nat -A POSTROUTING -s 172.16.0.0/24 -j MASQUERADE
```
This command means that we are adding a new rule to the `nat` table of the `POSTROUTING` chain to `MASQUERADE` all the
packets whose source is 172.16.0.0/24 network.

> `POSTROUTING` means right before leaving the interface.  

> `MASQUERADE` allows you to translate your private ip addresses with a single external ip address. In our case, we
> replaced containers private ip address with the host's external interface address.

You can run `iptables -t nat -L` to list the nat table rules. You can see a new rule is added in the nat table 
after you run the above postrouting masquerade command.
![Postrouting masquerade](/images/blog/container-networking-deep-dive-p3/masquerde-command-terminal.png)

Before you try to ping internet from the containers, we need to enable ip forwarding. By default, the ip forwarding is
disabled in Linux, if any incoming network packet arrives at one interface which is not meant for the system itself will be
dropped. Enabling ip forwarding will allow the incoming packet meant to be passed on to the another network to be accepted and
then forwards it accordingly.

```shell
# To see the ip forwarding status
cat /proc/sys/net/ipv4/ip_forward

# 0 means it's disabled. Setting it to 1 would mean it's enabled
sysctl -w net.ipv4.ip_forward=1
```

Now once again it's time to test our containers' connectivity with the internet. Let's do it...

Run `ip netns exec container1 ping 1.1.1.1`
![Ping internet from container1 success](/images/blog/container-networking-deep-dive-p3/ping-internet-success.png)

**CONGRATULATIONS, YOU DID IT !! 🥳🎉**

## Conclusion

In this, you learned how you can configure iptables to allow containers to connect with the internet.

**A big shoutout to you for making it this far in the journey of learning about container networking.**

## Other related articles
- [Container Networking Deep Dive - Part 1](/blog/container-networking-deep-dive-p1/)
- [Container Networking Deep Dive - Part 2](/blog/container-networking-deep-dive-p2/)