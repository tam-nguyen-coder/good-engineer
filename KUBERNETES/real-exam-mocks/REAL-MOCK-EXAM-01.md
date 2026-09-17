# 📝 CKA Real Exam Mock — Set 1: Standard Core Certification Exam

> **Exam Duration:** 120 Minutes · **Total Tasks:** 17 Tasks · **Passing Score:** 66% (Target: ≥ 85%)
> **Rules:** Authentic performance-based English tasks crawled from real exam experiences & Killer.sh scenarios.
> Always run the `kubectl config use-context` command at the beginning of each task!

---

### Task 1: RBAC Role & RoleBinding (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
In the namespace `development`, create a `Role` named `developer-role` that grants permissions to `create`, `get`, `list`, and `delete` on `pods` and `deployments`.
Then, create a `RoleBinding` named `developer-binding` that binds this `developer-role` to the user `john` in the same namespace.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. Ensure namespace exists
kubectl create namespace development --dry-run=client -o yaml | kubectl apply -f -

# 2. Create the Role
kubectl create role developer-role \
  --verb=create,get,list,delete \
  --resource=pods,deployments.apps \
  -n development

# 3. Create the RoleBinding
kubectl create rolebinding developer-binding \
  --role=developer-role \
  --user=john \
  -n development

# 4. Verification
kubectl auth can-i create pods -n development --as=john        # Expected: yes
kubectl auth can-i delete deployments -n development --as=john # Expected: yes
kubectl auth can-i get secrets -n development --as=john        # Expected: no
```
</details>

---

### Task 2: Troubleshooting a Worker Node (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
A worker node named `node01` is currently in the `NotReady` state. Investigate why this node is not ready, fix the underlying issue, and ensure the node returns to the `Ready` status.
Do not reboot the node.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. Inspect node conditions from master
kubectl describe node node01

# 2. SSH to node01
ssh node01

# 3. Check kubelet service status and logs
sudo systemctl status kubelet
sudo journalctl -u kubelet -e --no-pager -n 30

# 4. Common real-exam issues:
# Case A: Kubelet is stopped or crashed
sudo systemctl daemon-reload
sudo systemctl enable --now kubelet

# Case B: Container runtime containerd is stopped
sudo systemctl status containerd
sudo systemctl restart containerd
sudo systemctl restart kubelet

# Case C: Kubelet config points to invalid containerd socket in /var/lib/kubelet/kubeadm-flags.env
# Ensure: --container-runtime-endpoint=unix:///run/containerd/containerd.sock

# 5. Verify on node
sudo systemctl status kubelet # Active: active (running)

# 6. Exit back to master and verify
exit
kubectl get nodes
# node01 should now be in Ready state
```
</details>

---

### Task 3: Kubeadm Cluster Upgrade (Weight: 11%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Upgrade the Kubernetes cluster from version `1.34.0` to `1.35.0`.
First, upgrade the control plane node `controlplane`.
Then, upgrade the worker node `node01`.
Make sure to drain both nodes safely before upgrading and uncordon them after upgrading.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# ==================== STEP 1: UPGRADE CONTROL PLANE ====================
# Drain controlplane
kubectl drain controlplane --ignore-daemonsets

# Upgrade kubeadm tool
sudo apt-mark unhold kubeadm
sudo apt-get update && sudo apt-get install -y kubeadm=1.35.0-1.1
sudo apt-mark hold kubeadm

# Verify and plan upgrade
sudo kubeadm upgrade plan
sudo kubeadm upgrade apply v1.35.0 -y

# Upgrade kubelet and kubectl
sudo apt-mark unhold kubelet kubectl
sudo apt-get update && sudo apt-get install -y kubelet=1.35.0-1.1 kubectl=1.35.0-1.1
sudo apt-mark hold kubelet kubectl

# Restart kubelet and uncordon
sudo systemctl daemon-reload
sudo systemctl restart kubelet
kubectl uncordon controlplane

