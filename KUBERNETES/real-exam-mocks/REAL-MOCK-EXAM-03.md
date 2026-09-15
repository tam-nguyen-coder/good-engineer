# 📝 CKA Real Exam Mock — Set 3: Speed, Accuracy & Advanced Scenarios

> **Exam Duration:** 120 Minutes · **Total Tasks:** 17 Tasks · **Passing Score:** 66% (Target: ≥ 85%)
> **Rules:** Authentic performance-based English tasks crawled from recent CKA exam experiences (v1.30–v1.32), Killer.sh high-difficulty scenarios, and community forums.
> **Critical Rule:** Always execute `kubectl config use-context <context-name>` before starting each task!

---

### Task 1: Encrypting Secret Data at Rest (Weight: 8%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
The cluster currently stores Kubernetes Secrets in plain text in etcd. You are tasked with enabling encryption at rest for all `Secret` objects using the `aescbc` provider.
1. Create an `EncryptionConfiguration` file at `/etc/kubernetes/enc/enc.yaml` using the base64-encoded 32-byte secret key provided below:
   - Secret key: `c3VwZXJzZWNyZXRwYXNzd29yZDEyMzQ1Njc4OQ==`
2. Update the `kube-apiserver` static pod manifest at `/etc/kubernetes/manifests/kube-apiserver.yaml` to use this encryption configuration via the `--encryption-provider-config` flag.
3. Ensure the `kube-apiserver` restarts and becomes fully healthy.
4. Re-encrypt all existing secrets in the cluster so that they are stored encrypted in etcd.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. SSH to controlplane node (if needed) and create directory
mkdir -p /etc/kubernetes/enc

# 2. Create the EncryptionConfiguration file
cat <<EOF > /etc/kubernetes/enc/enc.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: c3VwZXJzZWNyZXRwYXNzd29yZDEyMzQ1Njc4OQ==
      - identity: {}
EOF

# 3. Mount the directory and set the flag in /etc/kubernetes/manifests/kube-apiserver.yaml
# Edit /etc/kubernetes/manifests/kube-apiserver.yaml:
# Under spec.containers[0].command:
#   - --encryption-provider-config=/etc/kubernetes/enc/enc.yaml
# Under spec.containers[0].volumeMounts:
#   - mountPath: /etc/kubernetes/enc
#     name: enc
#     readOnly: true
# Under spec.volumes:
#   - hostPath:
#       path: /etc/kubernetes/enc
#       type: DirectoryOrCreate
#     name: enc

# 4. Wait for kube-apiserver to restart
sleep 15
kubectl get pods -n kube-system | grep kube-apiserver

# 5. Re-encrypt all existing secrets in the cluster
kubectl get secrets --all-namespaces -o json | kubectl replace -f -

# 6. Verification: Create a test secret and check raw etcd content
kubectl create secret generic test-enc-secret --from-literal=pass=topsecret -n default

# Check in etcd (must show 'k8s:enc:aescbc:v1:key1')
ETCDCTL_API=3 etcdctl \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/secrets/default/test-enc-secret | hexdump -C
```
</details>

---

### Task 2: Troubleshooting a Broken Kube-Proxy DaemonSet (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Applications running on worker nodes cannot access Services via ClusterIP. It has been reported that the `kube-proxy` DaemonSet in namespace `kube-system` has failing or crash-looping Pods.
1. Diagnose why `kube-proxy` pods are failing on worker nodes.
2. Correct the misconfiguration in the `kube-proxy` DaemonSet or its ConfigMap.
3. Ensure all `kube-proxy` pods reach `Running` state and ClusterIP routing functions properly across all nodes.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Inspect kube-proxy pods in kube-system
kubectl get pods -n kube-system -l k8s-app=kube-proxy

# 2. Check logs of a failing kube-proxy pod
kubectl logs -n kube-system -l k8s-app=kube-proxy --tail=50

# Common issues seen on exams:
# Case A: Typo in ConfigMap `kube-proxy` (e.g. clusterCIDR format, mode: "iptables" mistyped)
kubectl edit configmap kube-proxy -n kube-system
# If ConfigMap is edited, restart DaemonSet:
kubectl rollout restart daemonset kube-proxy -n kube-system

# Case B: Typo in DaemonSet command or image tag in DaemonSet spec
kubectl edit daemonset kube-proxy -n kube-system

# Case C: Missing or misconfigured hostPath volume for /run/xtables.lock or /lib/modules

# 3. Verify all pods running
kubectl rollout status daemonset kube-proxy -n kube-system

# 4. Test service resolution
kubectl run test-curl --rm -it --image=curlimages/curl -- restart=Never -- curl -m 3 http://kubernetes.default.svc.cluster.local
```
</details>

