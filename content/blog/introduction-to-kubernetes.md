---
title: "Introduction to Kubernetes"
date: 2022-12-20
draft: false
---
Wondering what all the buzz about Kubernetes is? Too complicated to have understood it in one shot? Let's learn together.

## What is Kubernetes?
Kubernetes (K8s) is an open-source platform that helps automate, scale, and manage containerized applications. It allows you to run and coordinate containerized applications across a cluster of machines in a distributed and fault-tolerant way, making it a powerful tool for container orchestration.

Now that we understand what Kubernetes is, let's examine the concept of a Kubernetes cluster and its key components.

A Kubernetes cluster consists of two main components: the **control plane** and **worker nodes**. A basic cluster can have just one control plane and no worker nodes. While it is possible to run workloads on the control plane, it is generally not recommended.

### Control Plane Components 

Now let's explore the control plane in more detail.

The control plane is made up of 5 components.

#### 1. kube-apiserver
   This component exposes the Kubernetes API. Using the APIs is the only way to interact with a Kubernetes cluster. It is designed to scale horizontally, allowing you to load balance traffic to the kube-apiserver by deploying multiple instances. This becomes important as kube-apiserver is the primary interface for interacting with the cluster. This component is also responsible for maintaining the desired state of the cluster.

#### 2. etcd
   etcd is used as a backing store for the Kubernetes cluster, which means that it stores the current state of the cluster which is used by the kube-apiserver to retrieve the cluster's desired state. For more information about etcd and its capabilities, refer to the official etcd [documentation](https://etcd.io/docs/).

#### 3. kube-scheduler
   The kube-scheduler determines which nodes in the cluster are suitable for hosting the pods based on the constraints and resources required by the pods. It plays a crucial role in ensuring that the pods are scheduled to run on nodes that have the necessary resources and capabilities to support them.

#### 4. kube-controller-manager
   The controller-manager is responsible for running the controller processes, which ensure that the cluster matches the desired state. These controllers watch the current state of the cluster and make any necessary adjustments to bring it into alignment with the desired state.

#### 5. cloud-controller-manager
   The cloud-controller-manager enables the cluster to interact with the underlying cloud provider's APIs to manage cloud resources. If the cluster is running locally or on-premises, it will not have a cloud controller manager running.

Though all the control plane components can be run on any machine in the cluster, for simplicity, the setup script typically starts all the control plane components on a machine where no user containers are running. For high availability, these components can be run across multiple machines, resulting in multiple control planes.

### Worker Node Components

Let's examine the components of a worker node.

Each worker node is made up of 3 components.

#### 1. kubelet
   The kubelet ensures that the containers within the pods are running as intended, and it communicates with the control plane to receive instructions on which pods to run on the node.  

#### 2. kube-proxy
   The kube-proxy is responsible for maintaining the network rules on the nodes, which enable pods to communicate with each other and with external resources over the network, both within and outside of the cluster.

#### 3. container runtime
   The container runtime takes care of starting and managing containerised applications. This allows the pod to run containers.

Node components are responsible for maintaining the running pods and providing the Kubernetes runtime environment. These components run on every node in the cluster.

