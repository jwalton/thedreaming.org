---
title: "Kubernetes for Developers - Part 4: Monitoring"
tags:
  - Kubernetes
---

Kubernetes offers a powerful API that allow workloads to discover other services and pods within Kubernetes. The [`kube-prometheus`](https://github.com/prometheus-operator/kube-prometheus) stack takes advantage of this to discover information about running workloads, monitor them, and report on their performance.

`kube-prometheus` is made up of a lot of different components that work together; [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics) collects metrics about your cluster, [prometheus](https://prometheus.io/docs/introduction/overview/) queries kube-state-metrics and your own applications to collect statistics and store them in a database, [alertmanager](https://github.com/prometheus/alertmanager) sends emails or other alerts when certain metrics exceed certain tolerances, and finally [grafana](https://grafana.com/) is used to pull all this together into dashboards.

<!--more-->

## Installing

You can get most of this monitoring solution up and running with very few commands, thanks to the [kube-prometheus-stack helm chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) (formerly called the "prometheus-operator" chart, if you want to go searching for other tutorials):

```sh
# Create the "monitoring" namespace
$ kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Deploy kube-prometheus-stack into the monitoring namespace
$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
$ helm repo update
$ helm upgrade --install --namespace monitoring \
    prometheus-stack prometheus-community/kube-prometheus-stack
```

This will create a namespace called "monitoring", and deploy Prometheus-and-friends into this namespace. If you run:

```sh
$ kubectl -n monitoring port-forward svc/prometheus-stack-grafana 3000:80
```

You can get access to the Grafana dashboard via [http://localhost:3000](http://localhost:3000). The default username is "admin", with the password "prom-operator".

If you click on the Search icon on the left, you can see a list of dashboards that have already been created for you. One of my favorites is the "General/Kubernetes/Compute Resources/Namespace (Pods)" dashboard, which will show you details about how much CPU and RAM each pod is using - you can switch which namespace or you're looking at in a dropdown at the top. You can use the "General/Kubernetes/Compute Resources/Pod" dashboard to explore the resources used by any single pod.

You can also get access to the Prometheus dashboard:

```sh
$ kubectl -n monitoring port-forward svc/prometheus-stack-kube-prom-prometheus 9090:9090
```

This will let you enter a "PromQL" query and see the results instantly. We'll talk more about PromQL in a minute. You can also get access to the alertmanager dashboard to see what alerts are currently defined and which are firing:

```sh
$ kubectl -n monitoring port-forward svc/prometheus-stack-kube-prom-alertmanager 9093:9093
```

And that's it! We have monitoring deployed. Job well done... Well, not quite. This is a cool demo, but's it not quite production ready. Where does Prometheus store it's data? How can I let users from my organization get access to Grafana without us all sharing a single admin password? How do I create my own cool dashboards?

Let's dig a little deeper into Prometheus, and answer some of those questions.

## Prometheus

Prometheus is a systems monitoring and alerting engine, and a time-series database. Unlike other monitoring solutions, Prometheus is a "pull" based solution - Prometheus will actively go out and query a "/metrics" endpoint to fetch statistics from services it monitors. The list of services to monitor can be configured through a configuration file, but in the world of Kubernetes where pods come and go, we'll use special resources called "PodMonitor"s and "ServiceMonitor"s to describe what Prometheus should monitor - we can create these via YAML or a Helm chart for each service we install.

This makes it fairly trivial to get Prometheus to watch custom statistics for your applications. It's easy to export a "/metrics" endpoint that provides a count of how many HTTP requests a service has handled, for example, and then see a graph of HTTP requests across all your applications. Or you might export a "gauge" for the number of jobs currently being processed, and then you can see the sum of all jobs being processed across your cluster at a glance.

Prometheus uses a custom query language called [PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/) to query statistics. Let's go back to the Prometheus dashboard:

```sh
$ kubectl -n monitoring port-forward svc/prometheus-stack-kube-prom-prometheus 9090:9090
```

And visit [http://localhost:9090](http://localhost:9090). If you type `rest_client_requests_total` into the "Expression" bar at the top and click "Execute", you'll get a big table of counts. Each row in the table will look something like:

```txt
rest_client_requests_total{code="200", endpoint="http-metrics", host="control-plane.minikube.internal:8443", ...
```

`rest_client_requests_total` is the metric we're interested in, and all those other values are "labels" - there's one row in this table for each distinct set of labels. We can narrow our search to a specific label with a query like `rest_client_requests_total{job="kubelet"}`, which should reduce the number of rows in the table considerably. If you switch to the "graph" tab you can see each of these values graphed into a line. You'll notice these lines are continuously growing - this is because counters in Prometheus always increase. The query `rate(rest_client_requests_total{job="kubelet"}[5m])` will split this up into 5m intervals, and then plot the rate of change, giving us a more useful graph. That's just a taste of PromQL - a full PromQL tutorial is outside the scope of this tutorial.

"alertmanager" is actually part of Prometheus - basically you define "alerts" with a PromQL query. If that query returns a count, then alertmanager will fire an alert, and then can forward that alert via email or PagerDuty, or whatever else you like.

## Prometheus Storage

Prometheus has to store all this data it's collecting. With the quick demo we've created so far, it's getting stored in the Pod, eating up free space on the host machine. If the pod restarts for some reason, all the data will be lost. As we know from the [previous tutorial](/2022/03/07/kubernetes-for-developers-part-3/), we want to store all this data in a Volume.

There are going to be some configuration files for bringing up this monitoring solution; let's create a new github project to store these in:

```sh
$ mkdir monitoring
$ cd monitoring
$ git init .
```

Then we'll create a "values.yaml" file:

```yaml
alertmanager:
  config:
    receivers:
      # TODO: Add email receivers here.
      - name: "null"
  alertmanagerSpec:
    storage:
      volumeClaimTemplate:
        metadata:
          labels:
            storage: prometheus
        spec:
          storageClassName: standard
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi
prometheus:
  prometheusSpec:
    retention: 10d
    retentionSize: 160GB
    # Allow ServiceMonitors/PodMonitors from any namespace
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    storageSpec:
      volumeClaimTemplate:
        metadata:
          labels:
            storage: prometheus
        spec:
          storageClassName: standard
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 200Gi
grafana:
  persistence:
    enabled: true
    storageClassName: standard
    size: 10Gi
```

And now we can update our deployment with:

```sh
$ helm upgrade --install --namespace monitoring \
    -f values.yaml \
    prometheus-stack prometheus-community/kube-prometheus-stack
```

This will configure Prometheus to use a 200GB EBS volume, and give AlertManager a 50GB volume. Prometheus will retain data for 10 days, or for 160GB (whichever comes first). Note that Prometheus's "retentionSize" doesn't account for all the disk space that gets used, so we want to set this a healthy value below the total disk space we actually have. Also, you may notice that the retentionSize is expressed in "GB" while the storage is in "Gi" - that's because the `storage` is going to Kubernetes, and the `retentionSize` is going to be passed as `--storage.tsdb.retention.size 160GB` to prometheus, and these two applications expect these values in different formats.

We also give Grafana a small 10GB drive - this lets users and charts you create persist across restarts. Generally if you create charts, it's better to create them in Kubernetes, so they'll be there if you want to recreate your deployment on another stack. We'll look at that a bit later on. But it's handy to be able to edit charts to prototype them.

This also has a "receivers" section which at the moment only has the default "null" receiver in it. There's an excellent [tutorial about setting up receivers](https://grafana.com/blog/2020/02/25/step-by-step-guide-to-setting-up-prometheus-alertmanager-with-slack-pagerduty-and-gmail/) from Grafana's blog.

If you're curious about what other values you can put in here, [this is the Values.yaml file](https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/values.yaml) for kube-prometheus-stack. This depends on some other helm charts; everything under the `grafana:` section, for example, gets sent to the [grafana helm chart](https://github.com/grafana/helm-charts/tree/main/charts/grafana). If you want to read up on Grafana configuration, the documentation for that chart will be what you're after.

## SOPS

In a minute, we're going to configure Grafana to do single-sign-on using OAuth. To do this, we're going to have to store some secrets in some configuration files. It's a bad idea to commit secrets to a repository, so we're going to use a tool from Mozilla called SOPS to help us store encrypted secrets in our repository.

To use SOPS, first we need to install it. You can find releases [on GitHub](https://github.com/mozilla/sops/releases), or on a Mac you can `brew install sops`.

In AWS, go to the Key Management Service and create a new symmetric key. Take note of the key's ARN. In the root of your project create a file called ".sops.yaml", and fill in the key ARN:

```yaml
creation_rules:
  - kms: arn:aws:kms:us-west-2:<account_id>:key/<key_id>
```

Also in the root of your project, edit `.gitignore` and add the following:

```txt
*.plaintext.yaml
```

This will prevent any "plaintext" files from being committed to source control by accident.

Let's give this a try to make sure it's working. Create a file somewhere in your project called "mysecrets.plaintext.yaml:

```yaml
githubPassword: supersecret
```

Then run SOPS:

```sh
$ sops -e mysecrets.plaintext.yaml > mysecrets.encrypted.yaml
```

If we open up mysecrets.encrypted.yaml, we'll see it starts with the line:

```yaml
githubPassword: ENC[AES256_GCM,data:K3/UeWyuM+vzHIY=,iv:I2W6+hUH6WMaD2nWAJ5+AFyzGpVq6rrRwG+YXJioe/U=,tag:k8jzDHJ8OYNRxbz6OrnWsA==,type:str]
```

followed by some metadata about how this value was encrypted. One of the nice things about SOPS is that the structure of our YAML file is preserved - we can see in GitHub's history when certain values were changed or added.

We can decrypt this file with:

```sh
$ sops -d mysecrets.encrypted.yaml > mysecrets.plaintext.yaml
```

## Grafana Single-Sign-On

We're going to want to expose Grafana to other users in our organization, and we are not going to create individual user accounts for them. The solution to this is to use single-sign-on. In this example, we're going to use GitHub as an OAuth provider, allowing anyone who is part of our GitHub org to access the dashboard.

To do this, we're going to need a domain name. I like to use something like "ops.example.com" to group all my ops-related internal services together, so here I'd create a "grafana.ops.example.com". We'll use that as an example throughout this, but obviously you'll need to replace this with the domain name you choose.

First, go visit `https://github.com/<my-org>/`. Click on the "Settings" tab, then click on "Developer Settings", then "OAuth Apps" and click "Register an Application". Call your application "Grafana", set the "Homepage URL" to your organization's homepage. Set the "Authorization callback URL" to `https://granafa.ops.example.com/grafana/login/github`.

Once you create the application, you'll get a Client ID, and you'll need to generate a "client secret". Add both of these to a secrets.plaintext.yaml file in the root of your project:

```yaml
# secrets.plaintext.yaml
grafana:
  adminPassword: super-secret
  envRenderSecret:
    GITHUB_CLIENT_ID: YOUR_GITHUB_APP_CLIENT_ID
    GITHUB_CLIENT_SECRET: YOUR_GITHUB_APP_CLIENT_SECRET
```

Then we're going to make some updates to helm/monitoring/values.yaml:

```yaml
alertmanager: ...
prometheus: ...
grafana:
  persistence:
    enabled: true
    storageClassName: standard
    size: 10Gi
  service:
    # Must be NodePort to work with ALB Ingress.
    type: NodePort
  grafana.ini:
    server:
      # Replace this with your domain name.
      domain: granafa.ops.example.com
      root_url: "https://%(domain)s/grafana"
      serve_from_sub_path: true
    auth.github:
      enabled: true
      allow_sign_up: true
      client_id: "$__env{GITHUB_CLIENT_ID}"
      client_secret: "$__env{GITHUB_CLIENT_SECRET}"
      scopes: user:email,read:org
      auth_url: https://github.com/login/oauth/authorize
      token_url: https://github.com/login/oauth/access_token
      api_url: https://api.github.com/user
      # Replace this with your GitHub org name.
      allowed_organizations: <your-org-here>
  # ingress:
  #   enabled: true
  #   # Replace this with your domain name.
  #   hosts: ["grafana.ops.example.com"]
  #   annotations:
  #     kubernetes.io/ingress.class: "alb"
  #     alb.ingress.kubernetes.io/scheme: "internet-facing"
  #     alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
  #     alb.ingress.kubernetes.io/actions.ssl-redirect: '{"Type": "redirect", "RedirectConfig": { "Protocol": "HTTPS", "Port": "443", "StatusCode": "HTTP_301"}}'
  #     alb.ingress.kubernetes.io/certificate-arn: "arn:aws:acm:us-west-1:<account-id>:certificate/<certificate-id>"
```

Be sure to correct the domain, and to update `<your-org-here>` with your GitHub organization name - note that this is case sensitive. We can deploy this with:

```sh
$ helm upgrade --install --namespace monitoring \
    -f values.yaml \
    -f secrets.plaintext.yaml \
    prometheus-stack prometheus-community/kube-prometheus-stack
```

The idea here is that when we do a deploy, helm will use the values from `values.yaml`, but then will merge in any values we put in the "secrets.plaintext.yaml" file to produce the file values passed to the templates (actually, it first takes the "values.yaml" defined in the chart itself, then merges in our values.yaml, then merges in our secrets file). Our secrets file sets a new default password for Grafana (although this will only take effect the first time we deploy this - it won't change the existing password), and also sets up some environment variables that the Grafana chart will render into a Kubernetes "Secret" for us. These environment variables are available in the grafana.ini file, which we use to set the client_id and client_secret for OAuth.

You may notice the Ingress section is commented out. The grafana Helm chart creates a `networking.k8s.io/v1:Ingress`, and this isn't [supported by the AWS load balancer controller yet](https://github.com/kubernetes-sigs/aws-load-balancer-controller/issues/2050). So instead we need to create the ingress ourselves:

```yaml
# ingress.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  namespace: monitoring
  name: monitoring-ingress
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/scheme: "internet-facing"
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/certificate-arn: "arn:aws:acm:us-west-2:<account-id>:certificate/<certificate-id>"
spec:
  rules:
    - host: grafana.ops.example.com
      http:
        paths:
          - path: /*
            backend:
              serviceName: prometheus-stack-grafana
              servicePort: 80
```

Because Grafana has it's own login system, we can just expose it directly to the Internet. You'll notice the Prometheus and Alertmanager interfaces have no login - you can access them via port-forwarding, or if you want to you can expose them on the Internet behind something like [OAuth2 Proxy](https://alikhil.github.io/2018/05/oauth2-proxy-for-kubernetes-services/), or use [kube-auth-proxy](https://github.com/jwalton/kube-auth-proxy), to add an authentication layer.

You should be able to visit `https://grafana.ops.example.com` and click the "Sign in with GitHub" button at the bottom. If you can't connect at all, try a `kubectl -n monitoring describe ingress` to see if there are any errors from your ingress. If you get errors from GitHub, try right clicking and doing "Inpsect", then switch to the Network tab and try again - there should be an error back from the request to github.com that will point you in the right direction.

If you need to check logs from grafana, you'll need to do:

```sh
$ kubectl -n monitoring get pods
NAME                                                     READY   STATUS    RESTARTS   AGE
prometheus-stack-grafana-65b7b7b454-lnqw8                2/2     Running   0          3m34s
...

$ kubectl -n monitoring logs prometheus-stack-grafana-65b7b7b454-lnqw8 grafana
```

Note that last "grafana" at the end of the `logs` command - this is because the Grafana pod has more than one container running inside it (this is the "Ready: 2/2" in "get pods"), so you need to select which container you want to view the logs for.

Once you've signed into Grafana via github, logout and sign in again as the "admin" user. Then on the left under "Server Admin" => "Users", go find your GitHub user, click on them, and under "Permissions", change Grafana Admin from "No" to "Yes". This makes your user a Grafana admin. Then, below that under "Organizations", click "Change role" next to "Main Org.", and make yourself an admin for the organization too (which will let you create new dashboards).

## Adding Metrics to our Application

Now we have Prometheus and Grafana up and running, it would be nice if we could add some custom metrics to our application. Fortunately, this is very easy to do - we just need to add a "/metrics" endpoint in our app that serves up Prometheus statistics. The two most common metric types in Prometheus are counters and gauges.  A counter is something that only ever increases, a gauge is something that gets set to a certain level and can go up or down.

Let's say we have a transcoder server, and we want to keep track of how many jobs are currently in progress at any moment (via a gauge), and a count of how many jobs we've completed.  It might be nice to be able to work out the average length of a job, so we could also keep a total count of seconds we've spent processing jobs.  Jobs are either on a "normal" queue or a "priority" queue, so we want to add a label to each of these metrics.  The "/metrics" endpoint would need to serve up something like this:

```txt
# HELP transcoder_server_process Gauge that is always 1.
# TYPE transcoder_server_process gauge
transcoder_server_process{version="1.1.0"} 1

# HELP jobs_in_progress Number of jobs in progress
# TYPE jobs_in_progress gauge
transcoder_server_jobs_in_progress{queue="normal"} 0
transcoder_server_jobs_in_progress{queue="priority"} 1

# HELP jobs_complete_count Total number of jobs processed (both failed and succeeded)
# TYPE jobs_complete_count counter
transcoder_server_jobs_complete_count{queue="normal"} 1
transcoder_server_jobs_complete_count{queue="priority"} 0

# HELP jobs_duration_seconds Total duration of jobs in seconds
# TYPE jobs_duration_seconds counter
transcoder_server_jobs_duration_seconds{queue="normal"} 20
transcoder_server_jobs_duration_seconds{queue="priority"} 0
```

Most of these are pretty self-explanatory, but the "transcoder_server_process" gauge might be a little confusing at a glance.  Having a gauge that's always "1" seems like nonsense, but it's actually a very common technique in Prometheus.  If we have two instances running, the two gauges will be added together to make 2, so we can use this gauge to keep an eye on how many instances are running.  The "version" label lets us track what version is currently running in the cluster, and see when it changed.

Note that the "/metrics" endpoint doesn't have to be served on the same port as your application - you can serve a customer facing application from your container on port 3000, for example, and serve the "/metrics" endpoint from 3001, effectively making the stats endpoint unreachable from the outside world.

Most languages have some kind of library for generating Prometheus stats. For example, in node.js there's [prom-client](https://github.com/siimon/prom-client). Here's a quick example of a `metrics.ts` file:

```ts
import * as http from 'http';
import * as promClient from 'prom-client';
import { QueueType, Stage } from './constants';

const PREFIX = 'transcoder_server';

const jobsInProgress = new promClient.Gauge({
    name: `${PREFIX}_jobs_in_progress`,
    help: 'Number of jobs in progress',
    labelNames: ['queue'],
});

const jobsComplete = new promClient.Counter({
    name: `${PREFIX}_jobs_complete_count`,
    help: 'Total number of jobs processed (both failed and succeeded)',
    labelNames: ['queue'],
});

const jobsDuration = new promClient.Counter({
    name: `${PREFIX}_jobs_duration_seconds`,
    help: 'Total duration of jobs in seconds',
    labelNames: ['queue'],
});

const jobsFailed = new promClient.Counter({
    name: `${PREFIX}_jobs_failed_count`,
    help: 'Total number of jobs that failed',
    labelNames: ['queue'],
});

let initialized = false;

/**
 * Start the metrics server running.
 */
export function createMetricsMiddleware(): (req: http.IncomingMessage, res: http.ServerResponse) => void {
    const register = promClient.register;

    // Lazy-initialize promClient.
    if (!initialized) {
        initialized = true;

        promClient.collectDefaultMetrics({
            labels: { app: 'transcoder_server' },
            register,
        });
    }

    return (req: http.IncomingMessage, res: http.ServerResponse) => {
        register
            .metrics()
            .then((result) => {
                res.setHeader('Content-Type', register.contentType);
                res.writeHead(200);
                res.end(result);
            })
            .catch((err) => {
                res.writeHead(500);
                res.end(err.message);
            });
    };
}

export function startServer() {
  const metricsMiddleware = createMetricsMiddleware();
  const server = http.createServer((req, res) => {
      switch (req.url) {
          case '/metrics':
              metricsMiddleware(req, res);
              break;
          case '/status':
              res.writeHead(200);
              res.end('ok');
              break;
          default:
              res.writeHead(404);
              res.end();
      }
  });
  server.listen(DEFAULT_PORT);
}

export function startJob(queue: QueueType) {
    jobsInProgress.inc({ queue });
}

export function endJob(queue: QueueType, duration: number, failed: boolean) {
    jobsInProgress.dec({ queue });
    jobsComplete.inc({ queue });
    jobsDuration.inc({ queue }, Math.floor(duration / 1000));
    if (failed) {
        jobsFailed.inc({ queue });
    }
}
```

When you're creating your own metrics, keep note of the fact that each distinct set of labels will result in a new series of data in Prometheus - if you add a label like "username", this is nice because you can track stats for each individual user, but it's not so nice in that you'll create a time series for each individual user, potentially eating up terrabytes of disk space. Even your "/metrics" endpoint would return potentially thousands of rows for each metric. Try to keep the cardinality of your metrics low.

You'll note here we're adding a "queue" label to each of our counters, but if you actually give this a try, Prometheus will add a few extra labels for us:

```txt
transcoder_server_jobs_in_progress{
  container="transcoder-server",
  endpoint="http",
  instance="20.0.114.172:3001",
  job="default/transcoder-server-int",
  namespace="default",
  pod="transcoder-server-int-priority-944d74885-r45s4",
  queue="priority"
}
```

This lets us easily grab counters from, for example, a specific pod to see if that pod is misbehaving in some way.  At a glance, adding all these extra labels would seem to be counter to the advice we just discussed - to limit the cardinality of your labels.  In practice it's not such a problem - the "pod" here has a 1:1 correspondence with the "instance", for example, so these together will only create a single series in the database.

## Adding a PodMonitor

Now our application has a "/metrics" endpoint - we need to let Prometheus know where to find it.  As mentioned above, this is done using a custom resource called a `PodMonitor`.  In our service's .yaml file, or somewhere in it's Helm chart if it has one, we can add a `PodMonitor`:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: myService
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: transcoder-server
  podMetricsEndpoints:
  - port: http
    path: /metrics
```

Here the "matchLabels" tells Prometheus which pods it should be monitoring, and the `podMetricsEndpoint` tells Prometheus how to scrape metrics.  After `kubectl apply`ing this file, Prometheus should start scraping data from our application.

That wraps it up for Prometheus and Grafana.  In the next part of our series we'll look into how Prometheus's "alertmanager" can be used to alert us when something is going wrong in our cluster.