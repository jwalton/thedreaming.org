---
title: "Kubernetes for Developers - Part 3: Volumes and Autoscaling"
tags:
  - Kubernetes
---

In [part two](/2021/10/20/kubernetes-for-developers-part-2/), we deployed a service to EKS and set up an Ingress. In this section, we're going to discuss provisioning volumes, StatefulSets, and autoscaling.

<!--more-->

## Storage

So far all of the services we've looked at have not used much storage. If we were creating pods for a database, or creating pods for a service like a video transcoder that needed a large scratch disk, we might want more than whatever disk space happens to be available on the pod's host file system. We'd also want data to persist if the pod restarts or is moved to a new node.

The solution to this is called a "volume" - volumes are very similar to their Docker namesake. The basic idea behind a volume is that a pod creates a "PersistentVolumeClaim" or "PVC", which Kubernetes will match up with a "PersistentVolume" or "PV". Volumes can either be manually created ahead of time, or can be allocated dynamically as required. A persistent volume will "follow" a Pod around from node to node (or, alternatively, Kubernetes will ensure that the Pod can only be scheduled on nodes where the volume is available).

Kubernetes doesn't have any idea what kind of hardware environment your cluster is running in, so much like how we installed the "AWS Load Balancer Controller" to handle Ingress, we're going to install a "CSI Driver" to manage volumes. The name makes you think we're going to be doing forensics and fighting criminals, but sadly it stands for "Container Storage Interface".

If you've been following this tutorial, you may notice that we created a ServiceAccount called "ebs-csi-controller-sa" back in part 2, but we haven't used it yet. Now is the time! We're going to install the [EBS CSI driver](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html) which will create and mount volumes for us:

```sh
$ helm repo add aws-ebs-csi-driver https://kubernetes-sigs.github.io/aws-ebs-csi-driver && \
  helm repo update && \
  helm upgrade -install aws-ebs-csi-driver aws-ebs-csi-driver/aws-ebs-csi-driver \
    --namespace kube-system \
    --set image.repository=602401143452.dkr.ecr.us-west-1.amazonaws.com/eks/aws-ebs-csi-driver \
    --set controller.serviceAccount.create=false \
    --set controller.serviceAccount.name=ebs-csi-controller-sa
```

Also like with the ingress, we could have multiple CSI drivers installed - there's one for AWS EFS, one for "FSx for Lustre", etc... You can also provision "local storage", where the volume is stored on the disk of the host node. When you create a PVC, you need to tell it which of these many storage mechanisms to use. But, you also don't want to specify in each and every PVC that it must use the "EBS CSI Driver" - this would make it challenging to move your application from one Kubernetes cluster to another.  Instead you want to say "I want bulk persistent storage" or "I want storage that's very fast".

Kubernetes addresses this with an extra level of indirection called a "StorageClass". You create a StorageClass that describes how to allocate resources, and then your PVCs and PVs make reference to the StorageClass. To create a StorageClass for EBS volumes we could do:

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: standard
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
```

Now any time we use the "standard" StorageClass, Kubernetes will know to use the "ebs.csi.aws.com" provisioner. If you deploy your application to some other environment, you could define a "standard" StorageClass there which does something else. Minikube has a "standard" StorageClass created for you, with a simple CSI driver that allocates local disk space. Some CSI drivers may let you specify extra values in the StorageClass via annotations - whether the disk be an old-style spinning drive or an NVMe drive, for example.

The `volumeBindingMode` here describes when to bind a volume. By default it is "Immediate", meaning that a volume will be created as soon as the PVC is created. This can cause problems though. Remember that AWS regions are divided up into Availability Zones, or AZs. In order for an EBS volume to be mounted on an EC2 instance, they have to be in the same AZ. If we use Immediate volume binding, then when the PVC is created, your EBS drive would need to be created in a particular AZ, but the associated Pod hasn't been scheduled yet, so Kubernetes won't know which AZ to create the EBS drive in. "WaitForFirstConsumer" tells Kubernetes to wait until there's someone who wants to use a PVC before trying to allocate the PV.

We can create a PVC that uses this StorageClass directly (borrowing an [example](https://github.com/kubernetes-sigs/aws-ebs-csi-driver/tree/master/examples/kubernetes/dynamic-provisioning) from the CSI driver docs):

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ebs-claim
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 4Gi
```

And then we can create a Pod that uses the PVC:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: centos
      command: ["/bin/sh"]
      args:
        ["-c", "while true; do echo $(date -u) >> /data/out.txt; sleep 5; done"]
      volumeMounts:
        - name: persistent-storage
          mountPath: /data
  volumes:
    - name: persistent-storage
      persistentVolumeClaim:
        claimName: ebs-claim