# ==================== STEP 2: UPGRADE WORKER NODE ====================
# Drain node01 from master
kubectl drain node01 --ignore-daemonsets --delete-emptydir-data --force

# SSH to worker node01
ssh node01

# Upgrade kubeadm
sudo apt-mark unhold kubeadm
sudo apt-get update && sudo apt-get install -y kubeadm=1.35.0-1.1
sudo apt-mark hold kubeadm

# Upgrade node configuration (DO NOT USE apply HERE)
sudo kubeadm upgrade node

# Upgrade kubelet and kubectl on worker
sudo apt-mark unhold kubelet kubectl
sudo apt-get update && sudo apt-get install -y kubelet=1.35.0-1.1 kubectl=1.35.0-1.1
sudo apt-mark hold kubelet kubectl

# Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet
exit

# Uncordon node01 from master
kubectl uncordon node01

# Verification
kubectl get nodes
# Both controlplane and node01 should show v1.35.0 and Ready
```
</details>

---

### Task 4: ETCD Database Backup & Restore (Weight: 11%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
First, take a snapshot backup of the current `etcd` database running on the control plane and save it to `/opt/etcd-backup.db`.
Next, restore the `etcd` database from an existing backup snapshot located at `/opt/pre-upgrade-backup.db` into a new data directory `/var/lib/etcd-restored`.
Update the static pod configuration so the cluster uses the restored database.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. Identify etcd certificates from static manifest:
cat /etc/kubernetes/manifests/etcd.yaml | grep -E "cert-file|key-file|trusted-ca-file"
# --cacert=/etc/kubernetes/pki/etcd/ca.crt
# --cert=/etc/kubernetes/pki/etcd/server.crt
# --key=/etc/kubernetes/pki/etcd/server.key

# 2. TAKE BACKUP SNAPSHOT:
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /opt/etcd-backup.db

# Verify backup file:
ETCDCTL_API=3 etcdctl --write-out=table snapshot status /opt/etcd-backup.db

# 3. RESTORE FROM EXISTING SNAPSHOT to new directory:
ETCDCTL_API=3 etcdctl snapshot restore /opt/pre-upgrade-backup.db \
  --data-dir=/var/lib/etcd-restored

# 4. Update Static Pod manifest:
sudo vim /etc/kubernetes/manifests/etcd.yaml
# Find the volume named "etcd-data" and change hostPath:
# volumes:
# - hostPath:
#     path: /var/lib/etcd-restored   <-- CHANGE THIS LINE
#     type: DirectoryOrCreate
#   name: etcd-data

# 5. Verification:
# Wait 30 seconds for Kubelet to restart the etcd static pod
kubectl get nodes
kubectl get pods -A
```
</details>

---

### Task 5: NetworkPolicy Microsegmentation (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
In namespace `backend-tier`, create a `NetworkPolicy` named `secure-db-policy` that secures the pod with label `role: database`.
Requirements:
1. Allow ingress traffic ONLY from pods with label `role: backend` on TCP port `5432`.
2. Block all other ingress traffic to the database pod.
3. Allow all egress traffic so that DNS queries and external telemetry are not disrupted.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
Create file `secure-db-policy.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: secure-db-policy
  namespace: backend-tier
spec:
  podSelector:
    matchLabels:
      role: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: backend
    ports:
    - protocol: TCP
      port: 5432
```

Apply and verify:
```bash
kubectl apply -f secure-db-policy.yaml

# Verification
kubectl describe netpol secure-db-policy -n backend-tier
```
</details>

---

### Task 6: Ingress with TLS Termination (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
Create an Ingress resource named `secure-ingress` in namespace `ecommerce`.
Requirements:
- IngressClassName: `nginx`
- Host: `shop.example.com`
- Path `/products` (Prefix) routes to service `product-service` on port `8080`.
- Path `/orders` (Exact) routes to service `order-service` on port `9000`.
- Configure TLS termination for `shop.example.com` using the existing Secret `shop-tls-cert`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-ingress
  namespace: ecommerce
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - shop.example.com
    secretName: shop-tls-cert
  rules:
  - host: shop.example.com
    http:
      paths:
      - path: /products
        pathType: Prefix
        backend:
          service:
            name: product-service
            port:
              number: 8080
      - path: /orders
        pathType: Exact
        backend:
          service:
            name: order-service
            port:
              number: 9000