---

### Task 3: Worker Node Maintenance with PodDisruptionBudget (Weight: 6%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
You need to perform kernel maintenance on node `node02`.
1. Ensure that any eviction respects existing `PodDisruptionBudget` policies.
2. Safely drain `node02` so that all workloads running on it are evicted to other nodes. Force eviction of pods with `emptyDir` storage and ignore any `DaemonSet` pods.
3. After simulating maintenance, mark `node02` as schedulable again.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Check PodDisruptionBudgets in the cluster
kubectl get pdb --all-namespaces

# 2. Safely drain the node
kubectl drain node02 --ignore-daemonsets --delete-emptydir-data --force

# 3. Verify node status is 'SchedulingDisabled'
kubectl get nodes

# 4. Verify no non-DaemonSet pods remain on node02
kubectl get pods --all-namespaces -o wide | grep node02

# 5. Uncordon the node to allow scheduling again
kubectl uncordon node02

# 6. Verify node02 is Ready and schedulable
kubectl get node node02
```
</details>

---

### Task 4: Multi-Container Pod with Shared Volume (Logging Pattern) (Weight: 5%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
In namespace `production`, create a Pod named `order-processor`:
1. The primary container named `app` must run image `busybox:1.36` and write the current timestamp every 2 seconds to `/var/log/app/transaction.log`:
   `while true; do date >> /var/log/app/transaction.log; sleep 2; done`
2. The sidecar container named `log-shipper` must run image `busybox:1.36` and stream this log file using:
   `tail -n+1 -f /var/log/app/transaction.log`
3. Use an `emptyDir` volume named `log-volume` mounted at `/var/log/app` in both containers.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Create namespace if not exists
kubectl create namespace production --dry-run=client -o yaml | kubectl apply -f -

# 2. Create the Pod manifest
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: order-processor
  namespace: production
spec:
  volumes:
    - name: log-volume
      emptyDir: {}
  containers:
    - name: app
      image: busybox:1.36
      command: ["/bin/sh", "-c", "while true; do date >> /var/log/app/transaction.log; sleep 2; done"]
      volumeMounts:
        - name: log-volume
          mountPath: /var/log/app
    - name: log-shipper
      image: busybox:1.36
      command: ["/bin/sh", "-c", "tail -n+1 -f /var/log/app/transaction.log"]
      volumeMounts:
        - name: log-volume
          mountPath: /var/log/app
EOF

# 3. Verification
kubectl wait --for=condition=Ready pod/order-processor -n production --timeout=30s
kubectl logs order-processor -c log-shipper -n production --tail=5
```
</details>

---

### Task 5: Modern Traffic Routing with Gateway API HTTPRoute (Weight: 6%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
A Gateway named `prod-gateway` already exists in namespace `gateway-infra`.
Create an `HTTPRoute` named `payments-route` in namespace `ecommerce` that attaches to `gateway-infra/prod-gateway`:
- Hostname: `pay.example.com`
- Rules:
  - Exact path match on `/v2/checkout` forwards to Service `checkout-v2-svc` on port `8080`.
  - Prefix path match on `/v1` forwards to Service `checkout-v1-svc` on port `80`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Create the HTTPRoute manifest
cat <<EOF | kubectl apply -f -
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: payments-route
  namespace: ecommerce
spec:
  parentRefs:
    - name: prod-gateway
      namespace: gateway-infra
  hostnames:
    - "pay.example.com"
  rules:
    - matches:
        - path:
            type: Exact
            value: /v2/checkout
      backendRefs:
        - name: checkout-v2-svc
          port: 8080
    - matches:
        - path:
            type: PathPrefix
            value: /v1
      backendRefs:
        - name: checkout-v1-svc
          port: 80
EOF

