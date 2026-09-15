# 📝 CKA Real Exam Mock — Set 2: Advanced & Killer.sh Level Tasks

> **Exam Duration:** 120 Minutes · **Total Tasks:** 17 Tasks · **Passing Score:** 66% (Target: ≥ 85%)
> **Rules:** Advanced scenarios mirroring the challenging edge-cases frequently reported in Killer.sh and Reddit discussions.
> Always run the `kubectl config use-context` command at the beginning of each task!

---

### Task 1: Multi-AZ StorageClass with `WaitForFirstConsumer` (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Create a new `StorageClass` named `regional-delayed-sc` using provisioner `kubernetes.io/no-provisioner`.
It must have:
- `volumeBindingMode: WaitForFirstConsumer`
- `reclaimPolicy: Delete`
- `allowVolumeExpansion: true`

Next, create a PersistentVolumeClaim named `delayed-pvc` in namespace `storage-test` requesting `500Mi` storage using `storageClassName: regional-delayed-sc`.
Verify that the PVC initially remains in `Pending` state waiting for a pod to consume it.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
Create `sc-pvc.yaml`:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: regional-delayed-sc
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
allowVolumeExpansion: true
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: delayed-pvc
  namespace: storage-test
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: regional-delayed-sc
  resources:
    requests:
      storage: 500Mi
```

Apply and verify:
```bash
kubectl create ns storage-test --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f sc-pvc.yaml

# Verify delayed binding behavior:
kubectl get pvc delayed-pvc -n storage-test
# STATUS should be Pending (waiting for first consumer pod)
```
</details>

---

### Task 2: Custom Secondary Scheduler Configuration (Weight: 8%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Deploy a secondary scheduler in namespace `kube-system` using the standard `kube-scheduler:v1.31.0` image.
The scheduler must be configured with the name `my-custom-scheduler`.
Then, create a Pod named `custom-scheduled-pod` in namespace `default` using image `nginx` that explicitly uses `my-custom-scheduler` for scheduling.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
Create `scheduler-and-pod.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-custom-scheduler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-custom-scheduler
  template:
    metadata:
      labels:
        app: my-custom-scheduler
    spec:
      serviceAccountName: my-scheduler-sa
      containers:
      - name: kube-scheduler
        image: registry.k8s.io/kube-scheduler:v1.31.0
        command:
        - kube-scheduler
        - --leader-elect=false
        - --scheduler-name=my-custom-scheduler
---
apiVersion: v1
kind: Pod
metadata:
  name: custom-scheduled-pod
  namespace: default
spec:
  schedulerName: my-custom-scheduler   # <-- Specify custom scheduler
  containers:
  - name: nginx
    image: nginx
```

Apply and verify:
```bash
kubectl apply -f scheduler-and-pod.yaml
kubectl get pod custom-scheduled-pod -o wide
# Check events to confirm scheduled by my-custom-scheduler
kubectl describe pod custom-scheduled-pod | grep "Scheduled"
```
</details>

---

### Task 3: StatefulSet Scaling with Headless Service (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
Create a Headless Service named `cassandra-svc` in namespace `database` with `clusterIP: None` exposing port `9042`.
Then, create a `StatefulSet` named `cassandra` with 2 replicas using image `cassandra:3.11`.
Ensure the StatefulSet is connected to `serviceName: cassandra-svc`.
Each pod must have a volume mount at `/var/lib/cassandra` using `volumeClaimTemplates` requesting `1Gi` from `storageClassName: standard`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
Create `stateful-cassandra.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: cassandra-svc
  namespace: database
spec:
  clusterIP: None
  selector:
    app: cassandra
  ports:
  - port: 9042
    name: cql
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: cassandra
  namespace: database
spec:
  serviceName: cassandra-svc
  replicas: 2
  selector:
    matchLabels:
      app: cassandra
  template:
    metadata:
      labels:
        app: cassandra
    spec:
      containers:
      - name: cassandra
        image: cassandra:3.11
        ports:
        - containerPort: 9042
        volumeMounts:
        - name: cassandra-data
          mountPath: /var/lib/cassandra
  volumeClaimTemplates:
  - metadata:
      name: cassandra-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: standard
      resources:
        requests:
          storage: 1Gi
