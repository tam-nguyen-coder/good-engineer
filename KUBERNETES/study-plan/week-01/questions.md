# 📝 Practice Questions — Week 1: K8s Architecture, Control Plane & `kubectl` Imperative

> **23 Scenario Questions** · Authentic CKA / CKAD exam style · Comprehensive Week 1 assessment, including **extension interfaces (CRI / CNI / CSI)**.
> 🔒 **Detailed answers & explanations are in a separate file:** [answers.md](answers.md). Attempt all questions before checking!
> Taxonomy Tag: `[Domain · Topic · Question Type]`. Multi = multiple-response (number to choose is stated).
> Back to [Week 1 Plan](README.md) · [Labs](labs.md) · [Master Plan](../../K8S-STUDY-PLAN.md)

---

### Question 1 — `[ARCH · Control Plane · Single]`
A DevOps engineer discovers that `kube-scheduler` on the Control Plane node has crashed unexpectedly. While the scheduler remains down, which of the following statements ACCURATELY describes the behavior of the cluster?
- A. All existing Pods on worker nodes will immediately terminate due to lost communication with the Control Plane.
- B. Running Pods will continue to operate normally; however, any newly created Pods will remain stuck in the `Pending` state indefinitely.
- C. Kubelet on each worker node will automatically take over the scheduling duty and assign new Pods to the node with the most available memory.
- D. Executing `kubectl get pods` will return an HTTP 500 Internal Server Error and fail to connect to the API server.

---

### Question 2 — `[ARCH · etcd · Single]`
A Kubernetes High Availability (HA) cluster runs with a 5-node `etcd` cluster. What is the MAXIMUM number of etcd nodes that can fail simultaneously without the cluster losing quorum and still allowing write operations?
- A. 1 node
- B. 2 nodes
- C. 3 nodes
- D. 4 nodes

---

### Question 3 — `[ARCH · Kubelet & CRI · Single]`
On a worker node running Kubernetes v1.35, which component is directly responsible for communicating with the Container Runtime via the CRI Unix socket (`/run/containerd/containerd.sock`) to pull container images and manage the container lifecycle inside a Pod?
- A. `kube-proxy`
- B. `kube-apiserver`
- C. `kubelet`
- D. `kube-controller-manager`

---

### Question 4 — `[WORKLOAD · Pod Lifecycle · Single]`
A newly created Pod is reported in the `Pending` state. When an administrator inspects `kubectl describe pod <name>`, the `Events` section shows: `0/3 nodes are available: 3 Insufficient memory`. What is the primary cause of this condition?
- A. The container runtime on all nodes crashed due to out-of-memory.
- B. `kube-scheduler` could not find any node where unreserved/allocatable memory is greater than or equal to the Pod's `resources.requests.memory`.
- C. The container process terminated with an `OOMKilled` error (Exit Code 137) during startup.
- D. The root filesystem disk (`/var/lib/containerd`) on all worker nodes is 100% full.

---

### Question 5 — `[WORKLOAD · Init Containers · Single]`
A Pod specification defines two `initContainers` (`init-1`, `init-2`) and one primary application container (`app-main`). If `init-1` exits with Exit Code `1`, what does Kubelet do by default?
- A. Kubelet skips `init-1`, executes `init-2`, and starts `app-main`.
- B. Kubelet starts `app-main` immediately and logs a warning event in the Pod's event log.
- C. Kubelet halts the Pod startup sequence and restarts `init-1` according to the Pod's `restartPolicy` until it succeeds (Exit Code 0).
- D. Kubelet permanently deletes the Pod object from etcd.

---

### Question 6 — `[WORKLOAD · Native Sidecar K8s 1.28+ · Single]`
Since Kubernetes v1.28 (and GA in v1.29+), how is a "Native Sidecar Container" declared in the Pod specification?
- A. In a dedicated top-level array named `spec.sidecars[]`.
- B. Inside `spec.initContainers[]` with the field `restartPolicy: Always`.
- C. Inside `spec.containers[]` with the annotation `k8s.io/sidecar: "true"`.
- D. Inside `spec.ephemeralContainers[]`.

---

### Question 7 — `[CLI · Imperative · Single]`
In the CKA exam, which of the following commands is the FASTEST way to generate a starter `pod.yaml` manifest for an Nginx Pod WITHOUT creating any resource on the cluster?
- A. `kubectl create pod nginx --image=nginx -o yaml`
- B. `kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml`
- C. `kubectl run nginx --image=nginx --export -o yaml > pod.yaml`
- D. `kubectl get pod nginx --template='{{.spec}}' > pod.yaml`