# 2. Verification
kubectl get httproute payments-route -n ecommerce -o yaml
```
</details>

---

### Task 6: Troubleshoot Kubelet Client Certificate Expiration (Weight: 8%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Worker node `node01` is reporting `NotReady`. Checking `systemctl status kubelet` on `node01` shows repeated error logs:
`certificate has expired or is not yet valid` or `x509: certificate signed by unknown authority`.
1. SSH into `node01`.
2. Inspect the kubelet configuration and certificates under `/var/lib/kubelet/pki`.
3. Renew or re-bootstrap the kubelet client certificate using `/etc/kubernetes/bootstrap-kubelet.conf` or regenerate the kubeconfig from the control plane.
4. Restart `kubelet` and verify `node01` transitions back to `Ready`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. SSH to node01
ssh node01

# 2. Inspect kubelet service logs
journalctl -u kubelet -n 50 --no-pager

# 3. Check kubelet client certificates
openssl x509 -in /var/lib/kubelet/pki/kubelet-client-current.pem -text -noout | grep "Not After"

# 4. If bootstrap file exists, recover kubeconfig:
if [ -f /etc/kubernetes/bootstrap-kubelet.conf ]; then
  # Re-point kubelet to bootstrap kubeconfig
  systemctl restart kubelet
fi

# Alternative recovery if certificates are manually broken:
# Copy working kubeconfig from controlplane:
# scp controlplane:/etc/kubernetes/admin.conf /etc/kubernetes/kubelet.conf (or kubelet specific config)
# Or regenerate bootstrap token on controlplane:
# kubeadm token create --print-join-command

# 5. Restart kubelet
systemctl daemon-reload
systemctl restart kubelet
systemctl status kubelet

# 6. Exit back to control plane and verify node status
exit
kubectl get nodes
```
</details>

---

### Task 7: Advanced NetworkPolicy with CoreDNS Exception (Weight: 8%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
In namespace `secure-zone`, isolate all pods with label `role: worker` so that:
1. **Ingress:** Allow incoming TCP traffic on port `3000` ONLY from pods with label `role: frontend` in the same namespace.
2. **Egress:**
   - Allow outgoing UDP and TCP traffic on port `53` to namespace `kube-system` for DNS resolution.
   - Allow outgoing TCP traffic on port `443` ONLY to CIDR block `192.168.10.0/24`.
   - Deny all other incoming and outgoing traffic.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Ensure namespace kube-system has a known label for namespaceSelector
kubectl label namespace kube-system kubernetes.io/metadata.name=kube-system --overwrite

# 2. Apply the NetworkPolicy
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: worker-netpol
  namespace: secure-zone
spec:
  podSelector:
    matchLabels:
      role: worker
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              role: frontend
      ports:
        - protocol: TCP
          port: 3000
  egress:
    # Rule 1: DNS Resolution (UDP + TCP 53)
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
    # Rule 2: HTTPS to specific CIDR
    - to:
        - ipBlock:
            cidr: 192.168.10.0/24
      ports:
        - protocol: TCP
          port: 443
EOF

# 3. Verification
kubectl describe networkpolicy worker-netpol -n secure-zone
```
</details>

---

### Task 8: Reclaiming a PersistentVolume in Released State (Weight: 6%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
A PersistentVolume named `legacy-data-pv` was created with `persistentVolumeReclaimPolicy: Retain`. The original PVC that claimed it has been deleted, leaving the PV in `Released` status.
1. Make `legacy-data-pv` available again for new claims without losing any data stored on it.
2. In namespace `analytics`, create a PVC named `analytics-pvc` that binds to this exact PV `legacy-data-pv`. Request `2Gi` storage with accessMode `ReadWriteOnce`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Inspect the PV status
kubectl get pv legacy-data-pv

# 2. Remove the claimRef to return the PV to 'Available' status
kubectl patch pv legacy-data-pv --type=json -p='[{"op": "remove", "path": "/spec/claimRef"}]'

# 3. Verify PV status changed from Released to Available
kubectl get pv legacy-data-pv
# Expected: STATUS == Available

# 4. Create the new PVC in namespace analytics
kubectl create namespace analytics --dry-run=client -o yaml | kubectl apply -f -

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: analytics-pvc
  namespace: analytics
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
  volumeName: legacy-data-pv
EOF

# 5. Verification: Verify PVC and PV are Bound
kubectl get pvc analytics-pvc -n analytics
kubectl get pv legacy-data-pv
```
</details>

---

### Task 9: Projected Volume with ServiceAccountToken (Weight: 5%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
In namespace `security-lab`, create a Pod named `token-inspector`:
1. Use ServiceAccount `vault-auth-sa` (create it if missing).
2. Use image `nginx:1.25-alpine`.
3. Mount a projected volume named `token-volume` at path `/var/run/secrets/tokens`:
   - Projected `serviceAccountToken`:
     - `audience`: `https://vault.internal`
     - `expirationSeconds`: `7200`
     - `path`: `vault-token`

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Create namespace and ServiceAccount
kubectl create namespace security-lab --dry-run=client -o yaml | kubectl apply -f -
kubectl create serviceaccount vault-auth-sa -n security-lab --dry-run=client -o yaml | kubectl apply -f -

# 2. Create the Pod
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: token-inspector
  namespace: security-lab