```

Apply and verify:
```bash
kubectl apply -f secure-ingress.yaml
kubectl get ingress secure-ingress -n ecommerce
```
</details>

---

### Task 7: PersistentVolume & PVC with Dynamic Expansion (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
Create a PersistentVolume named `app-pv` with the following specs:
- Capacity: `2Gi`
- AccessModes: `ReadWriteOnce`
- ReclaimPolicy: `Retain`
- StorageClassName: `local-disk`
- HostPath: `/data/app-storage`

Then, create a PersistentVolumeClaim named `app-pvc` in namespace `finance` requesting `1Gi` using `storageClassName: local-disk` and `accessModes: ReadWriteOnce`.
Ensure the PVC binds to `app-pv`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
Create `pv-pvc.yaml`:
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: app-pv
spec:
  capacity:
    storage: 2Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-disk
  hostPath:
    path: /data/app-storage
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-pvc
  namespace: finance
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: local-disk
  resources:
    requests:
      storage: 1Gi
```

Apply and verify:
```bash
kubectl apply -f pv-pvc.yaml

# Verify Binding:
kubectl get pv app-pv
kubectl get pvc app-pvc -n finance
# Status of both should be Bound
```
</details>

---

### Task 8: Native Sidecar Container (K8s v1.29+) (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster3
```

**Task:**
Create a Pod named `batch-processor` in namespace `default`.
The Pod must have:
1. An init container named `log-shipper` using image `busybox:1.28` with `restartPolicy: Always`. It should execute command `sh -c "tail -F /var/log/app.log"`. Mount the volume `log-volume` to `/var/log`.
2. A main container named `worker` using image `busybox:1.28` that executes command `sh -c "for i in $(seq 1 30); do echo \"processing $i\" >> /var/log/app.log; sleep 1; done"`. Mount volume `log-volume` to `/var/log`.
3. An `emptyDir` volume named `log-volume`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
Create `native-sidecar.yaml`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: batch-processor
  namespace: default
spec:
  initContainers:
  - name: log-shipper
    image: busybox:1.28
    restartPolicy: Always   # <-- Native sidecar container attribute
    command: ["sh", "-c", "tail -F /var/log/app.log"]
    volumeMounts:
    - name: log-volume
      mountPath: /var/log
  containers:
  - name: worker
    image: busybox:1.28
    command: ["sh", "-c", "for i in $(seq 1 30); do echo \"processing $i\" >> /var/log/app.log; sleep 1; done"]
    volumeMounts:
    - name: log-volume
      mountPath: /var/log
  volumes:
  - name: log-volume
    emptyDir: {}
```

Apply and verify:
```bash
kubectl apply -f native-sidecar.yaml
kubectl get pod batch-processor
# Should show 2/2 containers running
kubectl logs batch-processor -c log-shipper
```
</details>

---

### Task 9: Troubleshooting Broken API Server Static Pod (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster3
```

**Task:**
`kubectl` commands on the control plane node fail with:
`The connection to the server 127.0.0.1:6443 was refused - did you specify the right host or port?`
SSH to the control plane, diagnose why the `kube-apiserver` static pod is failing to start, resolve the issue, and verify that `kubectl` functions properly.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. SSH to control plane
ssh controlplane

# 2. Check if kubelet is running
sudo systemctl status kubelet

# 3. Check container runtime for exited apiserver containers
sudo crictl ps -a | grep apiserver
# Grab the container ID of the exited container

# 4. View container logs
sudo crictl logs <container-id>
# Output reveals error, e.g.: "unknown flag: --invalid-flag-example"
# or bad file path for a client cert

# 5. Edit static manifest:
sudo vim /etc/kubernetes/manifests/kube-apiserver.yaml
# Remove the invalid flag or correct the certificate path

# 6. Wait 15 seconds for Kubelet to recreate the static pod
kubectl get nodes
# Should return 200 OK with nodes list
```
</details>

