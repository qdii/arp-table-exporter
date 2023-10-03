# arp-table-exporter
A daemon which continuously exports information the ARP table for consumption by prometheus.

In practice, every minute the daemon scrapes the /proc/net/arp table, and continuously
exports the timestamps at which each of the neighbors were last seen.

## Deploying on Kubernetes

The `DaemonSet` allows you to monitor neighbors on every nodes of your cluster:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: arp-table-exporter
spec:
  selector:
    matchLabels:
      name: arp-table-exporter
  template:
    metadata:
      labels:
        name: arp-table-exporter
    spec:
      containers:
      - name: arp-table-exporter
        image: qdii/arp-table-exporter:1.0.0
        securityContext:
          privileged: true
        ports:
        - name: web
          containerPort: 8000
```

If you have the [Prometheus operator](https://github.com/prometheus-operator/prometheus-operator)
set up on your cluster, you can add the following `PodMonitor` to regularly
scrape the pods:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: arp-table-exporter
  labels:
    jobLabel: arp-table-exporter
    release: prometheus
spec:
  jobLabel: name
  selector:
    matchLabels:
      name: arp-table-exporter
  podMetricsEndpoints:
  - port: web
```