spec:
  serviceAccountName: vault-auth-sa
  containers:
    - name: nginx
      image: nginx:1.25-alpine
      volumeMounts:
        - name: token-volume
          mountPath: /var/run/secrets/tokens
          readOnly: true
  volumes:
    - name: token-volume
      projected:
        sources:
          - serviceAccountToken:
              audience: https://vault.internal
              expirationSeconds: 7200
              path: vault-token
EOF

# 3. Verification
kubectl wait --for=condition=Ready pod/token-inspector -n security-lab --timeout=30s
kubectl exec token-inspector -n security-lab -- ls -la /var/run/secrets/tokens/vault-token
```
</details>

---

### Task 10: Non-Resource URL RBAC Authorization (Weight: 5%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
A monitoring agent needs read-only access to cluster health and metrics endpoints:
1. Create a `ClusterRole` named `monitoring-endpoints-cr` granting `get` access to the non-resource URLs `/healthz` and `/metrics`.
2. Create a `ClusterRoleBinding` named `monitoring-endpoints-crb` that assigns this `ClusterRole` to the user `prom-collector`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Create ClusterRole manifest for non-resource URLs
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-endpoints-cr
rules:
  - nonResourceURLs:
      - /healthz
      - /metrics
    verbs:
      - get
EOF

# 2. Create ClusterRoleBinding
kubectl create clusterrolebinding monitoring-endpoints-crb \
  --clusterrole=monitoring-endpoints-cr \
  --user=prom-collector

# 3. Verification
kubectl auth can-i get /healthz --as=prom-collector # Expected: yes
kubectl auth can-i get /metrics --as=prom-collector # Expected: yes
kubectl auth can-i get /pods --as=prom-collector    # Expected: no
```
</details>

---

### Task 11: Complex JSONPath Data Extraction (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Extract the name and pod IP of all pods running in the `kube-system` namespace.
Format the output as `<POD_NAME>:<POD_IP>` (one per line) and save the result to `/opt/system-pod-ips.txt`.
Sort the lines alphabetically by pod name.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# Solution using kubectl jsonpath:
kubectl get pods -n kube-system \
  --sort-by=.metadata.name \
  -o jsonpath='{range .items[*]}{.metadata.name}{":"}{.status.podIP}{"\n"}{end}' \
  > /opt/system-pod-ips.txt

# Verification:
cat /opt/system-pod-ips.txt
```
</details>

---

### Task 12: Ingress with Path-Based Routing & Default Backend (Weight: 6%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
In namespace `app-routing`, create an Ingress named `portal-ingress`:
- IngressClassName: `nginx`
- Host: `portal.company.com`
- Paths:
  - Path `/api` (PathType: `Prefix`) routed to Service `api-svc` on port `8000`.
  - Path `/web` (PathType: `Prefix`) routed to Service `web-svc` on port `80`.
- Default Backend: If no path matches, route traffic to Service `fallback-svc` on port `8080`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Create namespace
kubectl create namespace app-routing --dry-run=client -o yaml | kubectl apply -f -

# 2. Create Ingress manifest
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: portal-ingress
  namespace: app-routing
spec:
  ingressClassName: nginx
  defaultBackend:
    service:
      name: fallback-svc
      port:
        number: 8080
  rules:
    - host: portal.company.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-svc
                port:
                  number: 8000
          - path: /web
            pathType: Prefix
            backend:
              service:
                name: web-svc
                port:
                  number: 80
EOF

# 3. Verification
kubectl describe ingress portal-ingress -n app-routing
```
</details>

---

### Task 13: Topology Spread Constraints for Pod HA (Weight: 6%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
In namespace `ha-workloads`, create a Deployment named `ha-web`:
- Replicas: `4`
- Pod label: `app: ha-web`
- Container image: `nginx:1.25-alpine`
- Configure `topologySpreadConstraints` so that pods are evenly distributed across nodes using the topology key `kubernetes.io/hostname`:
  - `maxSkew`: `1`
  - `topologyKey`: `kubernetes.io/hostname`
  - `whenUnsatisfiable`: `DoNotSchedule`
  - Match pods with label `app: ha-web`

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Create namespace
kubectl create namespace ha-workloads --dry-run=client -o yaml | kubectl apply -f -

# 2. Create Deployment manifest
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ha-web
  namespace: ha-workloads
spec:
  replicas: 4
  selector:
    matchLabels:
      app: ha-web
  template:
    metadata:
      labels:
        app: ha-web
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: ha-web
      containers:
        - name: nginx
          image: nginx:1.25-alpine
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
EOF

