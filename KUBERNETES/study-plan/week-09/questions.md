# 📝 Practice Questions — Week 9: Cluster Maintenance & etcd Disaster Recovery

> **21 Scenario Questions** · Authentic CKA & CKAD exam style · Focus on Kubeadm Upgrade, Node Cordon/Drain, etcd Backup/Restore, Certificate Renewal, **HA Control Plane & CRD/Operators**.
> 🔒 **Detailed answers & explanations are in a separate file:** [answers.md](answers.md). Attempt all questions before checking!
> Taxonomy Tag: `[Domain · Topic · Question Type]`.
> Back to [Week 9 Plan](README.md) · [Labs](labs.md) · [Master Plan](../../K8S-STUDY-PLAN.md)

---

### Question 1 — `[ARCH · etcd Backup · Single]`
When using the `etcdctl` utility to take a snapshot backup of the etcd database on the Control Plane node, which environment variable MUST be exported to ensure `etcdctl` interacts with etcd via API v3?
- A. `export ETCD_VERSION=3`
- B. `export ETCDCTL_API=3`
- C. `export KUBE_ETCD_API=v3`
- D. `export ETCD_USE_V3=true`

---

### Question 2 — `[ARCH · etcd Restore Pitfall · Single]`
When restoring the etcd database from a snapshot file using `etcdctl snapshot restore <file.db>`, why MUST the `--data-dir` flag specify an uninitialized new directory (such as `/var/lib/etcd-from-backup`) rather than the active data directory `/var/lib/etcd`?
- A. `etcdctl` explicitly rejects target directories containing pre-existing database files to prevent corruption and file-lock conflicts.
- B. etcd supports snapshot restoration into RAM-backed disks only.
- C. `/var/lib/etcd` is an immutable, read-only system directory.
- D. Kubelet automatically purges the snapshot file if restored to the default path.

---

### Question 3 — `[ARCH · Node Drain Flags · Single]`
An engineer executes `kubectl drain worker-1` to prepare a node for kernel maintenance, but the command aborts with: `cannot delete Pods with local storage: ...`. Which flag must be appended to permit eviction of Pods mounting `emptyDir` volumes?
- A. `--force`
- B. `--delete-emptydir-data`
- C. `--ignore-local-storage`
- D. `--skip-volumes`

---

### Question 4 — `[ARCH · Node Drain DaemonSet · Single]`
When executing `kubectl drain <node-name>`, which flag is MANDATORY if there are active `DaemonSet` Pods running on that node?
- A. `--ignore-daemonsets`
- B. `--skip-daemonsets`
- C. `--delete-daemonsets`
- D. `--force-daemonsets`

---

### Question 5 — `[ARCH · Kubeadm Upgrade Sequence · Single]`
When performing an upgrade of a Kubernetes cluster from v1.34 to v1.35 using `kubeadm`, what is the CORRECT execution sequence on the primary Control Plane node?
- A. Upgrade Kubelet -> Upgrade Kubectl -> Upgrade Kubeadm -> Run `kubeadm upgrade apply`
- B. Drain node -> Upgrade `kubeadm` package -> Execute `kubeadm upgrade apply v1.35.0` -> Upgrade `kubelet` and `kubectl` -> Restart kubelet -> Uncordon node
- C. Upgrade all Worker nodes first, followed by the Control Plane
- D. Delete the cluster and initialize anew with `kubeadm init`

---

### Question 6 — `[ARCH · Kubeadm Worker Upgrade · Single]`
When upgrading a Worker Node using `kubeadm`, which command is used to apply the new cluster configuration to the worker (after upgrading the `kubeadm` binary)?
- A. `kubeadm upgrade apply v1.35.0`
- B. `kubeadm upgrade node`
- C. `kubeadm node update`
- D. `kubeadm upgrade worker`

---