```

Most often, though, we don't create PVCs directly, just like we wouldn't create pods directly. Instead we have some stateful service that wants to store data, and so we create a "StatefulSet", which in turn creates the PVCs and pods together.

## StatefulSets

In the first part of this tutorial we showed how to deploy stateless services using a Deployment. Sometimes, though, you have a service that is not stateless, such as a database. Stateless and stateful services behave very differently. Typically you want to have a fixed number of database pods running - a primary and a backup, or maybe you have three instances of your app running paxos or raft to pick the current primary. Unlike with a simple web server, you wouldn't want Kubernetes to create extra database nodes on a whim, or to kill off databases without concern for their disk contents. Clearly a "Deployment" isn't adequate here. We need something new, and that something is called a "StatefulSet".

In a StatefulSet, each running pod has a unique ID assigned to it (postgres-1, postgres-2, etc...). A database is also kind of useless if it doesn't store any data, so typically members of a stateful set also have a "persistent volume claim template" to create a PVC for each pod.

Pods in a StatefulSet _can_ be moved to another physical node, but only if the volume can be moved. There are different kinds of volumes in Kubernetes - if you're using EBS volumes then Kubernetes can shut down a pod on one node, detach the EBS volume, move the volume to a new node and restart it, and the pod will never know that's it is now on a new node (at least, so long as the nodes are in the same AZ). On AWS, you might use a "local storage" driver for a "storage optimized" EC2 instance like an `ie3n` instance, with high-speed NVMe drives attached. In this case, since the volume can't be moved, Kubernetes will not be able to move the pod, and will make sure it is always scheduled on the same node.

Let's see an example. Here is a YAML file that will bring up a three-node cluster of Elasticsearch nodes:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: es
  labels:
    service: elasticsearch
spec:
  ports:
    - port: 80
      name: web
  clusterIP: None
  selector:
    service: elasticsearch
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: elasticsearch
  labels:
    service: elasticsearch
spec:
  serviceName: es
  replicas: 3
  selector:
    matchLabels:
      service: elasticsearch
  template:
    metadata:
      labels:
        service: elasticsearch
    spec:
      terminationGracePeriodSeconds: 300
      securityContext:
        fsGroup: 1000
      initContainers:
        - name: init
          image: busybox
          command: ["/bin/sh", "-c"]
          args: ["sysctl -w vm.max_map_count=262144 && ulimit -n 65536"]
          securityContext:
            privileged: true
      containers:
        - name: elasticsearch
          image: docker.elastic.co/elasticsearch/elasticsearch-oss:6.2.4
          ports:
            - containerPort: 9200
              name: http
            - containerPort: 9300
              name: tcp
          env:
            - name: cluster.name
              value: elasticsearch-cluster
            - name: node.name
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: discovery.zen.ping.unicast.hosts
              value: "elasticsearch-0.es.default.svc.cluster.local,elasticsearch-1.es.default.svc.cluster.local,elasticsearch-2.es.default.svc.cluster.local"
          volumeMounts:
            - name: data
              mountPath: /usr/share/elasticsearch/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes:
          - ReadWriteOnce
        storageClassName: standard
        resources:
          requests:
            storage: 50Gi
```

This creates a "headless service" called "es". It's called a "headless service" because the clusterIP is set to "none", which means Kubernetes won't do any load balancing between the members of the service for us.

If you apply this, you'll see three pods get created (likely you'll see one pod get created first, and then once it starts the other two will show up). Unlike with a "deployment", where pods get names with a random suffix, here the pods will be named "elasticsearch-0", "elasticsearch-1" and "elasticsearch-2". Each pod will have a PVC and PV associated with it. Each pod gets a domain name like "elasticsearch-0.es.default.svc.cluster.local", based on the name of the pod and the name of the service.

Updates work a little differently for StatefulSets too. The default option here is `updateStrategy: {type: "RollingUpdate"}`, where Kubernetes will replace each instance in the StatefulSet one-by-one.  Here it's important to define readiness checks for each pod (which we haven't discussed yet) so that the rolling update knows when a node is ready and done upgrading.  The other option here is `type: "OnDelete"`, which makes it so the StatefulSet controller will not automatically update pods - you have to manually delete pods one-by-one, and handle the upgrade yourself.

## Autoscaling

