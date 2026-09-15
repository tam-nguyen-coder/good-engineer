# 📝 Practice Questions — Week 2: Workloads & Controllers

> **15 Scenario Questions** · Authentic CKA & CKAD exam style · Focus on Deployments, Rollouts, DaemonSet, StatefulSet & Jobs.
> 🔒 **Detailed answers & explanations are in a separate file:** [answers.md](answers.md). Attempt all questions before checking!
> Taxonomy Tag: `[Domain · Topic · Question Type]`.
> Back to [Week 2 Plan](README.md) · [Labs](labs.md) · [Master Plan](../../K8S-STUDY-PLAN.md)

---

### Question 1 — `[WORKLOAD · Deployment Strategy · Single]`
A production Deployment is configured with `replicas: 4`. The rollout strategy is set to `RollingUpdate` with `maxSurge: 1` and `maxUnavailable: 0`. During an ongoing image update, which of the following statements ACCURATELY describes the number of Pods?
- A. At most 5 Pods can exist simultaneously, and at least 4 Pods will always be available to serve incoming traffic.
- B. The maximum number of Pods is 4, and the minimum number of available Pods is 3.
- C. All 4 existing Pods are terminated simultaneously before the 4 new Pods begin initialization.
- D. Up to 6 Pods can run concurrently during the update window.

---

### Question 2 — `[WORKLOAD · Rollout Undo · Single]`
Following an image update for Deployment `web-app`, the new Pods fail repeatedly with status `CrashLoopBackOff`. An administrator must immediately roll back the Deployment to the previously known good state at Revision 2. Which command accomplishes this?
- A. `kubectl rollout rollback deployment/web-app --revision=2`
- B. `kubectl rollout undo deployment/web-app --to-revision=2`
- C. `kubectl revert deployment/web-app --version=2`
- D. `kubectl rollout restart deployment/web-app -r 2`

---

### Question 3 — `[WORKLOAD · DaemonSet · Single]`
An infrastructure team must ensure that every worker node in a Kubernetes cluster runs exactly one instance of a Fluentd log collection agent. When a new node joins the cluster, this agent must automatically be scheduled onto it. Which Kubernetes workload resource is BEST suited for this requirement?
- A. `ReplicaSet`
- B. `StatefulSet`
- C. `DaemonSet`
- D. `Job`

---

### Question 4 — `[WORKLOAD · StatefulSet · Single]`
When deploying a MySQL database cluster using a `StatefulSet` named `mysql` with `replicas: 3`, which statement regarding Pod naming and startup order is TRUE?
- A. Pods are assigned randomized hashes (e.g., `mysql-7b89f`, `mysql-a12cd`) and are created in parallel.
- B. Pods are assigned ordinal index names (`mysql-0`, `mysql-1`, `mysql-2`), and `mysql-1` is created only after `mysql-0` reaches `Running` and `Ready`.
- C. Pods are numbered from 1 to 3 (`mysql-1`, `mysql-2`, `mysql-3`) and start up in random sequence.
- D. Each Pod name is suffixed with the IP address of its assigned worker node.

---

### Question 5 — `[WORKLOAD · StatefulSet & Networking · Single]`
To allow individual Pods within a `StatefulSet` to communicate directly with each other using stable, predictable internal DNS records (such as `mysql-0.mysql-svc.default.svc.cluster.local`), which type of Service MUST be associated with the `StatefulSet`?
- A. Service of type `NodePort`
- B. Service of type `LoadBalancer`
- C. Headless Service (with `clusterIP: None`)
- D. ExternalName Service

---

### Question 6 — `[WORKLOAD · CronJob Concurrency · Single]`
A `CronJob` is scheduled to execute every 5 minutes (`*/5 * * * *`) to synchronize accounting records. Occasionally, high data volume causes a single run to take 8 minutes. The administrator requires that if a previous execution has not yet finished, the next scheduled run MUST NOT start and should be skipped. Which `concurrencyPolicy` setting must be configured?
- A. `concurrencyPolicy: Allow`
- B. `concurrencyPolicy: Forbid`
- C. `concurrencyPolicy: Replace`
- D. `concurrencyPolicy: Skip`

---