### Question 7 — `[ARCH · Version Skew Policy · Single]`
According to the official Kubernetes Version Skew Policy, by how many minor versions can `kubelet` on a Worker Node lag behind `kube-apiserver` on the Control Plane?
- A. At most 1 minor version
- B. At most 2 minor versions (expanded to up to 3 minor versions starting in v1.28+)
- C. Kubelet must strictly match the exact minor and patch version of the API Server
- D. Unlimited minor versions

---

### Question 8 — `[ARCH · Cordon vs Drain · Single]`
What is the fundamental difference between `kubectl cordon <node>` and `kubectl drain <node>`?
- A. `cordon` merely marks the node as unschedulable for new Pods; `drain` marks the node unschedulable AND evicts all existing running Pods to other nodes.
- B. `cordon` removes the node object from etcd; `drain` temporarily powers down the host.
- C. `cordon` applies exclusively to Control Plane nodes; `drain` applies exclusively to Worker nodes.
- D. `cordon` and `drain` are synonyms for the exact same underlying API operation.

---

### Question 9 — `[ARCH · etcd Certificates · Single]`
Taking an etcd snapshot backup requires mutual TLS certificates. In a standard cluster deployed with `kubeadm`, where are the CA certificate, client certificate, and private key for etcd located by default?
- A. `/etc/kubernetes/pki/etcd/` (specifically `ca.crt`, `server.crt`, `server.key`)
- B. `/var/lib/etcd/certs/`
- C. `/etc/ssl/etcd/`
- D. `/root/.etcd/certs/`

---

### Question 10 — `[ARCH · Static Pod Restart Mechanism · Single]`
After restoring an etcd snapshot to a new data directory and updating the `hostPath` volume path inside `/etc/kubernetes/manifests/etcd.yaml`, how does the administrator restart the etcd static pod?
- A. Execute `kubectl restart pod etcd`.
- B. Do nothing; Kubelet continuously watches `/etc/kubernetes/manifests/`, and upon detecting changes to `etcd.yaml`, it automatically restarts the etcd static pod with the new volume mapping.
- C. Perform a physical reboot of the Control Plane server.
- D. Execute `systemctl restart containerd`.

---

### Question 11 — `[ARCH · APT Package Hold · Single]`
Before running `apt-get install` to upgrade `kubeadm`, `kubelet`, and `kubectl` on an Ubuntu node, why must the administrator execute `apt-mark unhold`?
- A. Kubernetes packages are held by default to prevent unintended automatic upgrades during routine OS `apt upgrade` runs.
- B. To reclaim reserved disk space on the root filesystem.
- C. To disable underlying iptables firewall chains.
- D. To grant authorization to pull from external Docker registries.

---

### Question 12 — `[ARCH · Verify etcd Snapshot · Single]`
After capturing an etcd snapshot file, which command verifies its integrity and displays its metadata (such as file size, revision, and total keys) in a human-readable table?
- A. `etcdctl snapshot check /tmp/etcd.db`
- B. `etcdctl --write-out=table snapshot status /tmp/etcd.db`
- C. `etcdctl inspect /tmp/etcd.db`
- D. `etcdctl verify /tmp/etcd.db`

---

### Question 13 — `[ARCH · Certificate Expiration · Single]`
Which command provided by `kubeadm` checks the expiration dates of all internal cluster PKI certificates?
- A. `kubeadm certs check-expiration`
- B. `kubeadm cert status`
- C. `kubectl get certificates --all`
- D. `openssl verify /etc/kubernetes/pki/*`

---

### Question 14 — `[ARCH · Certificate Renewal · Single]`
To renew all internal control plane certificates managed by `kubeadm` before they expire, which command should be executed on the Control Plane node?
- A. `kubeadm certs renew all`
- B. `kubeadm update certs --all`
- C. `kubeadm certs refresh`
- D. `kubectl renew certs -A`

---

### Question 15 — `[ARCH · Uncordon Node · Single]`
After completing node kernel updates and rebooting Worker Node `node-01`, which command transitions the node back to schedulable status to receive new Pods from the scheduler?
- A. `kubectl enable node node-01`
- B. `kubectl start node node-01`
- C. `kubectl uncordon node-01`
- D. `kubectl resume node node-01`

