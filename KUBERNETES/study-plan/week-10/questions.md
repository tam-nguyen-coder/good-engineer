# 📝 Practice Questions — Week 10: Full-Scope Troubleshooting (30% CKA)

> **15 Scenario Questions** · Distilled from the 30% CKA Troubleshooting domain & Killer.sh simulators · Focus on Node Outages, Control Plane Crashes, Pod Failures & Network Diagnosis.
> 🔒 **Detailed answers & explanations are in a separate file:** [answers.md](answers.md). Attempt all questions before checking!
> Taxonomy Tag: `[Domain · Topic · Question Type]`.
> Back to [Week 10 Plan](README.md) · [Labs](labs.md) · [Master Plan](../../K8S-STUDY-PLAN.md)

---

### Question 1 — `[TROUBLE · Node NotReady · Single]`
A worker node in the cluster transitions unexpectedly to `NotReady`. An engineer SSHs into the affected node and executes `systemctl status kubelet`, finding the `kubelet` service in `failed` state. Which command is MOST effective for isolating the root cause of the Kubelet crash?
- A. `journalctl -u kubelet -e --no-pager`
- B. `cat /var/log/syslog | grep docker`
- C. `kubectl get events -n kube-system`
- D. `crictl ps`

---

### Question 2 — `[TROUBLE · Kubelet Container Runtime · Single]`
When checking the crash logs of Kubelet, the administrator observes: `failed to run Kubelet: validate service connection: CRI v1 runtime API is not implemented for endpoint "unix:///var/run/dockershim.sock"`. What is the root cause of this failure?
- A. The system ran out of physical RAM.
- B. Kubelet is configured to connect to the obsolete, removed `dockershim` socket; it must be updated to target the active containerd CRI endpoint (`unix:///run/containerd/containerd.sock`).
- C. The worker node lost network connectivity to the Control Plane.
- D. The Kubelet client certificate has expired.

---

### Question 3 — `[TROUBLE · API Server Down · Single]`
When executing `kubectl get nodes`, the terminal outputs the following connection error:
`The connection to the server 192.168.1.100:6443 was refused - did you specify the right host or port?`
Because `kubectl` cannot connect to any endpoint, the administrator SSHs into the primary Control Plane node. Which CLI tool enables the administrator to inspect the status and logs of the stopped `kube-apiserver` container?
- A. `crictl ps -a` and `crictl logs <container-id>`
- B. `kubectl logs kube-apiserver`
- C. `systemctl status kube-apiserver`
- D. `kubeadm status`

---

### Question 4 — `[TROUBLE · CrashLoopBackOff · Single]`
An application Pod rapidly alternates between `Running` and `Error` states before settling into `CrashLoopBackOff`. When running `kubectl logs <pod-name>`, no logs are printed because the current container instance just restarted. Which flag enables the administrator to view logs from the PREVIOUS, crashed execution?
- A. `--all`
- B. `--previous`
- C. `--last`
- D. `--history`

---

### Question 5 — `[TROUBLE · OOMKilled Exit Code 137 · Single]`
Running `kubectl describe pod analytics-worker` displays the following state:
`Last State: Terminated, Reason: OOMKilled, Exit Code: 137`.
What is the definitive corrective action to resolve this crash?
- A. Add an HTTP liveness probe to the container.
- B. Increase the `resources.limits.memory` threshold in the PodSpec or profile the application code to fix memory leaks.
- C. Switch the container image to an alpine variant.
- D. Restart the Kubelet service on the host worker node.

---

### Question 6 — `[TROUBLE · ImagePullBackOff Private Registry · Single]`
A Pod deployment referencing an image hosted in a private corporate container registry fails in `ImagePullBackOff` with: `rpc error: code = Unknown desc = Error response from daemon: unauthorized: authentication required`. What must be configured to permit successful image pulling?
- A. Create a `docker-registry` Secret with valid registry credentials, and declare this Secret in `spec.imagePullSecrets` in the PodSpec.
- B. Run the container with `privileged: true`.
- C. Set `imagePullPolicy: Never`.
- D. Inject a `DOCKER_AUTH` environment variable into the container.

---

### Question 7 — `[TROUBLE · Pod Stuck in Terminating · Single]`
A Pod is stuck in `Terminating` for over 15 minutes due to an unresponsive backend NFS mount and a process unresponsive to `SIGTERM`. Which command forcibly purges the Pod immediately to free up cluster scheduler resources during the CKA exam?
- A. `kubectl delete pod <name> --force --grace-period=0`
- B. `kubectl kill pod <name>`
- C. `kubectl remove pod <name> --now`
- D. `kubectl purge pod <name>`

