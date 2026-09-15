# 📝 Practice Questions — Week 3: Pod Scheduling, Affinity, Taints & QoS

> **15 Scenario Questions** · Authentic CKA & CKAD exam style · Focus on NodeSelector, NodeAffinity, PodAntiAffinity, Taints/Tolerations, Requests/Limits & QoS Classes.
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