---

### Task 10: Node Drain for Maintenance (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster3
```

**Task:**
Prepare node `worker-2` for maintenance by draining all workloads safely.
Ensure pods containing `emptyDir` volumes are evicted, and `DaemonSet` pods are ignored.
Do not delete the node from the cluster.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# Execute safe drain
kubectl drain worker-2 \
  --ignore-daemonsets \
  --delete-emptydir-data \
  --force

# Verify node status
kubectl get nodes
# worker-2 status must show: Ready,SchedulingDisabled
```
</details>

---

### Task 11: JSONPath Query to Extract Information (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Write a JSONPath query using `kubectl` to retrieve the `internalIP` of all nodes in the cluster.
Sort the output by node creation timestamp, and write the output into `/opt/node-ips.txt`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
kubectl get nodes -o jsonpath='{range .items[*]}{.status.addresses[?(@.type=="InternalIP")].address}{"\n"}{end}' --sort-by=.metadata.creationTimestamp > /opt/node-ips.txt

# Verification
cat /opt/node-ips.txt
```
</details>

---

### Task 12: CertificateSigningRequest (CSR) & User Onboarding (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
A developer named `developer-sam` generated a private key and a CSR file located at `/root/sam.csr`.
Create a Kubernetes `CertificateSigningRequest` resource named `sam-csr` for this request with signerName `kubernetes.io/kube-apiserver-client`.
Approve the CSR using `kubectl`.
Finally, extract the approved certificate from the CSR and save it to `/root/sam.crt`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. Base64 encode the CSR file:
CSR_BASE64=$(cat /root/sam.csr | tr -d '\n' | base64 | tr -d '\n')

# 2. Create the CSR object:
cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: sam-csr
spec:
  request: ${CSR_BASE64}
  signerName: kubernetes.io/kube-apiserver-client
  usages:
  - client auth
EOF

# 3. Approve the CSR:
kubectl certificate approve sam-csr

# 4. Extract the certificate:
kubectl get csr sam-csr -o jsonpath='{.status.certificate}' | base64 -d > /root/sam.crt

# Verification
openssl x509 -in /root/sam.crt -text -noout | grep "Subject:"
```
</details>

---

### Task 13: Expose Deployment as NodePort Service (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
Expose the existing deployment `frontend-ui` in namespace `web` as a `NodePort` service named `frontend-svc`.
The service must listen on port `80`, route to targetPort `80`, and be accessible on nodePort `30080`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# Expose imperative template
kubectl expose deployment frontend-ui \
  --name=frontend-svc \
  --namespace=web \
  --type=NodePort \
  --port=80 \
  --target-port=80 \
  --dry-run=client -o yaml > svc.yaml

# Add nodePort: 30080 under ports:
vim svc.yaml
# ports:
# - port: 80
#   targetPort: 80
#   nodePort: 30080

kubectl apply -f svc.yaml

# Verify
kubectl get svc frontend-svc -n web
```
</details>

---

### Task 14: Pod PriorityClass and Preemption (Weight: 7%)

**Context:**
```bash
kubectl config use-context k8s-cluster2
```

**Task:**
Create a `PriorityClass` named `critical-workload` with a value of `1000000` and `preemptionPolicy: PreemptLowerPriority`.
Then, create a pod named `high-priority-pod` using image `nginx` that utilizes this `critical-workload` priority class.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: critical-workload
value: 1000000
preemptionPolicy: PreemptLowerPriority
globalDefault: false
description: "Mission critical priority class"
---
apiVersion: v1
kind: Pod
metadata:
  name: high-priority-pod
spec:
  priorityClassName: critical-workload
  containers:
  - name: nginx
    image: nginx
```