---

### Question 8 — `[ARCH · Static Pods · Single]`
An engineer places a manifest file `nginx.yaml` into the `/etc/kubernetes/manifests/` directory on a worker node named `node01`. Which statement regarding this Pod is TRUE?
- A. This Pod is managed and scheduled by `kube-scheduler`.
- B. The Pod name registered on the API server will automatically have the node name appended as a suffix (e.g., `nginx-node01`).
- C. Running `kubectl delete pod nginx-node01` will permanently remove the Pod from the node.
- D. The static Pod will automatically failover to another node if `node01` crashes.

---

### Question 9 — `[NET · kube-proxy · Single]`
What is the primary responsibility of `kube-proxy` in Kubernetes cluster networking?
- A. Dynamically assigning IP addresses to each Pod using the DHCP protocol.
- B. Resolving internal domain names for cluster Services over UDP port 53.
- C. Maintaining network routing rules (via iptables or IPVS) to forward traffic sent to a Service ClusterIP to backend Pod endpoints.
- D. Providing mutual TLS (mTLS) certificates for container-to-container communication.

---

### Question 10 — `[CLI · JSONPath · Single]`
Which command uses correct JSONPath syntax to extract and print the name and pod IP of all Pods in the `default` namespace?
- A. `kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.podIP}{"\n"}{end}'`
- B. `kubectl get pods --jsonpath='{.items.name} {.items.ip}'`
- C. `kubectl get pods -o custom-columns=NAME:.name,IP:.ip`
- D. `kubectl get pods -o jsonpath='{items.pod[*].ip}'`

---

### Question 11 — `[ARCH · Communication · Single]`
Which of the following communication pairs interacts DIRECTLY with each other WITHOUT going through the `kube-apiserver`?
- A. `kube-scheduler` ↔ `kubelet`
- B. `kube-controller-manager` ↔ `etcd`
- C. `kubelet` ↔ `containerd` (via CRI Unix Domain Socket)
- D. `kubectl` ↔ `etcd`

---

### Question 12 — `[ARCH · API Server · Multi — Choose 2]`
When a resource creation request is received by `kube-apiserver`, what is the processing order? (Choose two correct statements).
- A. The Authentication phase occurs BEFORE the Authorization phase.
- B. Validating Admission Controllers always execute BEFORE Mutating Admission Controllers.
- C. Mutating Admission Controllers execute BEFORE Validating Admission Controllers.
- D. Data is persisted to `etcd` before Admission Controllers execute.
- E. Authorization occurs before Authentication.

---

### Question 13 — `[WORKLOAD · Pod Lifecycle · Single]`
A container inside a Pod terminates abruptly with Exit Code `137`. What should the administrator conclude regarding the cause of container termination?
- A. The application encountered an unhandled syntax error or missing file (Runtime Error).
- B. The container was terminated by the Linux kernel via `SIGKILL` due to exceeding its memory limit (`OOMKilled - Out Of Memory`).
- C. The container received a graceful `SIGTERM` shutdown signal from Kubelet.
- D. The container's network port conflicted with another process running on the host.

---

### Question 14 — `[ARCH · Controller Manager · Single]`
If the `kube-controller-manager` process terminates on the Control Plane, what happens when an existing Pod belonging to a `Deployment` is manually deleted with `kubectl delete pod`?
- A. The API server rejects the pod deletion request.
- B. The Pod is successfully deleted, but no replacement Pod is created to maintain the desired replica count.
- C. The worker node hosting the deleted Pod reboots automatically.
- D. Kubelet on the worker node immediately creates a new replacement Pod.

---

### Question 15 — `[CLI · Imperative · Single]`
An exam question states: "Create a Deployment named `web-api` running image `nginx:1.24`, with 4 replicas, in namespace `production`". Which command satisfies this requirement in a SINGLE line?
- A. `kubectl run web-api --image=nginx:1.24 --replicas=4 -n production`
- B. `kubectl create deployment web-api --image=nginx:1.24 --replicas=4 -n production`
- C. `kubectl apply deployment web-api --image=nginx:1.24 --replicas=4 -n production`
- D. `kubectl new deployment web-api --image=nginx:1.24 -r 4 -n production`

