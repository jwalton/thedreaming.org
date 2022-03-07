---
title: "Kubernetes for Developers - Part 2: EKS and Ingress"
tags:
  - Kubernetes
---

In [part one](/2021/10/20/kubernetes-for-developers-part-1/), we created a service and we learned how to connect to our service from inside the cluster, and how to connect to it from outside the cluster with with port forwarding - how would we go about exposing this service on the Internet?

The answer is a Kubernetes resource called an Ingress, which describes how traffic gets into your cluster and which services traffic gets routed to. There are lots of different kinds of Ingress to choose from - you get to pick one and install it on your cluster. What an Ingress looks like in terms of network architecture will depend very much on which Ingress you choose.

If you were to install [ingress-nginx](https://kubernetes.github.io/ingress-nginx/), for example, then your ingress would consist of nginx running in several pods within your cluster (and then some method for getting all inbound traffic to those nginx pods, so it can distribute it to your services). [Traefik-ingress](https://doc.traefik.io/traefik/providers/kubernetes-ingress/) is another popular choice, because of it's built in support for fetching certificates from LetsEncrypt. In this tutorial, we're going to use AWS and EKS, so we're going to go the simple route and install the [AWS load balancer controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller), which will create ALBs for our ingress traffic.

In order to do that, we're going to set up a cluster on AWS's EKS service, then we're going to learn probably more than we want to know about security and Service Accounts, and we'll learn how to set up an Ingress. We'll also look at how to automatically configure a DNS entry for our service in Route 53 and setup SSL with a certificate from AWS.

<!--more-->

## Creating a Cluster in EKS

We did our first tutorial with minikube, but in order to expose a service to the Internet, we need a cluster that's connected to the Internet and which has features like a load balancer. These are both things which minikube is sadly missing. So, for this tutorial we're going to launch a cluster on AWS using Elastic Kubernetes Service (EKS). Note that this is not free - an EKS cluster costs about $0.10 USD per hour, depending on which region you launch it in, and then there are additional costs for the EC2 instances that get launched for running workloads. Make sure you destroy your cluster when you're done working through this tutorial - 10 cents an hour sounds cheap, but if you follow this tutorial and leave it running in us-east-1 for a month by accident, you'll be look at approximately $90 in AWS charges.

You need a few tools installed first; `kubectl` to talk to Kubernetes (which you already have installed if you followed along with part one), `eksctl` to create a cluster, `aws-iam-authenticator` for authentication, and `helm` to install helm charts. On a Mac, if you're using brew, you can install all of these with: `brew install kubectl eksctl aws-iam-authenticator helm`. Installing these on other operating systems is left as an exercise for the reader.

We're going to create our cluster with [`eksctl`](https://eksctl.io/), a tool for creating EKS clusters.  In order to create a cluster with eksctl, first we're going to create a configuration file that describes our cluster, called "cluster.yaml":

```yaml
# cluster.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: my-cluster
  region: us-west-1

iam:
  withOIDC: true
  serviceAccounts:
    - metadata:
        name: aws-load-balancer-controller
        namespace: kube-system
      wellKnownPolicies:
        awsLoadBalancerController: true
    - metadata:
        name: ebs-csi-controller-sa
        namespace: kube-system
      wellKnownPolicies:
        ebsCSIController: true
    - metadata:
        name: external-dns
        namespace: kube-system
      wellKnownPolicies:
        externalDNS: true

managedNodeGroups:
  - name: ng-1
    instanceType: t3.small
    desiredCapacity: 2
```

This will create a cluster named "my-cluster", with a managed node group containing two t3.small nodes. (There are also unmanaged node groups, although that's a bit beyond the scope of this tutorial.) There's a big "iam" section here which we'll explain a bit later...

One thing to note here - we're using a t3.small. This is about the smallest useful instance for running EKS. Every running pod in an EKS cluster is assigned it's own unique IP address from your VPC. A t3.small has a maximum of [3 network interfaces](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html#AvailableIpPerENI), and a maximum of 4 IPv4 addresses per interface. This means a single t3.small can run at most 12 pods - if you try to run more than that, new pods will not be able to be scheduled. A t3.micro has a particularly small pool here, as it will only be able to run four pods in total. EKS actually creates some pods behind-the-scenes on each node using a "DaemonSet", so a t3.micro will run out of IPs very quickly, and is not really appropriate for using with EKS.

We can bring this cluster up with:

```sh
eksctl create cluster -f cluster.yaml
```

This will take quite a while - go get yourself a coffee. This does a lot of things including creating a VPC for your new cluster to run in, the EKS cluster itself, the EC2 nodes to run your cluster, security groups, an Internet gateway, and much more. Not only does it have a lot of things to create, it's based on CloudFormation which is unfortunately not know for being particularly fast.

When it's eventually done, it will write credentials to access your cluster to "~/.kube/config", and you should be able to run `kubectl` commands. For example, you should be able to see a list of all nodes in your cluster with:

```sh
$ kubectl get nodes
NAME                                           STATUS   ROLES    AGE    VERSION
ip-192-168-61-124.us-west-1.compute.internal   Ready    <none>   140m   v1.20.7-eks-135321
ip-192-168-87-194.us-west-1.compute.internal   Ready    <none>   140m   v1.20.7-eks-135321
```

When you're done playing with the cluster, you can destroy it (and everything running on it) with:

```sh
eksctl delete cluster -f cluster.yaml
```

Be careful with this command - it goes without saying that deleting your production cluster by accident is not a great way to impress your boss and win customers.

## What happened to minikube?

If you started this tutorial in [part one](/2021/10/20/kubernetes-for-developers-part-1/), you noticed that `kubectl` was controlling your minikube cluster, but now it's controlling your EKS cluster! What happened to minikube?

If you have a look in ~/.kube/config, you'll see that kubectl now knows about two different clusters, and has authentication credentials for both of them. Kubectl has a concept called a "context" - at any given point you are in a particular context, controlling a particular cluster. You can see a list of contexts:

```sh
$ kubectl config get-contexts
CURRENT   NAME               CLUSTER      AUTHINFO           NAMESPACE
*         jason@my-cluster   my-cluster   jason@my-cluster
          minikube           minikube     minikube           default
```

The "\*" here shows which one is the current active context, and you can switch the current context with `kubectl config use-context <context-name>`.

If you switch to a new laptop or want to manage an EKS cluster created by another user, you can use this AWS command to "login" to an existing EKS cluster:

```sh
$ aws eks --region [region] update-kubeconfig --name [cluster_name] --alias [cluster_name]
```

If you tried switching contexts, switch back to the context for "my-cluster" now.

## Security - IAM and ServiceAccounts

So now we have an EKS cluster, we're ready to create an Ingres...  Well, not quite.  Before we can create an Ingress, we have to install "AWS load balancer controller" to create ALBs for us, and before we can do that, we have to talk a little about security. AWS load balancer controller is actually going to run on Pods inside our cluster. This means somehow our cluster needs to have permission to create and update load balancers in AWS. In the early days of EKS, the easiest way to do this would have been to add an IAM role that allows modifying ALBs to every node in the cluster. `eksctl` even automates this, so in your cluster.yaml file, you would have created a nodegroup like this:

```yaml
managedNodeGroups:
  - name: ng-not-very-secure
    instanceType: t3.micro
    desiredCapacity: 2
    iam:
      withAddonPolicies:
        albIngress: true # Add permission to create ALBs
```

But this assigns an IAM role to the entire node - this means any workload running on the node could theoretically create or modify an ALB. This is potentially a bit of a security problem; if someone finds a security hole in one of your services and figures out how to run commands in that Pod, they could potentially cause quite a bit of damage.

There is a resource we haven't talked about yet called a "ServiceAccount". A ServiceAccount is to Kubernetes a bit like a "user" is to a typical UNIX system. Every pod is associated with a ServiceAccount, and the ServiceAccount has various permissions and roles that affect what that pod can and can't do. For example, we might want to make it so a particular Pod is allowed to enumerate a list of running services via the Kubernetes API, or to create other new pods - Pods can't do either of those by default, but if you create a ServiceAccount and a ServiceRole, and associate that ServiceAccount to your pod, you could give the pod permission to do these sorts of things.  If you're interested in learning more about this, go read up on "Kubernetes RBAC".

We've already created some pods - what ServiceAccount are they associated with? We can see a list of ServiceAccounts on the cluster with:

```sh
$ kubectl get serviceaccount
NAME      SECRETS   AGE
default   1         161m
```

We're not interested in giving pods access to the Kubernetes API though - what we'd really like to do here is to somehow assign an IAM role to an individual Service Account, and then attach that Service Account to our load balancer controller's pod. This is exactly what the imaginatively named "IAM Roles for Service Accounts", or IRSA, lets us do. IRSA is based on OpenID Connect (OIDC); we create an OIDC provider for our cluster, then roles are constructed with a reference to that OIDC provider and to the Service Account it will be bound to. The Service Account has an annotation added to it that links back to the IAM role. IRSA, OIDC; this a lot of acronyms, and the process of setting this all up manually is [a bit involved](https://dzone.com/articles/aws-eks-fine-grained-iam-roles-for-service-account), but fortunately eksctl automates all of this fot us. This is what that long "iam" section in the cluster.yaml file we glossed over does:

```yaml
iam:
  withOIDC: true
  serviceAccounts: ...
```

If you left that bit out of your cluster.yaml file, you can still [set this up yourself with eksctl](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.2/deploy/installation/#setup-iam-role-for-service-accounts). You can also see [this example](https://github.com/weaveworks/eksctl/blob/main/examples/13-iamserviceaccounts.yaml) from eksctl to see some other commonly configured service accounts. Once that's done, you can install the controller with:

```sh
$ helm repo add eks https://aws.github.io/eks-charts && \
  kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master" && \
  helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
   -n kube-system \
   --set clusterName=my-cluster \
   --set serviceAccount.create=false \
   --set serviceAccount.name=aws-load-balancer-controller
```

A quick aside here about helm - we just ran some Helm commands. We're going to talk about it in more detail in an upcoming tutorial, but for now you can think about Helm as a bit like a "pacakge manager" for Kubernetes. That `helm upgrade --install` command we ran generated a bunch of YAML files and `kubectl apply`ed them to our cluster for us. Also, notice that we specified our `clusterName` here to Helm as a parameter, along with the `serviceAccount.name` we want the pods to use. This particular Helm chart needed the cluster name to use in the generated YAML.

## Ingress

We're finally ready to create an ingress! Let's update the `2048.yaml` file we created in [part one](/2021/10/20/kubernetes-for-developers-part-1/):

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
  type: NodePort
  ports:
    - protocol: TCP
      port: 80
      targetPort: http
      name: http
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: gameingress
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/scheme: "internet-facing"
spec:
  rules:
      http:
        paths:
         - path: /
           backend:
             serviceName: gameservice
             servicePort: http
```

If you followed along from [part one](/2021/10/20/kubernetes-for-developers-part-1/) of the tutorial, the `Deployment` and `Service` should be familiar. We did make a small change here - the Service used to be `type: ClusterIP`, which meant the service was given an IP address that could only be reached from inside the cluster. Instead we've now specified `type: NodePort` - this means that a port will be opened on each node in the cluster to allow access to this service from outside the cluster. This is required to work with the AWS load balancer controller.

The "Ingress" at the bottom is the new part. The `metadata` for the ingress contains an `annotation`: `kubernetes.io/ingress.class: "alb"`. Annotations are basically free-form strings, like labels, but they're used to set "extra" configuration on a resource - configuration that's used by some Kubernetes controller or operator, but which isn't part of the official `spec`. You could have multiple different kinds of ingress controllers configured on the same Kubernetes cluster, so the AWS load balance controller, by default, will ignore any Ingress resources that don't have this annotation. Put another way, this annotation marks this Ingress as one that the AWS load balancer controller controller should pay attention to. You can see a list of all the annotations that the AWS Load Balancer Controller supports [in the documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.2/guide/ingress/annotations).

The `spec` part is where things get interesting - we have a set of `rules` for inbound traffic, and within that we have rules for `http` (and HTTPS) traffic. Within the `http` block, we have a set of `paths`. In our case we just have the one: all traffic to any path that starts with "/" will be forwarded to the "gameservice". You can specify multiple paths here though - you could forward all traffic to "/users" to the user service, and all traffic to "/messages" to the message service; this is how you would split your backend up into multiple microservices.

Once you've updated the "2048.yaml" file, apply it, and then if everything has gone according to plan you should have a new ingress:

```sh
$ apply -f 2048.yaml
deployment.apps/game unchanged
service/gameservice unchanged
Warning: extensions/v1beta1 Ingress is deprecated in v1.14+, unavailable in v1.22+; use networking.k8s.io/v1 Ingress
ingress.extensions/gameingress created

$ kubectl get ingress
NAME          CLASS    HOSTS   ADDRESS                                                             PORTS   AGE
gameingress   <none>   *       internal-k8s-default-gameingr-xxx-yyy.us-west-1.elb.amazonaws.com   80      2m33s
```

It can take a few minutes for AWS to actually provision the ALB, and the "address" will be shown long before that happens. Log into the EC2 console for AWS, go to "Load Balancers", and find your ALB - when the "State" switches from "Provisioning" to "Active", it's ready to go. At this point you should be able to visit the URL in a browser, and see your service running. Note that you need to visit the "http://" version, not the "https://" version, because we haven't set up HTTPS yet.

You may also notice Kubernetes complain that extensions/v1beta1 is deprecated and will be removed in v1.22+.  At some point in the near future, this ingress example will change to look like the following:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: gameingress
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/scheme: "internet-facing"
spec:
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: gameservice
                port:
                  name: http

```

However, at the time of this writing the AWS load balancer controller [does not support the new networking.k8s.io/v1 API](https://github.com/kubernetes-sigs/aws-load-balancer-controller/issues/2050), so we have to use the older format for the ingress.

## Namespaces and Logs

I mentioned that when we installed the AWS load balancer controller, it would run in pods in our cluster. But, you'll notice if you run `kubectl get pods`, you can't see them:

```sh
$ kubectl get pods
NAME                    READY   STATUS    RESTARTS   AGE
game-77878d75db-svmgd   0/1     Pending   0          88s
game-77878d75db-t8hdh   0/1     Pending   0          88s
```

What gives? Where are our pods? The reason you can't see them is because of something called a "namespace". Namespaces let you divide up your cluster into "virtual" clusters. Whenever we create a resource, we can specify which namespace it will be created in via the `metadata.namespace` field. Our AWS load balancer controller is running in a special namespace called the "kube-system" namespace.

We can list all the namespaces in our cluster:

```sh
$ kubectl get namespaces
NAME              STATUS   AGE
default           Active   146m
kube-node-lease   Active   146m
kube-public       Active   146m
kube-system       Active   146m
```

Any resource we create, where we don't explicitly specify a namespace, will end up in the "default" namespace. We can list pods in the "kube-system" namespace like so:

```sh
$ kubectl --namespace kube-system get pods
NAME                                            READY   STATUS    RESTARTS   AGE
aws-load-balancer-controller-66d949fb97-cbbr4   1/1     Running   0          95m
aws-load-balancer-controller-66d949fb97-lbmn8   1/1     Running   0          95m
aws-node-7bn2r                                  1/1     Running   0          128m
aws-node-kskx9                                  1/1     Running   0          128m
coredns-546f4f657c-4t9cl                        1/1     Running   0          141m
coredns-546f4f657c-v7ckd                        1/1     Running   0          141m
kube-proxy-wff9v                                1/1     Running   0          128m
kube-proxy-x544f                                1/1     Running   0          128m
```

And there are our load balancer pods. You can replace `--namespace` with `-n` to save some typing. If something is going wrong, and the pod is not running, we can examine the state of the pod with:

```sh
$ kubectl -n kube-system describe pod aws-load-balancer-controller-66d949fb97-lbmn8
```

Frequently in the "events" section at the bottom of "describe", you'll be able to see what's preventing the pod from starting. If the pod is starting but isn't doing what you expect, or is crashing, we can get logs from each of these pods:

```sh
$ kubectl -n kube-system logs aws-load-balancer-controller-66d949fb97-lbmn8
```

Since there's a pair of them, you'll have to figure out which one is currently the "leader" by looking through the logs - it's the one doing the actual work, the other once is just there to take over in case the first one fails.

If you spend a lot of time working in a particular namespace, it can be tedious to keep typing "--namespace" over and over again.  Back when we were looking at contexts, to control which cluster we were interacting with, you may have noticed that in the list of contexts there was a column called "namespace".  We can set the default namespace for a context:

```sh
$ kubectl config set-context minikube-dev \
  --namespace=dev --cluster=minikube --user=minikube
```

If you run the above command and use the "minikube-dev" context, then when you issue any command, it will operate the "dev" namespace by default.

## DNS and HTTPS

We can now access our service through the ALB, but it would be nice if we could access the service through a domain name. You could manually configure CNAME records to point to the ALB, but it would be nice if we could get Kubenetes to automatically update our DNS records every time we bring up or update an ingress. The tool we're going to use to do this is a service called `external-dns`, which like the AWS Load Balancer Controller, we're going to run on our cluster. In order to do this, first you'll have to register a domain name. external-dns [supports many DNS registries](https://github.com/kubernetes-sigs/external-dns#deploying-to-a-cluster), but for the purposes of this tutorial we're going all in on AWS, and we're going to use Route 53.

If you already have a domain name and hosted zone, you can use them - we'll add a new subdomain and won't touch any of the existing records. Otherwise you'll need to log into the AWS management console, and go to [Route53](https://console.aws.amazon.com/route53/v2/home#Dashboard), go to "Registered domains" and register a new domain name, then go to "Hosted Zones" and create a new zone. Let's pretend you've registered "thedreaming.org" as your domain name.

To install external-dns, you can follow along with the [official installation instructions for external-dns](https://github.com/kubernetes-sigs/external-dns/blob/master/docs/tutorials/aws.md), but Bitnami has a nice [Helm chart](https://github.com/bitnami/charts/tree/master/bitnami/external-dns/) that will install external-dns for us, so for simplicity's sake we'll use it here:

```sh
$ helm repo add bitnami https://charts.bitnami.com/bitnami
$ helm upgrade --install external-dns --dry-run \
  --namespace kube-system \
  --set provider=aws \
  --set aws.zoneType=public \
  --set serviceAccount.create=false \
  --set serviceAccount.name=external-dns \
  --set txtOwnerId=UNIQUE_ID_HERE \
  --set "domainFilters[0]"=DOMAIN_NAME \
  bitnami/external-dns
```

Replace `UNIQUE_ID_HERE` with some unique ID that won't change over the life of your cluster (the cluster name, for example) - external-dns will set this on each record it creates so it can figure out which domain names it "owns". If you have multiple clusters that all create records in the same hosted zone, make sure the txtOwnerId is different in each cluster, otherwise they may clobber each other's records.  Replace `DOMAIN_NAME` with the name of your domain (e.g. "thedreaming.org") - this will get external-dns to only modify records for this domain name and no others.  You can use `domainFilters` in a case where you're being extra paranoid - let's say you work for "bigcorp.com", and you want to make extra sure no one accidentally reconfigures the DNS records for "www.bigcorp.com" - you could create a "k8s.bigcorp.com" subdomain and set this to the "domainFilters". The external-dns would be able to update "k8s.bigcorp.com" and any subdomain of "k8s.bigcorp.com", but would refuse to try to setup anything outside that subdomain.

You can run:

```sh
$ kubectl --namespace=kube-system get pods --selector "app.kubernetes.io/name=external-dns"
```

to verify the pod is up and running (note the use of a selector to get specific pods).

After we have external-dns setup, let's create a certificate for our service. If you really want to automate absolutely everything, you can use [cert-manager](https://cert-manager.io/docs/) for this - a service that runs on your cluster and automatically fetches certificates via LetsEncrypt. But, if you don't mind manually creating the certificate, you can create the certificate via [AWS Certificate Manager](https://console.aws.amazon.com/acm/home). If you have no certificates provisioned, click on "Get started" under "Provision certificates", otherwise click on "Request a certificate". From there:

- Choose "Request a public certificate" and click on the "Request a certificate" button.
- Enter your domain name (e.g. "thedreaming.org") as the domain, click "Add another name to this certificate" and then enter your domain again prefixed with "\*." to make a wildcard certificate (e.g. "\*.thedreaming.org".) Click "Next".
- Choose "DNS Validation", and then click "Next", then "Review".
- If everything looks good, click "Confirm and request".
- You now have to "validate" that you own these domains. You should see a screen with "Pending validation" next to both entries. Since both are for the same top-level domain, when you validate one it should also validate the other. Open one of these up and it will give you instructions for validating the domain name, although if your domain is on Route 53 there should be a "Create record in Route 53". Once the record has been created, click "Continue" (even though validation is still pending). This will take you to your list of certificates, and you can refresh the page until validation is complete.

Once you've created your certificate, of if you already have a certificate for the domain name in question, take note of the certificate ARN (something like "arn:aws:acm:us-west-1:XXXX:certificate/YYYY"). Now we can update our ingress. Replace the ingress in 2048.yaml with this updated version:

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: gameservice
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/scheme: "internet-facing"
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'
    alb.ingress.kubernetes.io/actions.ssl-redirect: '{"Type": "redirect", "RedirectConfig": { "Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"}}'
    alb.ingress.kubernetes.io/certificate-arn: "arn:aws:acm:us-west-1:150...:certificate/277..."
spec:
  rules:
    - host: 2048.thedreaming.org
      http:
        paths:
         # The ALB will only match this path if we come in via HTTP.
         - path: /*
           backend:
             serviceName: ssl-redirect
             servicePort: use-annotation
         - path: /*
           backend:
             serviceName: gameservice
             servicePort: http
```

Replace the "certificate-arn" with your certificate-arn, and "thedreaming.org" with your domain name. Notice here we specify the port to redirect to for HTTPS traffic via the "alb.ingress.kubernetes.io/ssl-redirect".  We have to specify this as a string: "443", instead of as a bare number.  This is because annotations can only have string values in Kubernetes.

This ingress looks a little strange, because it has two paths for "/*".  There's some funny-business going on here in the controller, which you can read about in more detail [at the bottom of this page](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.1/guide/tasks/ssl_redirect/#how-it-works), but the short version is that the first one will only match when we come in via HTTP, and will be ignored for HTTPS (because it would cause an infinite loop).

Then, apply our 2048.yaml file again:

```sh
$ kubectl apply -f 2048.yaml
deployment.apps/game unchanged
service/gameservice unchanged
ingress.extensions/gameservice configured
```

In the AWS management console, you should see a new A record has been created for our domain name, and you should now be able to visit that domain and get to the HTTPS version of the site.

## Conclusion

In part two of this tutorial we learned how to bring up a cluster in AWS, we learned a bit about security, and we learned about how to set up an Ingress to bring traffic into our cluster.  In [part three](/2021/10/20/kubernetes-for-developers-part-3/) we're going to look at some important concepts like volumes, stateful sets, and autoscaling.
