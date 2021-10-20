---
title: "Kubernetes for Developers - Part 1: Introduction to Kubernetes"
tags:
  - Kubernetes
---

This series is a practical introduction to Kubernetes and Amazon's EKS. I come from the developer side of things, rather than the ops side of things, so this is written from that perspective. In this first tutorial, we're going to discuss some basic Kubernetes concepts and play around with a local cluster running in a VM. This tutorial assumes you are already somewhat familiar with Docker - if you know how to write a Dockerfile, and run an application in Docker, (or at least understand what those concepts are) you should be good.

<!--more-->

## Scheduling Workloads

Kubernetes (often abbreviated "K8s", in the same way that "internationalization" is often abbreviated to "i18n" - developers are a lazy bunch), is a system that lets you run "workloads" (i.e. docker containers) on a cluster of nodes. The act of deciding what node to run a workload on is known as "scheduling" a workload. What Kubernetes provides you is a standardized framework for creating workloads, for service discovery (figuring out how to connect to those workloads internal), for exposing services to the Internet, and provides a powerful API for inspecting what workloads are running and interacting with them.

The Kubernetes mantra is "cattle, not pets". As a rule (with some exceptions we'll talk about in future tutorials), you don't care which nodes a given workload is scheduled on. If a workload dies, then we simply dispose of it and create a new copy. If a Kubernetes node needs to be upgraded, we create a new node with the upgrade, then simply dispose of the old node, and let Kubernetes handle moving workloads off the old node to the new one. Kubernetes provides lots of functionality to make sure this sort of thing goes smoothly and the way you want it to, but without having to kill off individual workloads one-by-one - Kubernetes will take care of moving workloads around in a graceful manner.

## Creating a Cluster

We can't do much with Kubernetes without a cluster of nodes to run containers on, so let's create a cluster. There are a few ways you can do this for free. For this tutorial, we're going to use `minikube`, which will set up an entire Kubernetes cluster in a VM on your local machine. This is a great way to play around with Kubernetes. (I'd also point you towards "[k3s](https://k3s.io/)" which is a great solution for running a small Kubernetes cluster on your own hardware, such as on a Raspberry Pi.)

To get minikube running, you need a few tools installed first; `kubectl` to talk to Kubernetes, and of course `minikube`. If you have Docker installed, you may already have `kubectl` installed, as it often comes bundled. On a Mac, if you're using brew, you can install both of these and start minikube with:

```sh
$ brew install kubectl minikube
$ minikube start --vm-driver=hyperkit
```