---

### Question 16 — `[ARCH · etcd quorum · Single]`
An architect proposes growing an etcd cluster from **3** members to **4** to improve fault tolerance. Evaluate the proposal.
- A. Correct — 4 members tolerate 2 failures, double that of 3 members.
- B. Incorrect — quorum for 4 members is 3, so it still tolerates only **1** failure, exactly like a 3-member cluster, while adding another machine that can fail. etcd clusters should always have an odd member count.
- C. Correct — an even member count lets Raft split the vote evenly and recover faster.
- D. Incorrect — etcd supports a maximum of 3 members.

---

### Question 17 — `[ARCH · HA topology · Single]`
A cluster was originally bootstrapped with `kubeadm init --apiserver-advertise-address=10.0.1.10` and no `--control-plane-endpoint`. Management now wants to add two more control plane nodes behind a load balancer. What is the situation?
- A. Simply run `kubeadm join --control-plane` on the two new nodes; kubeadm reconfigures the endpoint automatically.
- B. Edit `/etc/kubernetes/admin.conf` on every node to point at the load balancer VIP, then join.
- C. The control plane endpoint is baked into the cluster's certificates and kubeconfigs at init time and cannot be changed afterwards — converting this cluster to HA requires rebuilding it with `--control-plane-endpoint` set to the LB address.
- D. Run `kubeadm upgrade apply --control-plane-endpoint k8s-api.example.com:6443` to migrate in place.

---

### Question 18 — `[ARCH · HA components · Single]`
In a 3-node HA control plane, which statement correctly describes how the components run?
- A. All three `kube-apiserver`, `kube-scheduler` and `kube-controller-manager` instances are active simultaneously.
- B. `kube-apiserver` runs active-active behind the load balancer, while `kube-scheduler` and `kube-controller-manager` run active-passive — only the leader elected via a Lease object in `kube-system` actually does work.
- C. Only one `kube-apiserver` is active; the load balancer performs health-check failover to a standby.
- D. All three components elect a single leader node that runs every control plane component.

---

### Question 19 — `[ARCH · CRD naming · Single]`
You apply a CustomResourceDefinition with `spec.group: ops.example.com`, `spec.names.plural: backups`, `spec.names.kind: Backup`, and `metadata.name: backup.ops.example.com`. The API server rejects it. Why?
- A. `spec.names.kind` must be lowercase.
- B. `metadata.name` must be exactly `<plural>.<group>` — here it must read `backups.ops.example.com` (plural), not `backup.ops.example.com`.
- C. Custom groups may not contain the substring `example.com`.
- D. A CRD must declare at least two entries under `spec.versions`.

---

### Question 20 — `[ARCH · CRD vs controller · Single]`
A CRD is registered successfully, `kubectl get crd` lists it, and you can create custom objects of the new kind — `kubectl get backups` shows them. However, nothing at all happens in the cluster: no pods, no jobs, no side effects. What is the explanation?
- A. The CRD is missing `additionalPrinterColumns`, so its reconciliation loop never starts.
- B. Custom resources need `spec.scope: Cluster` before controllers can act on them.
- C. A CRD only extends the API's storage and validation. Actually acting on the objects requires a **controller/operator** watching that kind — it is either not installed or its pod is not running.
- D. The objects must be annotated with `kubernetes.io/reconcile: "true"`.

---

### Question 21 — `[ARCH · Operator troubleshooting · Single]`
An operator was installed via Helm. Its custom resources are accepted but stay in an empty `status`. Which sequence best isolates the fault?
- A. Delete and recreate the CRD to force re-registration.
- B. Increase the custom resource's `spec.retention` value and wait for the next sync interval.
- C. Check that the operator's controller pod is Running in its namespace, read its logs (`kubectl logs -n <ns> deploy/<controller>`), then inspect the custom resource's `.status` and `kubectl describe` events.
- D. Restart `kube-controller-manager` on every control plane node — it owns reconciliation for all custom resources.

