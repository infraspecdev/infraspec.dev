---
title: "Setting up Ingress on EKS"
authorIds: ["rajat"]
date: 2022-11-30
draft: false
featured: true
weight: 1
---

> **Note**: Everything here applies to [Amazon Elastic Kubernetes Service (EKS)](https://aws.amazon.com/eks/). If you are running on another cloud, on-prem, with minikube, or something else, these will be slightly different.

* * * * *

## What is an Ingress?

An Ingress in Kubernetes provides external access to your Kubernetes services. You configure access by creating a collection of routing rules that define which requests reach which services.

This lets you consolidate your routing rules into a single resource. For example, you might want to send requests to [mydomain.com/](http://example.com/api/v1)api1 to the api1 service, and requests to [mydomain.com/](http://example.com/api/v2)api2 to the api2 service. With an Ingress, you can easily set this up without creating a bunch of LoadBalancers or exposing each service on the Node.

*An Ingress provides the following:*

- Externally reachable URLs for applications deployed in Kubernetes clusters
- Name-based virtual host and URI-based routing support
- Load Balancing rules and traffic, as well as SSL termination

## Kubernetes Service types -- an overview

### ClusterIP

A ClusterIP service is the default service. It gives you a service inside your cluster that other apps inside your cluster can access. There is no external access.

<p align="center">
  <img width="500px" src="/images/blog/setting-up-ingress-on-eks/cluster-ip.png" alt="ClusterIP">
</p>

*The YAML for ClusterIP service looks like this:*

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namesapce: default
spec:
  selector:
    app: nginx
  type: ClusterIP
  ports:
  - name: http
    port: 80
    targetPort: 80
    protocol: TCP

```

Create the service:

```bash
$ kubectl apply -f nginx-svc.yaml
service/nginx-service created

```

Check it:

```bash
$ kubectl get svc nginx-serice
NAME            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
nginx-service   ClusterIP   172.20.54.138   <none>        80/TCP    38s

```

### NodePort

A NodePort service is the most primitive way to get external traffic directly to your service. NodePort, as the name implies, opens a specific port on all the Nodes (the VMs), and any traffic that is sent to this port is forwarded to the service.

When we create a Service of type NodePort, Kubernetes gives us a nodePort value. Then the Service is accessible by using the IP address of any node along with the nodePort value. In other words, when a user sets the Service type field to NodePort, the Kubernetes master allocates a static port from a range, and each Node will proxy that port (the same port number on every Node) into our Service.

<p align="center">
  <img width="500px" src="/images/blog/setting-up-ingress-on-eks/node-port.png" alt="NodePort">
</p>

*The YAML for NodePort service looks like this:*

```bash
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: default
spec:
  selector:
    app: nginx
  type: NodePort
  ports:
  - name: http
    port: 80
    targetPort: 80
    nodePort: 30036
    protocol: TCP

```

The `nodePort` parameter here is optional, added here just for an example. Without it, Kubernetes will allocate a port from the 30000-32767 ports range.

Create the service:

```bash
$ kubectl apply -f nginx-svc.yaml
service/nginx-service created

```

Check it:

```bash
$ kubectl get svc nginx-service
NAME            TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
nginx-service   NodePort   172.20.54.138   <none>        80:30036/TCP   40s

```

Please keep in mind that it will work as long as the node is reachable via its IP addresses. In most cases, the worker nodes reside in our private network(like office networks or private VPC). In such cases, we can not access the `NodePort` service from the Internet.

### LoadBalancer

A LoadBalancer service is the standard way to expose a service to the internet.

In case of AWS -- will create an AWS Load Balancer, by default Classic type, which will proxy traffic to all ЕС2 instances of the TargetGroup tied to this Load Balancer, and then via  `NodePort` Service -- to all the pods.

`LoadBalancer` type provides a Public IP address or DNS name to which the external users can connect. The traffic flows from the LoadBalancer to a mapped service on a designated port, which eventually forwards it to the healthy pods. Note that LoadBalancers doesn't have a direct mapping to the pods.

<p align="center">
  <img width="400px" src="/images/blog/setting-up-ingress-on-eks/load-balancer.png" alt="LoadBalancer">
</p>

*The YAML for LoadBalancer service looks this:*

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: default
spec:
  selector:
    app: nginx
  type: LoadBalancer
  ports:
    - name: http
      port: 80
```

Apply it:

```yaml
$ kubectl apply -f nginx-svc.yaml
service/nginx-service created

```

Check:

```yaml
$ kubectl get svc nginx-service
NAME            TYPE           CLUSTER-IP      EXTERNAL-IP                                                              PORT(S)        AGE
nginx-service   LoadBalancer   172.20.54.138   ac8415de24f6c4db9b5019f789792e45-443260761.ap-south-1.elb.amazonaws.com   80:30968/TCP   1h

```

So, the *LoadBalancer* service type:

- will provide external access to pods
- will provide a basic load-balancing to pods on different EC2
- will give an ability to terminate SSL/TLS sessions
- doesn't support level-7 routing

*The big downside is that each service you expose with a LoadBalancer will get its own IP address, and you have to pay for a LoadBalancer per exposed service, which can get expensive!*

## Ingress

Unlike all the above examples, Ingress is actually NOT a dedicated Service. Instead, it sits in front of multiple services and act as a "smart router" or entrypoint into your cluster.

It just describes a set of rules for the Kubernetes Ingress Controller to create a Load Balancer, its Listeners, and routing rules for them.

An Ingress does not expose arbitrary ports or protocols. Exposing services other than HTTP and HTTPS to the internet typically uses a service of type [Service.Type=NodePort](https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport) or [Service.Type=LoadBalancer](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer).

<p align="center">
  <img width="500px" src="/images/blog/setting-up-ingress-on-eks/ingress.png" alt="Ingress">
</p>

<p align="center">
  <img width="700px" src="/images/blog/setting-up-ingress-on-eks/ingress-managed-lb.png" alt="Ingress managed LB">
</p>

_image source: https://kubernetes.io/docs/concepts/services-networking/ingress/_

In order for the Ingress resource to work, the cluster must have an ingress controller running. Only creating an Ingress resource has no effect.

An [Ingress controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers) is responsible for fulfilling the Ingress, usually with a load balancer, though it may also configure your edge router or additional frontends to help handle the traffic.

*In this example, we'll use the Nginx Ingress Controller:*

Install:

```bash
$ kubectl apply -f <https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.3.1/deploy/static/provider/cloud/deploy.yaml>

```

Output:

```bash
namespace/ingress-nginx created
serviceaccount/ingress-nginx created
clusterrole.rbac.authorization.k8s.io/ingress-nginx created
clusterrolebinding.rbac.authorization.k8s.io/ingress-nginx created
role.rbac.authorization.k8s.io/ingress-nginx created
rolebinding.rbac.authorization.k8s.io/ingress-nginx created
service/ingress-nginx-controller-admission created
service/ingress-nginx-controller created
deployment.apps/ingress-nginx-controller created
validatingwebhookconfiguration.admissionregistration.k8s.io/ingress-nginx-admission created
serviceaccount/ingress-nginx-admission created
clusterrole.rbac.authorization.k8s.io/ingress-nginx-admission created
role.rbac.authorization.k8s.io/ingress-nginx-admission created
rolebinding.rbac.authorization.k8s.io/ingress-nginx-admission created
job.batch/ingress-nginx-admission-create created
job.batch/ingress-nginx-admission-patch created

```

**Pre-flight check**

A few pods should start in the `ingress-nginx` namespace:

```bash
$ kubectl get pods --namespace=ingress-nginx

```

After a while, they should all be running. The following command will wait for the ingress controller pod to be up, running, and ready:

```bash
$ kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

```

This has set up the Nginx Ingress Controller. Now, we can create Ingress resources in our Kubernetes cluster and route external requests to our services. Let's do that.

### Creating a Kubernetes Ingress

First, let's create two services to demonstrate how the Ingress routes our request. We'll run two web applications that output a slightly different response.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: apple-app
  labels:
    app: apple
spec:
  containers:
    - name: apple-app
      image: hashicorp/http-echo
      args:
        - "-text=apple"

---

apiVersion: v1
kind: Service
metadata:
  name: apple-service
spec:
  selector:
    app: apple
  type: NodePort
  ports:
    - port: 5678 # Default port for image

```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: banana-app
  labels:
    app: banana
spec:
  containers:
    - name: banana-app
      image: hashicorp/http-echo
      args:
        - "-text=banana"

---

apiVersion: v1
kind: Service
metadata:
  name: banana-service
spec:
  selector:
    app: banana
  type: NodePort
  ports:
    - port: 5678 # Default port for image

```

Create the resources

```bash
$ kubectl apply -f apple.yaml
$ kubectl apply -f banana.yaml

```

Now, declare an Ingress to route requests to `/apple` to the first service, and requests to `/banana`  to second service.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
        - path: /apple
          pathType: Prefix
          backend:
            service:
              name: apple-service
              port:
                number: 5678
        - path: /banana
          pathType: Prefix
          backend:
            service:
              name: banana-service
              port:
                number: 5678

```

Here we set two rules: if URI == */apple* or */banana*  -- then send the traffic to the *apple-service* or *banana-service* accordingly.

Deploy it:

```bash
$ kubectl apply -f ingress.yaml

```

Another example is the hostname-based routing.

*Update the manifest:*

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: apple.banana.com
    http:
      paths:
      - path: /apple
        pathType: Prefix
        backend:
          service:
            name: apple-service
            port:
              number: 5678
      - path: /banana
        pathType: Prefix
        backend:
          service:
            name: banana-service
            port:
              number: 5678

```

The Ingress controller provisions an implementation-specific load balancer that satisfies the Ingress, as long as the Services (`apple-service`, `banana-service`) exist. When it has done so, you can see the address of the load balancer at the Address field.

**Name based virtual hosting**

Name-based virtual hosts support routing HTTP traffic to multiple host names at the same IP address.

<p align="center">
  <img width="700px" src="/images/blog/setting-up-ingress-on-eks/name-based-virtual-hosting.png" alt="Name based virtual hosting">
</p>

image source: https://kubernetes.io/docs/concepts/services-networking/ingress/#name-based-virtual-hosting

The following Ingress tells the backing load balancer to route requests based on the Host header.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  rules:
  - host: apple.service.com
    http:
      paths:
      - pathType: Prefix
        path: "/"
        backend:
          service:
            name: apple-service
            port:
              number: 5678
  - host: banana.service.com
    http:
      paths:
      - pathType: Prefix
        path: "/"
        backend:
          service:
            name: banana-service
            port:
              number: 5678

```

Here we left Services without changes, but in the Rules, we set that a request to the *[apple.service.com](http://apple.service.com)* must be sent to the *apple-service* and *[banana.service.com](http://banana.service.com)* to the banana-service.

## Summary

A Kubernetes Ingress is a robust way to expose your services outside the cluster. It lets you consolidate your routing rules to a single resource, and gives you powerful options for configuring these rules.

"That's all folks!"