Apply and verify:
```bash
kubectl apply -f priority-setup.yaml
kubectl get pod high-priority-pod
```
</details>

---

### Task 15: Pod Security Admission Enforcement (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster3
```

**Task:**
Enable Pod Security Standards on the namespace `secure-production`.
Enforce the `restricted` standard at the latest version.
Ensure that warning messages are emitted for the `baseline` profile.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
kubectl label --overwrite namespace secure-production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest \
  pod-security.kubernetes.io/warn=baseline \
  pod-security.kubernetes.io/warn-version=latest

# Verification
kubectl get ns secure-production --show-labels
```
</details>

---

### Task 16: ResourceQuota & LimitRange (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster3
```

**Task:**
In namespace `team-billing`, create a `ResourceQuota` named `compute-quota` restricting:
- Max CPU requests: `2`
- Max Memory requests: `2Gi`
- Max Pods count: `5`

Then, create a `LimitRange` named `default-limits` in `team-billing` setting the default memory request to `128Mi` and memory limit to `256Mi` for all containers.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: team-billing
spec:
  hard:
    requests.cpu: "2"
    requests.memory: "2Gi"
    pods: "5"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: team-billing
spec:
  limits:
  - default:
      memory: "256Mi"
    defaultRequest:
      memory: "128Mi"
    type: Container
```

Apply and verify:
```bash
kubectl apply -f quota-limits.yaml
kubectl describe quota compute-quota -n team-billing
kubectl describe limitrange default-limits -n team-billing
```
</details>

---

### Task 17: Top Resource Consuming Pods (Weight: 4%)

**Context:**
```bash
kubectl config use-context k8s-cluster1
```

**Task:**
Identify the Pod in the namespace `monitoring` that is consuming the highest amount of **Memory**.
Write the name of this single pod into the file `/opt/highest-memory-pod.txt`.

<details>
<summary>🔍 Click to view Solution & Verification</summary>

**Solution:**
```bash
# 1. Inspect top pods sorted by memory:
kubectl top pods -n monitoring --sort-by=memory

# 2. Extract top pod name without headers:
kubectl top pods -n monitoring --sort-by=memory --no-headers | head -n 1 | awk '{print $1}' > /opt/highest-memory-pod.txt

# Verification
cat /opt/highest-memory-pod.txt
```
</details>

---

## 🏆 Scoring Checklist for Set 1

| Task # | Topic | Weight | Completed? | Verified? |
|---|---|---|---|---|
| **1** | RBAC Role & Binding | 4% | [ ] | [ ] |
| **2** | Node NotReady Troubleshooting | 7% | [ ] | [ ] |
| **3** | Kubeadm Upgrade Cluster | 11% | [ ] | [ ] |
| **4** | ETCD Snapshot Save & Restore | 11% | [ ] | [ ] |
| **5** | NetworkPolicy Microsegmentation | 7% | [ ] | [ ] |
| **6** | Ingress Routing & TLS | 7% | [ ] | [ ] |
| **7** | PV & PVC Binding | 4% | [ ] | [ ] |
| **8** | Native Sidecar Container | 4% | [ ] | [ ] |
| **9** | API Server Static Pod Crash | 7% | [ ] | [ ] |
| **10** | Node Drain & Maintenance | 4% | [ ] | [ ] |
| **11** | JSONPath Query Extraction | 4% | [ ] | [ ] |
| **12** | CSR Creation & Approval | 7% | [ ] | [ ] |
| **13** | Service NodePort Expose | 4% | [ ] | [ ] |
| **14** | PriorityClass Preemption | 7% | [ ] | [ ] |
| **15** | Pod Security Admission | 4% | [ ] | [ ] |
| **16** | ResourceQuota & LimitRange | 4% | [ ] | [ ] |
| **17** | Kubectl Top Memory Extraction | 4% | [ ] | [ ] |
| **TOTAL** | | **100%** | **Target: ≥ 85%** | |