If you're on another platform, you'll need to install a hypervisor such as VirtualBox first. You can get detailed instructions [from the Kubernetes documentation](https://v1-18.docs.kubernetes.io/docs/tasks/tools/install-minikube/).

Once minikube is installed and running, you can run `kubectl` to interact with your Kubernetes cluster. For example, you can list all the nodes in your cluster with `kubectl get nodes`:

```sh
$ kubectl get nodes
NAME       STATUS   ROLES                  AGE    VERSION
minikube   Ready    control-plane,master   2m7s   v1.22.2
```

You can stop your minikube VM with `minikube stop`, or delete the VM entirely with `minikube delete`.

## Pods

The basic workload unit in Kubernetes is a Pod - you can think of a Pod like a running Docker container. (That's a little bit of a lie, but it's close enough for this tutorial.) You can create Pods directly in Kubernetes if you wish, but you rarely would - instead you would create a Deployment or a StatefulSet, which would in turn create Pods, and also take care of restarting those pods if they get destroyed, manage upgrading Pods, and so on.

But, let's create a pod, just to get some experience with `kubectl`. There are two ways we can go about doing this. We can create a pod directly from kubectl with `kubectl run`:

```sh
$ kubectl run my-pod --image=alexwhen/docker-2048:latest
pod/my-pod created
```

This is very similar to the `docker run` command - it starts up a pod for us. There are times when this is handy, but creating resources manually is error prone and not reproducible. More typically what we do with Kubernetes is create a YAML file that describes what we want deployed, then run `kubectl apply` to "apply" that YAML file - to create resources that are in the YAML file but not on the node, or to update resources that already exist. This way we can commit our YAML file to git or some other source control, and we have a reproducible set of instructions for what we want to deploy. Here's a sample YAML file for creating a Pod:

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod-2
  labels:
    env: test
spec:
  containers:
    - image: "alexwhen/docker-2048:latest"
      name: docker-2048
      ports:
        - name: http
          containerPort: 80
```

All YAML descriptors in Kubernetes have an `apiVersion`, `kind`, `metadata`, and `spec` section.

- The `apiVersion` and `kind` here tell us we want to create a "Pod"; each kind of resource in Kubernetes is associated with a particular apiVersion.
- `metadata` contains data about this resource - in the case the name of the pod, and some labels.
- `spec` describes the details of what we're trying to create - here we specify the pod has one container, where to find the image for the container, and a list of ports that the container exposes.

In the "metadata" section, "labels" are free-form metadata you can attach to any object in Kubernetes - you can set whatever labels you like on a resource. You might specify an "app: front-end" to specify this is the front-end part of your application, or you might specify that this deployment is part of "env: prod". It's entirely up to you. You can use "selectors" in Kubernetes to pick a subset of resources - to find all the pods that are part of "env: prod" for example. Frequently the metadata section will also contain "annotations" - we'll talk more about those in the [next part of this tutorial](http://www.thedreaming.org/2021/10/21/kubernetes-for-developers-part-2/) when we talk about "Ingress".

Once we write this to `pod.yaml`, we can create this pod with:

```sh
$ kubectl apply -f pod.yaml
pod/my-pod-2 created
```

We can see what pods exist with:

```sh
$ kubectl get pods
NAME       READY   STATUS    RESTARTS   AGE
my-pod     1/1     Running   0          5m26s
my-pod-2   1/1     Running   0          16s
```

You may see your pod is in the "ContainerCreating" state for a little bit while Kubernetes picks a node to run it on, downloads the Docker image, and starts the pod. If you run `kubectl get pods --watch` it will print a line every time a pod's status changes, and you can see your pod get updated in realtime. We can see detailed information about a specific pod by name, including a little bit of it's history, with:

```sh
$ kubectl describe pod my-pod
```

Or get a YAML description of the pod via:

```sh
$ kubectl get pod -o json my-pod
```

Note that the YAML description of a pod includes all the things we added in our YAML file, along with some defaults we didn't set, and some current status from Kubernetes. We can destroy pods, either destroying the pod we created manually:

```sh
$ kubectl delete pod my-pod
pod "my-pod" deleted
```

Or from the YAML file:

```sh
$ kubectl delete -f pod.yaml
pod "my-pod-2" deleted
```

But you'll notice if we delete a pod, it doesn't get recreated. Isn't this is the whole point of Kubernetes? It's supposed to create and manage pods for us! We'll see how to get Kubernetes to create a collection of pods for us by creating a "Deployment" in just a moment.

## kubectl - a RESTful API

A little bit of an aside, but you'll notice right away that kubectl is very "REST-like". You can `get`/`describe` pods, `delete` pods, and `apply` changes. You may notice an easy 1:1 mapping between these and the GET, DELETE, POST, and PATCH commands you'd find in REST, and in fact the Kubernetes API is entirely REST based under-the-hood.

These "verbs" - get, describe, delete - apply to pods and to a number of other "nouns" or "resources" in Kubernetes. You can get a full list of available resource types with `kubectl api-resources` - if you give it a try, it's a long list. Kubernetes is extensible, so if there's a resource that's missing from that list, you can even add your own through "operators". The learning curve in Kubernetes is largely about learning what these various resources are and how to configure them.

`kubectl` comes with a handy help function here in the form of `kubectl explain`. If you forget what a pod is, you can run `kubectl explain pod`, and it will give you a description of the pod, and all the fields that can appear on a pod and what they mean. If you want to know what the "image" field is for, you can run `kubectl explain pod.spec.containers.image`, and it will tell you all about that field.

## Deployments

Back to pods. Let's say you want to run a stateless service of some sort - an API layer running on node.js or Java, or perhaps a web server. Describing these as "stateless" just means we can run one pod by itself, or ten pods in parallel. They can run on different machines (so long as they have some kind of load balancer in front of them). If one dies, we can replace it with another pod, possibly running on a different node. Kubernetes manages this kind of workload with a "deployment".

Once we launch a deployment, Kubernetes takes care of making sure the specified number of pods are running, restarts pods if they fail, reschedules pods to a new node if a node fails. We can tell Kubernetes how much CPU and RAM a pod needs at minimum and how much it can burst to, and Kubernetes will make sure we don't put too many instances of a service on a single node, and will limit the CPU and RAM used. Kubernetes will even take care of rolling upgrades when we want to deploy a new version of a workload.  We're getting ahead of ourselves though. Let's describe a simple deployment in a YAML file:

```yaml
# 2048.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: game
  labels:
    app: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: game
  template:
    metadata:
      labels:
        app: game
    spec:
      containers:
        - name: web
          image: alexwhen/docker-2048:latest
          ports:
            - name: http
              containerPort: 80
```

I know what you're thinking; "What is with this giant wall of YAML? Am I sure I want to learn Kubernetes? What life decisions lad me to this point? Maybe I should give up on DevOps and open a gluten free bakery..."

This is definitely intimidating the first time you see it, but let's go through this piece by piece. The top level of any YAML document in Kubernetes looks much the same. Just like with our Pod above, the combination of `apiVersion` and `kind` tells Kubernetes that we're trying to create a Deployment. Unlike Pod, which was part of the "v1" apiVersion, a Deployment is part of "apps/v1". `metadata` here is just like it was for the pod, but here it gives a name and labels for the deployment itself.  `spec` is the part of any Kubernetes document that differs, depending on what we're creating.

The keen-eyed amongst you will have noticed that we have two `metadata` sections - one at the top level, and one inside `spec.template`. The `template` describes the YAML for each pod in this deployment, so the metadata inside the template is metadata we're going to apply to each pod (as opposed to the metadata at the top level, which is for the actual "Deployment" object). Here, each pod will get a `app: game` label. The template also specifies the `spec` for each pod, describing what image to fetch, what ports to expose on each pod, and so on.

`spec.replicas` tells us how many copies of this pod we want to create. `spec.selector` is a "label selector", which tells us how to figure out if the pods for this deployment are already running - the selector says we're going to select pods that have the label `app: game`, so if there are already two pods running with those labels, and they're configured to match the spec, then we don't have to change them. In any deployment you write, `spec.selector` must be a subset of `spec.template.metadata`. Often you apply the same labels to the deployment that you do to the pod, so often these labels are repeated three times in this file.

If we put this all in a file called "2048.yaml", and run `kubectl apply -f 2048.yaml`, we should see a single Deployment, and two Pods get created (and also a "ReplicaSet" - this is responsible for making sure the correct number of pods are running):

```sh
$ kubectl get deployments
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
game   2/2     2            2           6s

$ kubectl get replicasets
NAME              DESIRED   CURRENT   READY   AGE
game-6bcc6885f8   2         2         2       10s

$ kubectl get pods
NAME                    READY   STATUS    RESTARTS   AGE
game-6bcc6885f8-fplx6   1/1     Running   0          14s
game-6bcc6885f8-x6rnr   1/1     Running   0          14s
```

Now, let's try deleting one of these pods:

```sh
$ kubectl delete pod game-6bcc6885f8-fplx6

$ kubectl get pods
NAME                    READY   STATUS    RESTARTS   AGE
game-6bcc6885f8-q239n   1/1     Running   0          5s
game-6bcc6885f8-x6rnr   1/1     Running   0          1m10s
```

We deleted the pod, and Kubernetes created a new one for us, since we told it we always want there to be two!

Note that if a new version of our application comes out and we want to upgrade, all we need to do is update the `image` in the above YAML file and apply it again - Kubernetes will perform a rolling upgrade, adding new pods running the new version, then destroying pods running the old version, until we're back at two pods all running the new version. If you don't want a rolling update and instead want to terminate all the old pods and then bring up new pods, you can do that too, by setting [`spec.strategy.type` to "Recreate"](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy) - this will cause all the old pods to be terminated and then new pods to be created to replace them. "Recreate" will will incur a brief service outage, since there will be a very brief time when your old application has been terminated, and your new application is still starting up.

Now we have pods running, and they have a web server that each of them is exposing on their own port 80. How do we access that web server? We can access an individual pod using the `kubernetes port-forward` command:

```sh
$ kubectl port-forward game-6bcc6885f8-q239n 3000:80
Forwarding from 127.0.0.1:3000 -> 80
Forwarding from [::1]:3000 -> 80
```

Now if you open up a web browser and visit `http://localhost:3000`, you should see the game being served from the pod. But, this isn't very practical - I want to load balance traffic between these two pods. How do I do that, and how do I either find this pod from another pod inside Kubernetes, or access it from the Internet?

## StatefulSets and DaemonSets

I wanted to briefly mention StatefulSets and DaemonSets here, although we will look into these in greater detail in another article.

Deployments are appropriate for stateless services like backend services, but they're not appropriate for all services. If you wanted to run a MongoDB database in a replica set, for example, you'd always want exactly the same number of pods running at all times. You'd want each pod to have some kind of "volume" to read and write data to, and that volume would have to follow the pod around from node to node if the workload is rescheduled. The resource you'd want to create in this situation is called a "StatefulSet" - every pod in a StatefulSet gets a unique name (e.g. "postgres-1", "postgres-2", ...), and you can create a "PersistentVolumeClaim" for each pod in the set.

The other, less often used, resource is the DaemonSet - if you create a DaemonSet, then Kubernetes will ensure there is one pod running for the DaemonSet on every node in your cluster. These are useful for collecting metrics about nodes in the cluster. `kube-proxy`, a service which provides simple TCP and UDP forwarding within the cluster, runs as a DaemonSet on each node.

## Services

A `Service` is another kind of Kubernetes resource - as the name implies, it describes the actual service that a group of pods exposes. It's rare you create a deployment without also creating a service. Let's update our 2048.yaml file so it looks like this:

```yaml
# 2048.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: game
  labels:
    app: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: game
  template:
    metadata:
      labels:
        app: game
    spec:
      containers:
        - name: web
          image: alexwhen/docker-2048:latest
          ports:
            - name: http
              containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: gameservice
spec:
  selector:
    app: game
  type: ClusterIP
  ports:
    - protocol: TCP
      port: 80
      targetPort: http
      name: http
```

And then run `kubectl apply -f 2048.yaml` again. This will create a new "service" object which describes how to connect to our service:

```sh
$ kubectl get service gameservice
NAME          TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
gameservice   ClusterIP   10.100.212.52   <none>        80/TCP    4s
```

Looking at the `spec`, again we see a `selector` describing which pods we want this service to connect to. The `type: ClusterIP` means that this service will be assigned an IP address internally - anyone who connects to port 80 of this service will have their connection sent to one of the pods running this service, to the "http" port (which we defined above in the deployment).

We can connect to this service in a couple of ways - first we can use `kubectl port-forward svc/gameservice 3000:http`, just like we did above, but now when we connect to `http://localhost:3000`, our connection will be forwarded to one of the pods at random.

From inside the cluster, we can find this service with a DNS query. Let's get a shell in an ubuntu image running inside the cluster, and see if we can find the service. First we'll install `curl`, and then we'll use `curl` to try to grab the HTML contents of the web page:

```sh
$ kubectl run -it --rm --image=ubuntu:latest -- bash
root@bash:/# apt-get update && \
  apt-get install -y -qq curl
root@bash:/# curl http://gameservice/

  # or

root@bash:/# curl http://gameservice.default.svc.cluster.local/
```

This provides us with a powerful way to link our applications together - each application can find services it wants to interact with just by looking up the service via DNS. Note that we can connect to the service via a fully qualified domain name like "gameservice.default.svc.cluster.local" ("default" here is the namespace we are currently running it - we'll talk more about namespaces in [part two](http://www.thedreaming.org/2021/10/21/kubernetes-for-developers-part-2/)), or we can just use the "gameservice" domain name to find the one running in the local namespace. This works because Kubernetes automatically configures a search path in /etc/resolv.conf.

We can also create services for resources that aren't in Kubernetes:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: prod
spec:
  type: ExternalName
  externalName: postgres.example.com
```

This is called an "external service", and here if we try to look up the DNS entry for "postgres", we'll get back a CNAME record for "postgres.example.com".

## Logs and Shells

If our pod's container writes output to stdout, sometimes it's handy to see the output. Much like the `docker logs` command, kubectl provides a `kubectl logs` command that will show logs for a pod:

```sh
kubectl logs [podname]
```

Our "2048" pods don't print any output, so the logs are empty.  Let's start a redis container so we can see some logs:

```sh
$ kubectl run redis --image=redis:latest
pod/redis created

$ kubectl logs redis
1:C 20 Oct 2021 19:57:03.787 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
1:C 20 Oct 2021 19:57:03.787 # Redis version=6.2.6, bits=64, commit=00000000, modified=0, pid=1, just started
1:C 20 Oct 2021 19:57:03.787 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
1:M 20 Oct 2021 19:57:03.788 * monotonic clock: POSIX clock_gettime
...
```

If we want to watch logs in realtime, then similar to the `tail -f` command, we can use the "-f" flag to tail the logs.  The "--since" will limit the output to recent output.  So this command will print all logs from the last 10 minutes, then keep showing logs as they come in:

```sh
$ kubectl logs -f --since=10m redis
...
```

The `--previous` flag is also handy - this shows logs from a previous instance of pod.  Handy when a pod crashes or restarts, and you want to see the error that caused it to die.  "fluentd" is a popular log aggregator that can fetch logs from all your deployments and collect them together for you.

One last thing that's handy for troubleshooting an existing pod; you can get a shell on an existing pod with `kubectl exec`:

```sh
$ kubectl exec -it redis -- sh
#
```

## Conclusion

That's it for part one of this tutorial - we learned about kubectl, we learned how to create pods, deployments, and services. We learned how to get a shell inside the cluster, and we learned about service discovery through DNS. In [part two](http://www.thedreaming.org/2021/10/21/kubernetes-for-developers-part-2/), we'll look at how to create a cluster in AWS using `eksctl` and how to forward traffic from the Internet to one or more of our services via an "Ingress".