---

### Question 16 — `[WORKLOAD · PodSpec · Single]`
Two containers residing within the same Pod need to share temporary log files. What is the recommended, lightweight Kubernetes approach?
- A. Configure a `hostPath` volume pointing to `/tmp` on the host worker node.
- B. Define a volume of type `emptyDir: {}` and mount it into both containers at their respective directory paths.
- C. Configure a PersistentVolume backed by an external NFS share.
- D. Transmit files through the API server using a binary ConfigMap.

---

### Question 17 — `[WORKLOAD · Pod Lifecycle · Single]`
In a Pod specification, what does the parameter `terminationGracePeriodSeconds` specify?
- A. The duration Kubelet waits before attempting to restart a container in `CrashLoopBackOff`.
- B. The duration granted to a container between receiving `SIGTERM` and being forcibly killed via `SIGKILL`.
- C. The maximum allowed time for pulling a container image from a remote registry.
- D. The initial delay before Kubelet initiates the first Liveness probe check.

---

### Question 18 — `[ARCH · Certificates · Single]`
By default in a cluster initialized with `kubeadm`, where are the core PKI certificates stored on the Control Plane node?
- A. `/var/log/kubernetes/certs`
- B. `/etc/kubernetes/pki`
- C. `/usr/local/share/k8s/ssl`
- D. `/etc/ssl/kubernetes/etcd`

---

### Question 19 — `[CLI · Kubectl Config · Single]`
During the CKA exam, which command sets the default working namespace of the current context to `finance`, avoiding the need to pass `-n finance` with every subsequent command?
- A. `kubectl switch namespace finance`
- B. `kubectl set ns finance`
- C. `kubectl config set-context --current --namespace=finance`
- D. `kubectl use-namespace finance`

---

### Question 20 — `[WORKLOAD · Multi-container · Single]`
In multi-container Pod design patterns, what is the primary purpose of an "Ambassador Container"?
- A. Acting as a local proxy that abstracts connections to external services (e.g., masking database sharding or a Redis cluster from the main container).
- B. Collecting and reformatting raw logs from the primary container before shipping them to a centralized logging system.
- C. Executing cleanup scripts before the Pod is terminated.
- D. Ensuring the primary container starts only after an external database has opened its network port.

---

### Question 21 — `[ARCH · Extension interfaces · Single]`
A newly joined worker node reports `NotReady`. `journalctl -u kubelet` repeatedly logs:
`Network plugin returns error: cni plugin not initialized`. Which extension interface is at fault, and where do you look first?
- A. CRI — inspect `/etc/containerd/config.toml` and restart `containerd`.
- B. CNI — check that a network plugin config exists in `/etc/cni/net.d/`, its binaries exist in `/opt/cni/bin/`, and the CNI DaemonSet pods in `kube-system` are Running.
- C. CSI — verify `kubectl get csidrivers` lists a registered driver.
- D. The Device Plugin interface — the node is missing its device plugin registration socket.

---

### Question 22 — `[ARCH · CNI capability · Single]`
A team applies a `default-deny-all` NetworkPolicy to their namespace on a cluster running plain **Flannel**. The object is accepted by the API server, but pods keep communicating freely in every direction. What explains this?
- A. The NetworkPolicy is missing a `policyTypes` field, so it is silently ignored.
- B. NetworkPolicy objects only take effect after `kube-proxy` is restarted on every node.
- C. NetworkPolicy enforcement is delegated to the CNI plugin. Plain Flannel does not implement it, so the policy is stored but never enforced — a CNI such as Calico or Cilium is required.
- D. `default-deny-all` policies only apply to egress traffic; ingress stays open by design.

---

### Question 23 — `[ARCH · CSI · Single]`
A PersistentVolumeClaim has been stuck in `Pending` for ten minutes. `kubectl describe pvc` shows no provisioning events at all — not even a failure. Which check most directly identifies the root cause?
- A. `kubectl get volumeattachments` — an existing attachment is blocking the new claim.
- B. Compare the PVC's `storageClassName` against `kubectl get storageclass`, and confirm the CSI driver behind that class's `provisioner` is installed and running (`kubectl get csidrivers`, plus its pods in `kube-system`).
- C. Increase the PVC's `resources.requests.storage`; claims under 1Gi are rejected silently.
- D. Delete and recreate the PVC with `accessModes: ReadWriteMany`.