---

### Question 8 — `[TROUBLE · Static Pod Manifest Location · Single]`
If Kubelet on the Control Plane node fails to start static pods like `kube-apiserver` or `etcd`, which field in the Kubelet configuration file `/var/lib/kubelet/config.yaml` should be inspected to locate the manifest directory?
- A. `manifestDirectory`
- B. `staticPodPath` (defaults to `/etc/kubernetes/manifests`)
- C. `podManifestURL`
- D. `staticConfig`

---

### Question 9 — `[TROUBLE · Node DiskPressure · Single]`
Running `kubectl describe node worker-2` reveals:
`Conditions: DiskPressure = True`.
What is the immediate consequence on `kube-scheduler` behavior?
- A. `kube-scheduler` will NOT schedule any new Pods onto `worker-2`, and Kubelet begins reclaiming disk space by pruning dead containers and unused container images.
- B. The node is automatically removed from etcd.
- C. All Pods on the node are switched to read-only filesystem mode.
- D. Kubelet shuts down the host network interface.

---

### Question 10 — `[TROUBLE · CoreDNS Crash · Single]`
Following initial cluster bootstrap, both CoreDNS Pods remain stuck in `Pending` or `CrashLoopBackOff`. What is the most common reason for this behavior in CKA exams?
- A. A CNI network plugin (such as Calico or Flannel) has not yet been deployed, preventing Pods from receiving IP addresses.
- B. No default StorageClass has been defined.
- C. The Control Plane node has insufficient RAM.
- D. Port 80 is occupied by a host process.

---

### Question 11 — `[TROUBLE · Service Not Routing · Single]`
A `ClusterIP` Service is deployed, but callers cannot establish connections to the backend application. An administrator executes `kubectl get ep <service-name>` and observes:
`NAME          ENDPOINTS   AGE`
`my-service    <none>      5m`
What is the immediate troubleshooting step?
- A. Restart the CoreDNS Deployment.
- B. Compare the Service's `spec.selector` against the `metadata.labels` on the target Pods, and update the selector to match the Pod labels exactly.
- C. Recreate the Service as type NodePort.
- D. Scale up the Deployment replica count.

---

### Question 12 — `[TROUBLE · Pending Pod Insufficient Resources · Single]`
A Deployment is configured with 5 replicas, but only 2 Pods achieve `Running` while 3 remain in `Pending`. Running `kubectl describe pod <pending-pod>` reveals: `0/2 nodes are available: 2 Insufficient cpu`. Which action resolves this issue?
- A. Lower the `resources.requests.cpu` in the Deployment's PodSpec, or add additional worker nodes to the cluster.
- B. Change the rollout strategy to `Recreate`.
- C. Upgrade the container image tag.
- D. Delete the Service linked to the Deployment.

---

### Question 13 — `[TROUBLE · crictl Default Config · Single]`
Upon SSHing into a worker node and invoking `crictl ps`, the command aborts with: `validate service connection: validate CRI v1 runtime API for endpoint "unix:///var/run/dockershim.sock": connect: no such file or directory`. Which configuration file should be edited or created to set the containerd socket?
- A. `/etc/crictl.yaml` containing `runtime-endpoint: unix:///run/containerd/containerd.sock`
- B. `/etc/docker/daemon.json`
- C. `/etc/kubernetes/crictl.conf`
- D. `~/.crictlrc`

---

### Question 14 — `[TROUBLE · Kubelet Swap Enabled · Single]`
After rebooting a worker node, the `kubelet` service fails to start with the error log: `failed to run Kubelet: running with swap on is not supported, please disable swap!`. Which Linux command immediately disables swap on the host?
- A. `swapoff -a`
- B. `systemctl stop swap`
- C. `rm /swapfile`
- D. `killall swap`

---

### Question 15 — `[TROUBLE · CKA Exam Time Strategy · Single]`
During the CKA exam, you are tackling a difficult troubleshooting question. You have spent 8 minutes inspecting logs and configs, but the node remains in `NotReady` and the cause is unclear. What is the RECOMMENDED time-management strategy?
- A. Spend another 20 minutes debugging because this task carries a high score weight.
- B. Click the **Flag** button in the exam interface, note the task number and weight on your scratchpad, immediately **PROCEED TO THE NEXT QUESTION** to bank easier points, and return only if time permits.
- C. Reboot the PSI secure browser virtual terminal.
- D. Submit the exam early.
