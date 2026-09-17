# 📝 Practice Questions — Week 3: Pod Scheduling, Affinity, Taints & QoS

> **19 Scenario Questions** · Authentic CKA & CKAD exam style · Focus on NodeSelector, NodeAffinity, PodAntiAffinity, Taints/Tolerations, Requests/Limits, QoS Classes & **Workload Autoscaling (HPA)**.
> 🔒 **Detailed answers & explanations are in a separate file:** [answers.md](answers.md). Attempt all questions before checking!
> Taxonomy Tag: `[Domain · Topic · Question Type]`.
> Back to [Week 3 Plan](README.md) · [Labs](labs.md) · [Master Plan](../../K8S-STUDY-PLAN.md)

---

### Question 1 — `[SCHED · Taints & Tolerations · Single]`
An administrator executes the following command on a worker node:
`kubectl taint nodes node-01 dedicated=finance:NoSchedule`
Which of the following statements ACCURATELY describes the behavior experienced by Pods that were already running on `node-01` prior to applying this Taint?
- A. Existing Pods are terminated and transition to `Terminating` immediately.
- B. Existing Pods continue running undisturbed on `node-01`; only new Pods lacking a matching toleration will be rejected by the scheduler.
- C. Kubelet restarts all existing Pods to evaluate them against the new toleration.
- D. All existing Pods on the node are placed into a suspended/paused state.

---

### Question 2 — `[SCHED · Taints NoExecute · Single]`
An engineer needs to apply a Taint to node `worker-gpu` such that: new Pods without a matching toleration cannot be scheduled on it, AND any currently running Pods on the node that lack a matching toleration **are evicted immediately**. Which Taint effect must be applied?
- A. `NoSchedule`
- B. `PreferNoSchedule`
- C. `NoExecute`
- D. `Strict`

---

### Question 3 — `[SCHED · Remove Taint · Single]`
Which command completely removes the Taint `app=analytics:NoSchedule` from worker node `node-02`?
- A. `kubectl untaint node node-02 app=analytics:NoSchedule`
- B. `kubectl taint nodes node-02 app=analytics:NoSchedule-`
- C. `kubectl delete taint node-02 app=analytics`
- D. `kubectl taint node node-02 app:NoSchedule --remove`

---

### Question 4 — `[SCHED · NodeAffinity Hard vs Soft · Single]`
A developer requires that their Pod **MUST** run exclusively on worker nodes located in availability zones `us-east-1a` or `us-east-1b`. If no nodes in those zones are available, the Pod should remain in `Pending` state rather than run on any other node. Which NodeAffinity block satisfies this requirement?
- A. `preferredDuringSchedulingIgnoredDuringExecution`
- B. `requiredDuringSchedulingIgnoredDuringExecution`
- C. `requiredDuringSchedulingRequiredDuringExecution`
- D. `allNodesMatchingSchedulingExecution`

---

### Question 5 — `[SCHED · PodAntiAffinity · Single]`
To guarantee High Availability, a platform administrator requires that replicas of Deployment `api-server` are never co-located on the same physical host (each worker node can host at most one `api-server` Pod). Which `topologyKey` must be specified in the `podAntiAffinity` configuration?
- A. `topologyKey: "kubernetes.io/os"`
- B. `topologyKey: "kubernetes.io/hostname"`
- C. `topologyKey: "kubernetes.io/arch"`
- D. `topologyKey: "kubernetes.io/role"`

---

### Question 6 — `[SCHED · QoS Classes · Single]`
A Pod specification contains two containers with the following resource configurations:
- Container 1: `requests: {cpu: "200m", memory: "256Mi"}`, `limits: {cpu: "200m", memory: "256Mi"}`
- Container 2: `requests: {cpu: "100m", memory: "128Mi"}`, `limits: {cpu: "100m", memory: "128Mi"}`
Which QoS (Quality of Service) class is automatically assigned to this Pod by Kubernetes?
- A. `BestEffort`
- B. `Burstable`
- C. `Guaranteed`
- D. `Critical`

---

### Question 7 — `[SCHED · QoS Eviction Order · Single]`
When a worker node experiences severe `MemoryPressure`, Kubelet initiates Pod eviction to safeguard the underlying operating system. Pods in which QoS class will be **evicted first** by Kubelet?
- A. `Guaranteed`
- B. `Burstable`
- C. `BestEffort`
- D. Pods running in the `kube-system` namespace

---

### Question 8 — `[SCHED · Resource Requests vs Limits · Single]`
What occurs when an application container inside a Pod exceeds its configured `limits.cpu` value?
- A. The container is immediately terminated with exit status `OOMKilled` (Exit Code 137).
- B. The container experiences CPU throttling via Linux cgroups CFS bandwidth enforcement, but its process remains alive.
- C. The worker node hosting the container performs an emergency reboot.
- D. Kubelet automatically doubles the container's CPU limit.

---

### Question 9 — `[SCHED · Resource Requests vs Limits · Single]`
What occurs when an application container inside a Pod exceeds its configured `limits.memory` value?
- A. The container's CPU bandwidth is throttled.
- B. The Linux kernel OOM-killer sends a `SIGKILL` signal, terminating the container with status `OOMKilled` (Exit Code 137).
- C. Disk swap space is automatically allocated to accommodate the excess memory demand.
- D. Kubelet live-migrates the Pod to another node with higher memory capacity.

---

