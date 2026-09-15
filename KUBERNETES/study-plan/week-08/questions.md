# 📝 Practice Questions — Week 8: Security, Authentication & RBAC

> **15 Scenario Questions** · Authentic CKA & CKAD exam style · Focus on Role, ClusterRole, RoleBinding, ClusterRoleBinding, ServiceAccount & PKI Certificates.
> 🔒 **Detailed answers & explanations are in a separate file:** [answers.md](answers.md). Attempt all questions before checking!
> Taxonomy Tag: `[Domain · Topic · Question Type]`.
> Back to [Week 8 Plan](README.md) · [Labs](labs.md) · [Master Plan](../../K8S-STUDY-PLAN.md)

---

### Question 1 — `[SECURITY · RBAC Scope · Single]`
An administrator creates a `ClusterRole` named `pod-reader` granting `get`, `list`, and `watch` permissions on `pods`. Subsequently, the administrator creates a `RoleBinding` in the `development` namespace binding `pod-reader` to user `alex`. Which statement accurately characterizes `alex`'s permissions?
- A. `alex` can read Pods across all namespaces throughout the entire cluster.
- B. `alex` can read Pods **only within the `development` namespace**.
- C. The RoleBinding creation fails because a RoleBinding cannot reference a ClusterRole.
- D. `alex` is automatically granted cluster-admin privileges.

---

### Question 2 — `[SECURITY · Checking Permissions · Single]`
Which command is the recommended way to verify whether the ServiceAccount `deployer-sa` in namespace `staging` has permission to delete Pods in the `staging` namespace?
- A. `kubectl auth can-i delete pods -n staging --as system:serviceaccount:staging:deployer-sa`
- B. `kubectl check permission delete pods --sa deployer-sa`
- C. `kubectl get rbac -n staging --sa deployer-sa`
- D. `kubectl verify user deployer-sa -n staging`

---

### Question 3 — `[SECURITY · Authentication Method · Single]`
In Kubernetes architecture, how are human user accounts (Normal Users) stored and managed within the cluster's etcd database?
- A. They are persisted in a user registry table at `/registry/users` in etcd.
- B. Kubernetes **DOES NOT have a User resource or database** in etcd; authentication is delegated to external mechanisms such as X.509 client certificates signed by the cluster CA or external OIDC providers.
- C. They are defined in the `kube-users` ConfigMap in `kube-system`.
- D. They are stored locally on each worker node by Kubelet.

---

### Question 4 — `[SECURITY · ServiceAccount Token (v1.24+) · Single]`
Since Kubernetes v1.24+, when a new ServiceAccount is created via `kubectl create sa my-service-account`, what occurs regarding its API token Secret?
- A. A permanent static Secret token is generated and linked automatically as in legacy versions.
- B. No secret is generated automatically; instead, Kubernetes uses the TokenRequest API to project short-lived, rotatable tokens (Bound ServiceAccount Tokens) into Pod volumes at runtime.
- C. All Pods in the namespace are automatically bound to this ServiceAccount.
- D. The ServiceAccount remains disabled until an administrator manually binds an Opaque secret.

---

### Question 5 — `[SECURITY · RBAC Verbs & Resources · Single]`
An administrator needs to create a Role in namespace `prod` that allows developers to inspect and list `Deployments` and `StatefulSets`. Which API group must be specified in the `apiGroups` list of the Role rule?
- A. `""` (core group)
- B. `"apps"`
- C. `"extensions"`
- D. `"batch"`

---

### Question 6 — `[SECURITY · RBAC Pod Logs · Single]`
To grant a developer permission to retrieve container logs using `kubectl logs`, which resource entry must be specified in the RBAC Role?
- A. `pods/logs`
- B. `podlogs`
- C. `logs`
- D. `podevents`

---

### Question 7 — `[SECURITY · Certificate Signing Request (CSR) · Single]`
A new engineer submits a Certificate Signing Request to the Kubernetes API as a `CertificateSigningRequest` object named `john-csr`. Which command does the cluster administrator use to approve this request?
- A. `kubectl sign csr john-csr`
- B. `kubectl certificate approve john-csr`
- C. `kubectl accept csr john-csr`
- D. `kubectl cert verify john-csr`

---

### Question 8 — `[SECURITY · Kubeconfig Context · Single]`
A `~/.kube/config` file contains blocks for `clusters`, `users`, and `contexts`. Which statement BEST defines a `context`?
- A. An IP address and memory threshold definition for the API server.
- B. A tuple binding together a specific **Cluster**, a specific **User**, and a default **Namespace**.
- C. A list of active RBAC privileges assigned to a user.
- D. The current client version of the `kubectl` binary.

---

### Question 9 — `[SECURITY · Switch Context CLI · Single]`
During the CKA exam, which command switches the active CLI context to the cluster context named `k8s-prod`?
- A. `kubectl switch context k8s-prod`
- B. `kubectl config use-context k8s-prod`
- C. `kubectl set-context k8s-prod`
- D. `kubectl context use k8s-prod`

---

### Question 10 — `[SECURITY · ClusterRoleBinding Target · Single]`
To which entity types can a `ClusterRoleBinding` grant cluster-wide permissions?
- A. Normal Users exclusively
- B. ServiceAccounts exclusively
- C. Users, Groups, or ServiceAccounts across the entire cluster
- D. Worker Nodes exclusively

---

### Question 11 — `[SECURITY · RBAC Core Group · Single]`
Which set of resources belongs to the Kubernetes Core API Group (represented by an empty string `apiGroups: [""]`)?
- A. `Deployments`
- B. `Pods`, `Services`, `ConfigMaps`, `Secrets`
- C. `CronJobs`
- D. `Ingresses`

---

### Question 12 — `[SECURITY · Encrypting Data at Rest · Single]`
To enable Secret encryption at rest in `etcd`, an `EncryptionConfiguration` file must be passed to which Control Plane component?
- A. `kube-controller-manager`
- B. `kube-apiserver` (via the `--encryption-provider-config` flag)
- C. `kube-scheduler`
- D. `kubelet`

---

### Question 13 — `[SECURITY · Pod ServiceAccount Binding · Single]`
To configure a Pod to authenticate against the API server using a custom ServiceAccount named `backend-sa` rather than `default`, which field must be specified in the PodSpec?
- A. `spec.serviceAccountName: backend-sa`
- B. `spec.identity: backend-sa`
- C. `spec.user: backend-sa`
- D. `spec.role: backend-sa`

---

### Question 14 — `[SECURITY · Subject in RoleBinding · Single]`
When referencing a human user inside the `subjects` array of a `RoleBinding`, which `apiGroup` must be declared?
- A. `rbac.authorization.k8s.io`
- B. `core`
- C. `system`
- D. Empty string `""`

---

### Question 15 — `[SECURITY · Certificate Location · Single]`
In a Kubernetes cluster deployed via standard `kubeadm`, where are the primary Certificate Authority private key (`ca.key`) and certificate (`ca.crt`) stored on the Control Plane node?
- A. `/var/lib/kubelet/pki`
- B. `/etc/kubernetes/pki`
- C. `/root/.kube/pki`
- D. `/opt/kubernetes/certs`