### Question 7 — `[WORKLOAD · Job · Single]`
A batch processing queue requires completing a total of 10 data items (`completions: 10`), and allows up to 3 Pods to process items concurrently to speed up completion. Which pair of parameters in the Job `spec` satisfies this requirement?
- A. `replicas: 10` and `maxSurge: 3`
- B. `completions: 10` and `parallelism: 3`
- C. `count: 10` and `concurrency: 3`
- D. `iterations: 10` and `workers: 3`

---

### Question 8 — `[WORKLOAD · Job Failure · Single]`
In a Kubernetes `Job` specification, what is the default value of `backoffLimit` (number of retry attempts) before the Job is marked as permanently failed?
- A. 1
- B. 3
- C. 6
- D. Unlimited

---

### Question 9 — `[WORKLOAD · Deployment Strategy · Single]`
Under which circumstance should an engineering team choose `strategy.type: Recreate` instead of `RollingUpdate` for a Deployment?
- A. When the application requires zero downtime and 99.999% uptime.
- B. When the application cannot run two versions concurrently due to strict exclusive locks on database tables.
- C. When performing a 10% canary traffic experiment.
- D. When deploying a completely stateless microservice on cloud infrastructure.

---

### Question 10 — `[CLI · Imperative · Single]`
Which command updates the container image of container `app` in Deployment `backend` to `backend:v2.0` directly from the command line?
- A. `kubectl update deployment backend --image=backend:v2.0`
- B. `kubectl set image deployment/backend app=backend:v2.0`
- C. `kubectl edit deployment backend --image=backend:v2.0`
- D. `kubectl rollout deployment backend --image=backend:v2.0`

---

### Question 11 — `[WORKLOAD · ReplicaSet vs Deployment · Single]`
If an engineer directly deletes a running Pod managed by a Deployment using `kubectl delete pod <pod-name>`, which Kubernetes controller detects the shortfall and triggers the creation of a replacement Pod?
- A. `kube-scheduler`
- B. `kubelet`
- C. ReplicaSet Controller (part of `kube-controller-manager`)
- D. `kube-proxy`

---

### Question 12 — `[WORKLOAD · Rollout Pause & Resume · Single]`
An administrator needs to make multiple sequential updates to a Deployment (changing the container image, injecting new environment variables, and adjusting CPU limits) without triggering a separate rolling update for each change. Which strategy is recommended?
- A. Pause the rollout with `kubectl rollout pause deployment/<name>`, apply all changes, and resume with `kubectl rollout resume deployment/<name>`.
- B. Delete the Deployment, edit the local YAML file, and recreate it using `kubectl create`.
- C. Scale `replicas` to 0, apply all configuration changes, and scale back up to the original count.
- D. Temporarily switch the Deployment strategy to `Recreate` before making edits.

---

### Question 13 — `[WORKLOAD · DaemonSet Scheduling · Single]`
In modern Kubernetes versions (v1.20+), which component is responsible for scheduling and assigning DaemonSet Pods to worker nodes?
- A. DaemonSet Controller assigns the `nodeName` field directly in the PodSpec.
- B. `kube-scheduler` schedules DaemonSet Pods using default NodeAffinity rules.
- C. Kubelet on each node reads the manifest from local disk storage.
- D. `kube-apiserver` launches containers directly via the Container Runtime Interface.

---

### Question 14 — `[WORKLOAD · Job Deadline · Single]`
A reporting `Job` must not run for longer than 30 minutes (1800 seconds). If it exceeds this duration without completing, Kubernetes must terminate the Job and terminate all active Pods. Which field enforces this duration limit?
- A. `timeoutSeconds: 1800`
- B. `activeDeadlineSeconds: 1800`
- C. `terminationGracePeriodSeconds: 1800`
- D. `ttlSecondsAfterFinished: 1800`

---

### Question 15 — `[WORKLOAD · StatefulSet Storage · Single]`
When a StatefulSet provisions storage for its Pods using `volumeClaimTemplates` (generating PVCs like `data-mysql-0`, `data-mysql-1`), what happens to these PVCs if an administrator deletes the StatefulSet via `kubectl delete statefulset mysql`?
- A. All associated PVCs are automatically cascade-deleted along with the StatefulSet.
- B. The PVCs are preserved and remain intact to prevent accidental loss of critical persistent data.
- C. All underlying storage blocks in the PVCs are immediately zeroed out.
- D. The PVCs transition to `Pending` status.