### Question 10 — `[SCHED · NodeSelector · Single]`
A worker node is labeled with `disktype=ssd`. What is the SIMPLEST configuration in a PodSpec to ensure that the Pod schedules only onto nodes with this label?
- A. `spec.nodeName: "disktype=ssd"`
- B. `spec.nodeSelector: { disktype: ssd }`
- C. `spec.tolerations: [{ key: "disktype", value: "ssd" }]`
- D. `spec.affinity.diskSelector: ssd`

---

### Question 11 — `[SCHED · LimitRange vs ResourceQuota · Single]`
What is the fundamental architectural difference between a `LimitRange` and a `ResourceQuota`?
- A. A `LimitRange` enforces resource boundaries (min/max/default) on **individual Pods and Containers**, whereas a `ResourceQuota` enforces aggregate resource caps across an **entire Namespace**.
- B. A `LimitRange` applies cluster-wide, whereas a `ResourceQuota` applies to a single Node.
- C. A `LimitRange` only governs network bandwidth, whereas a `ResourceQuota` only manages CPU.
- D. `LimitRange` and `ResourceQuota` are identical objects with interchangeable names.

---

### Question 12 — `[SCHED · Manual Scheduling · Single]`
If an engineer needs to bind a Pod directly to node `worker-node-2` **WITHOUT INVOLVING KUBE-SCHEDULER** (even if the scheduler component is offline), which field in the PodSpec must be defined?
- A. `spec.nodeSelector: worker-node-2`
- B. `spec.nodeName: worker-node-2`
- C. `spec.targetNode: worker-node-2`
- D. `spec.bindTo: worker-node-2`

---

### Question 13 — `[SCHED · Toleration Operator · Single]`
In a Pod's `tolerations` block, if the `operator` field is set to **`Exists`**, what does this indicate?
- A. The Pod tolerates the Taint only if both key and value match identically.
- B. The Pod tolerates any Taint possessing the specified `key`, regardless of its `value`.
- C. The Pod requires the specified Taint to be present on a node before it can be scheduled.
- D. Kubelet will dynamically add the Taint to the host node.

---

### Question 14 — `[SCHED · BestEffort QoS Condition · Single]`
Under which condition does a Pod qualify for the `BestEffort` QoS class?
- A. CPU requests are set, but CPU limits are omitted.
- B. Memory requests are set, but Memory limits are omitted.
- C. NO `requests` and NO `limits` for either CPU or Memory are declared for any container in the Pod.
- D. Declared `requests` exceed declared `limits`.

---

### Question 15 — `[SCHED · Pod PriorityClass · Single]`
In Kubernetes, what is the primary role of a `PriorityClass` resource during scheduling?
- A. Allocating prioritized network interface bandwidth to high-priority Pods.
- B. Indicating Pod scheduling importance; when cluster resources are insufficient, the scheduler can trigger **preemption** by evicting lower-priority Pods to schedule pending high-priority Pods.
- C. Ensuring the Pod is mounted to high-throughput NVMe storage volumes.
- D. Triggering automated node scale-up on cloud provider clusters.

---

### Question 16 — `[WORKLOAD · HPA troubleshooting · Single]`
`kubectl get hpa web -n prod` reports `TARGETS: <unknown>/70%` and the replica count never changes. `kubectl top pods -n prod` returns healthy numbers for every pod. What is the most likely cause?
- A. Metrics Server is not installed in the cluster.
- B. The Deployment's container spec omits `resources.requests.cpu`, so the HPA has no baseline against which to compute a utilisation percentage.
- C. The HPA must use `apiVersion: autoscaling/v1`; `v2` does not support CPU metrics.
- D. `minReplicas` is set higher than `maxReplicas`.

---

### Question 17 — `[WORKLOAD · HPA semantics · Single]`
A Deployment's container declares `resources.requests.cpu: 200m` and `resources.limits.cpu: 1000m`. Its HPA targets `averageUtilization: 50`. At what average per-pod CPU consumption does the HPA consider the workload to be exactly on target?
- A. 500m — 50% of the limit.
- B. 100m — 50% of the request.
- C. 600m — 50% of the midpoint between request and limit.
- D. 50% of the node's total allocatable CPU.

---

### Question 18 — `[TROUBLE · Resource monitoring · Single]`
You must record the name of the single highest memory-consuming pod in namespace `monitoring` into `/opt/top-pod.txt`, with no other text in the file. Which command does this correctly?
- A. `kubectl describe nodes | grep memory > /opt/top-pod.txt`
- B. `kubectl get pods -n monitoring --sort-by=.spec.containers[0].resources.requests.memory -o name > /opt/top-pod.txt`
- C. `kubectl top pods -n monitoring --sort-by=memory --no-headers | head -n 1 | awk '{print $1}' > /opt/top-pod.txt`
- D. `kubectl top pods -n monitoring | head -n 1 > /opt/top-pod.txt`

---

### Question 19 — `[WORKLOAD · Autoscaler types · Single]`
A cluster runs a batch workload whose pods are consistently OOMKilled because their memory `limits` were set far too low at design time. Which autoscaling mechanism is designed to correct **this specific** problem?
- A. Horizontal Pod Autoscaler — it adds replicas until memory pressure drops.
- B. Cluster Autoscaler — it adds nodes with more memory.
- C. Vertical Pod Autoscaler — it adjusts the pods' own `requests`/`limits` (restarting the pods to apply them).
- D. `kubectl top` — it automatically right-sizes the workload after collecting samples.