```

Apply and verify:
```bash
kubectl create ns database --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f stateful-cassandra.yaml
kubectl get statefulset cassandra -n database
kubectl get pods -n database
# Pods should be named cassandra-0 and cassandra-1
```
</details>

---

### Task 4: CronJob with `concurrencyPolicy: Forbid` (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
Create a CronJob named `db-backup-cron` in namespace `maintenance`.
Requirements:
- Schedule: Every 3 minutes (`*/3 * * * *`)
- ConcurrencyPolicy: `Forbid`
- SuccessfulJobsHistoryLimit: `3`
- FailedJobsHistoryLimit: `2`
- Image: `busybox:1.28`
- Command: `sh -c "echo 'Database backup in progress'; sleep 10"`

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
kubectl create ns maintenance --dry-run=client -o yaml | kubectl apply -f -

cat << 'EOF' > cron.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup-cron
  namespace: maintenance
spec:
  schedule: "*/3 * * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 2
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup-worker
            image: busybox:1.28
            command: ["sh", "-c", "echo 'Database backup in progress'; sleep 10"]
EOF

kubectl apply -f cron.yaml
kubectl get cronjob db-backup-cron -n maintenance
```
</details>

---

### Task 5: NetworkPolicy with AND Logic (Namespace + Pod) (Weight: 8%)

**Context:**
```bash
kubectl config use-context k8s-cluster3
```

**Task:**
In namespace `payment`, create a `NetworkPolicy` named `restrict-payment-gw`.
The policy applies to pods with label `app: payment-gateway`.
It must allow ingress traffic ONLY from pods that have label `access: granted` **AND** reside inside a namespace with label `team: checkout`.
Allow all egress traffic.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-payment-gw
  namespace: payment
spec:
  podSelector:
    matchLabels:
      app: payment-gateway
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          team: checkout
      podSelector:       # <-- IN THE SAME ARRAY ITEM FOR 'AND' LOGIC
        matchLabels:
          access: granted
```

Apply and verify:
```bash
kubectl apply -f netpol-and.yaml
kubectl describe netpol restrict-payment-gw -n payment
```
</details>

---

### Task 6: Ingress URL Rewrite with Annotations (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster3
```

