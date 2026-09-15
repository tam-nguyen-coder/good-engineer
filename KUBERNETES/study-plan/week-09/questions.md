# 📝 Practice Questions — Week 9: Cluster Maintenance & etcd Disaster Recovery

> **15 Scenario Questions** · Authentic CKA & CKAD exam style · Focus on Kubeadm Upgrade, Node Cordon/Drain, etcd Backup/Restore & Certificate Renewal.
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
When performing an upgrade of a Kubernetes cluster from v1.30 to v1.31 using `kubeadm`, what is the CORRECT execution sequence on the primary Control Plane node?
- A. Upgrade Kubelet -> Upgrade Kubectl -> Upgrade Kubeadm -> Run `kubeadm upgrade apply`
- B. Drain node -> Upgrade `kubeadm` package -> Execute `kubeadm upgrade apply v1.31.0` -> Upgrade `kubelet` and `kubectl` -> Restart kubelet -> Uncordon node
- C. Upgrade all Worker nodes first, followed by the Control Plane
- D. Delete the cluster and initialize anew with `kubeadm init`

---

### Question 6 — `[ARCH · Kubeadm Worker Upgrade · Single]`
When upgrading a Worker Node using `kubeadm`, which command is used to apply the new cluster configuration to the worker (after upgrading the `kubeadm` binary)?
- A. `kubeadm upgrade apply v1.31.0`
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