Now that we know how to create deployments and stateful sets, let's talk about Autoscaling. This is the idea that we can ramp up the number of pods we have in a deployment, or the amount of resources allocated to pods automatically. There are three different kinds of autoscaling:

- Cluster autoscaling lets us scale up (or down) the number of nodes in our cluster. There's no use creating new pods if we run out of nodes to run them on.
- Horizontal autoscaling is about scaling the number of pods that are currently running. If our web backend has a high CPU usage, or high memory usage, or even some custom stat we want to track, we can increase the number of pods to try to reduce these.
- Vertical autoscaling is about dynamically setting the CPU and memory limits for a pod - if a pod starts taking up too much CPU, we'll increase the CPU allocated to it (which may cause some pods to be rescheduled to new nodes). This is less often used - we're not going to discuss this here.

### Cluster Autoscaling

Autoscaling your cluster is obviously going to depend a great deal on how you're running your cluster (GCP vs. AWS vs. other cloud providers). The rest of these tutorials have focused on AWS, so we'll keep to that theme. When you set up your nodegroups in EKS, you can specify a minimum and maximum number of nodes.

If you are running "availability-zone aware" loads, you need to be aware that the auto-scaler treats every node in a node group the same. For example, if you have a StatefulSet that uses EBS volumes, each pod in that StatefulSet can only start on a node in the same AZ as its associated EBS volume. In this case, you need to set up a nodegroup in each AZ.  In eksctl, this would look like:

```yaml
nodeGroups:
  - name: ng1-public-2a
    instanceType: t3.small
    availabilityZones: ["eu-west-2a"]
    minSize: 1
    maxSize: 4
    tags:
      k8s.io/cluster-autoscaler/enabled: "true"
      k8s.io/cluster-autoscaler/<CLUSTER-NAME>: owned
  - name: ng1-public-2b
    instanceType: t3.small
    availabilityZones: ["eu-west-2b"]
    minSize: 1
    maxSize: 4
    tags:
      k8s.io/cluster-autoscaler/enabled: "true"
      k8s.io/cluster-autoscaler/<CLUSTER-NAME>: owned
```

If all you're doing is running stateless services, you can omit the "availabilityZones" and just create a single node group.  We're going to create some EBS volumes later, though, so we'll go with the two-nodegroup option.

Once you have your nodegroups created, you need to install the cluster-autoscaler, which you can do with this helm command:

```sh
$ helm upgrade --install auto-scaler autoscaler/cluster-autoscaler \
  --namespace kube-system \
  --set 'autoDiscovery.clusterName'=my-cluster \
  --set 'rbac.serviceAccount.create'=false \
  --set 'rbac.serviceAccount.name'=cluster-autoscaler \
  --set 'extraArgs.expander'=least-waste \
  --set 'extraArgs.balance-similar-node-groups=true'
```

Now, if you have two nodes running, and scheduling a new pod fails (because, for example, the `resources` section in the pod definition requests more CPU or memory than is available), then AWS will automatically create a new node to schedule pods on.

### Horizontal Autoscaling

In order to horizontally scale pods, you need to create a "HorizontalPodAutoscaler", or "HPA":

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
  # No `replicas` - the replica count is controlled by the HPA
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
          # Specify that this "wants" 20% of a CPU.
          resources:
            requests:
              cpu: 200m
            limits:
              cpu: 1000m
---
apiVersion: autoscaling/v2beta1
kind: HorizontalPodAutoscaler
metadata:
  name: game
  labels:
    app: web
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: game
  minReplicas: 1
  maxReplicas: 4
  metrics:
    - type: Resource
      resource:
        name: cpu
        targetAverageUtilization: 800m
```

Notice that we don't specify a `replicas` in the deployment - the HPA will take care of setting this value for us.  If average CPU usage across all pods in the `game` deployment is greater than 80%, we'll create more pods, up to a maximum of 4. Similarly, if the CPU usage is low, we'll scale down the number of pods to a minimum of 1.  You can learn more about the specific algorithm that is used to determine when to scale up or down by reading [the official docs](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/#algorithm-details).

 Also note that we now specify a `resources` section for the container, which says this pod would like at least 20% of a CPU, and is allowed to use a maximum of 100% of a CPU. If we don't specify a `resources.requests`, then the CPU utilization for this pod will be undefined in the Kubernetes API, and the HPA will ignore our pods.

## Conclusion

This part of our tutorial covered three important concepts - volumes, stateful sets, and auto scaling. [Next time](/2021/10/20/kubernetes-for-developers-part-4/) we're going to talk about monitoring your Kubernetes cluster with Prometheus and Grafana.