**Task:**
Create an Ingress named `api-rewrite-ingress` in namespace `gateway`.
Requirements:
- Class: `nginx`
- Host: `api.company.com`
- Any request matching path prefix `/v2/services/(.*)` must be rewritten to `/$1` before reaching backend service `v2-service` on port `8080`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-rewrite-ingress
  namespace: gateway
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$1
    nginx.ingress.kubernetes.io/use-regex: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: api.company.com
    http:
      paths:
      - path: /v2/services/(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: v2-service
            port:
              number: 8080
```

Apply and verify:
```bash
kubectl apply -f rewrite-ing.yaml
kubectl get ingress api-rewrite-ingress -n gateway
```
</details>

---

### Task 7: DaemonSet Tolerating Control Plane Taints (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Create a DaemonSet named `security-agent` in namespace `kube-system`.
Use image `busybox:1.28` with command `sleep 3600`.
Ensure that pods of this DaemonSet are scheduled on **ALL NODES**, including the control plane node(s) which have taint `node-role.kubernetes.io/control-plane:NoSchedule`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: security-agent
  namespace: kube-system
  labels:
    app: security-agent
spec:
  selector:
    matchLabels:
      app: security-agent
  template:
    metadata:
      labels:
        app: security-agent
    spec:
      tolerations:
      - key: "node-role.kubernetes.io/control-plane"
        operator: "Exists"
        effect: "NoSchedule"
      containers:
      - name: agent
        image: busybox:1.28
        command: ["sleep", "3600"]
```

Apply and verify:
```bash
kubectl apply -f ds-toleration.yaml
kubectl get pods -n kube-system -l app=security-agent -o wide
# Pods should be running on all nodes including controlplane
```
</details>

---

### Task 8: Troubleshoot Kubelet Cgroup Driver Mismatch (Weight: 8%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Worker node `node02` failed to start after a system update.
SSH to `node02`, investigate the journal logs of `kubelet`, fix the cgroup driver or container runtime mismatch, and return `node02` to `Ready` status.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. SSH to node02
ssh node02

# 2. Check kubelet failure logs
sudo journalctl -u kubelet -e --no-pager -n 25
# Look for error: "failed to run Kubelet: misconfiguration: kubelet cgroup driver: "cgroupfs" is different from docker/containerd cgroup driver "systemd""

# 3. Edit kubelet config file:
sudo vim /var/lib/kubelet/config.yaml
# Change:
# cgroupDriver: systemd

# 4. Restart services
sudo systemctl daemon-reload
sudo systemctl restart kubelet
sudo systemctl status kubelet # Active: active (running)

# 5. Exit and verify from master
exit
kubectl get nodes
# node02 should show Ready
```
</details>

---

### Task 9: Static Pod Creation on Remote Worker Node (Weight: 5%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
Create a Static Pod named `node-health-checker` using image `busybox:1.28` running command `sleep 7200` on worker node `node01`.
Configure it directly via the node's static pod manifest directory.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. SSH to worker node01
ssh node01

# 2. Identify staticPodPath in kubelet config
cat /var/lib/kubelet/config.yaml | grep staticPodPath
# Typically: /etc/kubernetes/manifests

# 3. Create manifest directly inside manifests directory
cat << 'EOF' | sudo tee /etc/kubernetes/manifests/node-health-checker.yaml
apiVersion: v1
kind: Pod
metadata:
  name: node-health-checker
spec:
  containers:
  - name: checker
    image: busybox:1.28
    command: ["sleep", "7200"]
EOF

# 4. Exit to master node
exit

# 5. Verify mirror pod
kubectl get pods -A | grep node-health-checker-node01
```
</details>

---

### Task 10: Sort Events by Creation Timestamp (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
List all Kubernetes Events in namespace `kube-system`.
Sort the events chronologically based on `.metadata.creationTimestamp`.
Extract only the Reason and Message into `/opt/kube-system-events.log`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
kubectl get events -n kube-system \
  --sort-by=.metadata.creationTimestamp \
  -o custom-columns=REASON:.reason,MESSAGE:.message > /opt/kube-system-events.log

# Verify
cat /opt/kube-system-events.log | head -n 10
```
</details>

---

### Task 11: Pod with SecurityContext Capabilities (Weight: 5%)

**Context:**
```bash
kubectl config use-context k8s-cluster3
```

**Task:**
Create a Pod named `time-syncer` in namespace `default` with image `busybox:1.28`.
The container must run command `sleep 3600`.
Grant the Linux capability `SYS_TIME` to the container while ensuring `allowPrivilegeEscalation` is disabled (`false`).

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: time-syncer
  namespace: default
spec:
  containers:
  - name: syncer
    image: busybox:1.28
    command: ["sleep", "3600"]
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        add: ["SYS_TIME"]
```

Apply and verify:
```bash
kubectl apply -f time-syncer.yaml
kubectl get pod time-syncer
```
</details>

---

### Task 12: Horizontal Pod Autoscaler (HPA v2) (Weight: 6%)

**Context:**
```bash
kubectl config use-context k8s-cluster3
```

**Task:**
Create a HorizontalPodAutoscaler named `web-hpa` for deployment `frontend` in namespace `default`.
Configure it to scale between `2` and `10` replicas.
Target CPU average utilization must be `70%`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
kubectl autoscale deployment frontend \
  --name=web-hpa \
  --min=2 \
  --max=10 \
  --cpu-percent=70 \
  -n default

# Verification
kubectl get hpa web-hpa -n default
```
</details>

---

### Task 13: Service Account Secret Binding (v1.24+) (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Create a ServiceAccount named `build-robot` in namespace `ci-cd`.
Manually generate an API token Secret for this ServiceAccount named `build-robot-secret` using annotation `kubernetes.io/service-account.name: build-robot` and type `kubernetes.io/service-account-token`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
kubectl create ns ci-cd --dry-run=client -o yaml | kubectl apply -f -
kubectl create sa build-robot -n ci-cd

cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: build-robot-secret
  namespace: ci-cd
  annotations:
    kubernetes.io/service-account.name: build-robot
type: kubernetes.io/service-account-token
EOF

# Verify token generation:
kubectl get secret build-robot-secret -n ci-cd -o jsonpath='{.data.token}' | base64 -d
```
</details>

---

### Task 14: Pod AntiAffinity Across Availability Zones (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
Deploy an Nginx deployment named `distributed-web` with 3 replicas in namespace `production`.
Configure `podAntiAffinity` so that no two pods of this deployment run on nodes that share the same availability zone label `topology.kubernetes.io/zone`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: distributed-web
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: distributed-web
  template:
    metadata:
      labels:
        app: distributed-web
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - distributed-web
            topologyKey: "topology.kubernetes.io/zone"
      containers:
      - name: nginx
        image: nginx:alpine
```

Apply and verify:
```bash
kubectl apply -f distributed-web.yaml
kubectl get pods -n production -o wide
```
</details>

---

### Task 15: Secret Decryption & Modification (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
There is a Secret named `api-credentials` in namespace `default`.
Decode the key `API_KEY` into plaintext, change its value to `NEW_SECRET_KEY_999`, and update the Secret without recreating it.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. Base64 encode new value:
NEW_VAL=$(echo -n "NEW_SECRET_KEY_999" | base64)

# 2. Patch the Secret directly:
kubectl patch secret api-credentials -p "{\"data\":{\"API_KEY\":\"$NEW_VAL\"}}"

# 3. Verify
kubectl get secret api-credentials -o jsonpath='{.data.API_KEY}' | base64 -d
# Output: NEW_SECRET_KEY_999
```
</details>

---

### Task 16: Troubleshoot CoreDNS CrashLoopBackOff (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster3
```

**Task:**
Pods in namespace `default` cannot resolve any internal services.
Investigate the `coredns` deployment in namespace `kube-system`.
Resolve why CoreDNS pods are crashing and restore internal DNS functionality.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. Check CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns

# 2. Check logs of crashing CoreDNS pod
kubectl logs -n kube-system -l k8s-app=kube-dns --previous
# Common exam error: "plugin/loop: Loop (127.0.0.1:53 -> :53) detected"
# Cause: Upstream DNS loop in host /etc/resolv.conf

# 3. Edit CoreDNS ConfigMap
kubectl edit configmap coredns -n kube-system
# If loop detected, comment out or remove the "loop" plugin line,
# or change "forward . /etc/resolv.conf" to "forward . 8.8.8.8"

# 4. Restart CoreDNS
kubectl rollout restart deployment coredns -n kube-system

# 5. Verify resolution
kubectl run test-dns --image=busybox:1.28 --rm -it --restart=Never -- nslookup kubernetes.default
```
</details>

---

### Task 17: Container Exit Code Analysis (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
The pod `batch-worker` in namespace `default` failed.
Find the Exit Code of the terminated container and write the exit code number into `/opt/exit-code.txt`.
If the termination reason was `OOMKilled`, write `YES` into `/opt/oom-status.txt`, otherwise write `NO`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. Inspect container termination status:
EXIT_CODE=$(kubectl get pod batch-worker -o jsonpath='{.status.containerStatuses[0].state.terminated.exitCode}')
echo $EXIT_CODE > /opt/exit-code.txt

REASON=$(kubectl get pod batch-worker -o jsonpath='{.status.containerStatuses[0].state.terminated.reason}')
if [ "$REASON" = "OOMKilled" ]; then
  echo "YES" > /opt/oom-status.txt
else
  echo "NO" > /opt/oom-status.txt
fi

# Verification
cat /opt/exit-code.txt
cat /opt/oom-status.txt
```
</details>

---

## 🏆 Scoring Checklist for Set 2

| Task # | Topic | Weight | Completed? | Verified? |
|---|---|---|---|---|
| **1** | Multi-AZ StorageClass WaitForFirstConsumer | 7% | [ ] | [ ] |
| **2** | Custom Secondary Scheduler | 8% | [ ] | [ ] |
| **3** | StatefulSet Scaling with Headless Service | 7% | [ ] | [ ] |
| **4** | CronJob ConcurrencyPolicy Forbid | 4% | [ ] | [ ] |
| **5** | NetworkPolicy AND Logic (Namespace + Pod) | 8% | [ ] | [ ] |
| **6** | Ingress URL Rewrite with Annotations | 7% | [ ] | [ ] |
| **7** | DaemonSet Tolerating Control Plane Taints | 7% | [ ] | [ ] |
| **8** | Troubleshoot Kubelet Cgroup Mismatch | 8% | [ ] | [ ] |
| **9** | Static Pod on Worker Node | 5% | [ ] | [ ] |
| **10** | Sort Events by Creation Timestamp | 4% | [ ] | [ ] |
| **11** | Pod with SecurityContext Capabilities | 5% | [ ] | [ ] |
| **12** | Horizontal Pod Autoscaler (HPA) | 6% | [ ] | [ ] |
| **13** | ServiceAccount API Secret Binding | 4% | [ ] | [ ] |
| **14** | Pod AntiAffinity Across AZs | 7% | [ ] | [ ] |
| **15** | Secret Decryption & Modification | 4% | [ ] | [ ] |
| **16** | Troubleshoot CoreDNS CrashLoop | 7% | [ ] | [ ] |
| **17** | Exit Code Analysis | 4% | [ ] | [ ] |
| **TOTAL** | | **100%** | **Target: ≥ 85%** | |