# 3. Verification
kubectl rollout status deployment ha-web -n ha-workloads
kubectl get pods -n ha-workloads -o wide
```
</details>

---

### Task 14: Batch Processing Job with Deadlines (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
In namespace `batch-ops`, create a Job named `db-migration-job`:
- Image: `busybox:1.36`
- Command: `["sh", "-c", "echo Starting migration... && sleep 5 && echo Complete!"]`
- Completions: `3`
- Parallelism: `2`
- ActiveDeadlineSeconds: `100`
- BackoffLimit: `2`
- Pod restartPolicy: `Never`

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Create namespace
kubectl create namespace batch-ops --dry-run=client -o yaml | kubectl apply -f -

# 2. Create Job manifest
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-job
  namespace: batch-ops
spec:
  completions: 3
  parallelism: 2
  activeDeadlineSeconds: 100
  backoffLimit: 2
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migration
          image: busybox:1.36
          command: ["sh", "-c", "echo Starting migration... && sleep 5 && echo Complete!"]
EOF

# 3. Verification
kubectl wait --for=condition=complete job/db-migration-job -n batch-ops --timeout=60s
kubectl get job db-migration-job -n batch-ops
```
</details>

---

### Task 15: Troubleshoot CrashLoopBackOff Application (Weight: 6%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
A Pod named `cart-service` in namespace `ecommerce` is failing with status `CrashLoopBackOff`.
1. Inspect the pod logs and events to find the root cause.
2. The pod fails due to an incorrect command or missing environment variable referenced in its configuration.
3. Fix the Pod specification so that it runs successfully and reaches `Running` status with `1/1 Ready`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Describe pod and check events
kubectl describe pod cart-service -n ecommerce

# 2. Check current and previous logs
kubectl logs cart-service -n ecommerce
kubectl logs cart-service -n ecommerce --previous

# 3. Export YAML to make changes
kubectl get pod cart-service -n ecommerce -o yaml > /tmp/cart-service.yaml

# 4. Common exam root causes:
# - Command typo (e.g. ["/bin/bash", "-c", "..."] on alpine where bash is not installed) -> Change to ["/bin/sh", "-c", "..."]
# - Missing required configmap/secret key ref in envFrom
# - Liveness probe checking wrong port (e.g. port 8080 when app listens on 80)

# Edit /tmp/cart-service.yaml, then replace:
kubectl replace --force -f /tmp/cart-service.yaml

# 5. Verification
kubectl wait --for=condition=Ready pod/cart-service -n ecommerce --timeout=30s
```
</details>

---

### Task 16: Audit Cluster for Unhealthy Pods (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Identify all Pods across ALL namespaces that are NOT in the `Running` or `Completed` state.
Output each unhealthy pod in the format:
`<NAMESPACE> <POD_NAME> <STATUS>`
Save the output to `/opt/unhealthy-pods.txt`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# Solution using awk filter:
kubectl get pods --all-namespaces --no-headers | \
  awk '$4 != "Running" && $4 != "Completed" {print $1, $2, $4}' \
  > /opt/unhealthy-pods.txt

# Verification:
cat /opt/unhealthy-pods.txt
```
</details>

---

### Task 17: ETCD Cluster Health Check & Member List (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Perform an operational health check on the active etcd cluster:
1. Use `etcdctl` with the appropriate PKI certificates (`/etc/kubernetes/pki/etcd/ca.crt`, `server.crt`, `server.key`) to verify the endpoint health of `https://127.0.0.1:2379`.
2. Extract the member list and write the table output to `/opt/etcd-members.txt`.
3. Extract the endpoint status in JSON format and write the output to `/opt/etcd-status.json`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**

```bash
# 1. Set environment variables for etcdctl
export ETCDCTL_API=3
export CACERT=/etc/kubernetes/pki/etcd/ca.crt
export CERT=/etc/kubernetes/pki/etcd/server.crt
export KEY=/etc/kubernetes/pki/etcd/server.key

# 2. Check endpoint health
etcdctl --cacert=$CACERT --cert=$CERT --key=$KEY \
  --endpoints=https://127.0.0.1:2379 endpoint health

# 3. Write member list table to /opt/etcd-members.txt
etcdctl --cacert=$CACERT --cert=$CERT --key=$KEY \
  --endpoints=https://127.0.0.1:2379 \
  --write-out=table member list > /opt/etcd-members.txt

# 4. Write endpoint status in JSON to /opt/etcd-status.json
etcdctl --cacert=$CACERT --cert=$CERT --key=$KEY \
  --endpoints=https://127.0.0.1:2379 \
  --write-out=json endpoint status > /opt/etcd-status.json

# 5. Verification
cat /opt/etcd-members.txt
cat /opt/etcd-status.json
```
</details>
