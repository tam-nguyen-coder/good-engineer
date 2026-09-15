# 📝 Practice Questions — Week 7: Storage Architecture, PV, PVC & StorageClass

> **15 Scenario Questions** · Authentic CKA & CKAD exam style · Focus on PersistentVolumes, Claims, StorageClass, Reclaim Policies & Volume Expansion.
> 🔒 **Detailed answers & explanations are in a separate file:** [answers.md](answers.md). Attempt all questions before checking!
> Taxonomy Tag: `[Domain · Topic · Question Type]`.
> Back to [Week 7 Plan](README.md) · [Labs](labs.md) · [Master Plan](../../K8S-STUDY-PLAN.md)

---

### Question 1 — `[STORAGE · Reclaim Policy · Single]`
A PersistentVolume (PV) is configured with `persistentVolumeReclaimPolicy: Retain`. When an application administrator deletes the associated PersistentVolumeClaim (PVC), what is the resulting status of the PV?
- A. `Available` (immediately eligible for binding to a new PVC)
- B. `Released` (retains underlying data, but cannot be rebound until manual administrator intervention)
- C. `Failed`
- D. The PV object is automatically cascade-deleted from the cluster

---

### Question 2 — `[STORAGE · AccessModes · Single]`
What does the `ReadWriteMany` (RWX) access mode signify for a Kubernetes PersistentVolume?
- A. The volume can be mounted as read-write simultaneously by multiple Pods running across **MULTIPLE DISTINCT NODES**.
- B. The volume can be mounted as read-write by multiple Pods, but all Pods MUST reside on the **SAME NODE**.
- C. The volume supports writing multiple times but can only be read once.
- D. The volume automatically mirrors its data blocks across multiple Availability Zones.

---

### Question 3 — `[STORAGE · VolumeBindingMode · Single]`
In a Kubernetes cluster deployed across multiple Availability Zones (Multi-AZ), why is `volumeBindingMode: WaitForFirstConsumer` strongly recommended over `volumeBindingMode: Immediate` in a `StorageClass`?
- A. It reduces cloud storage provisioning costs.
- B. It delays volume provisioning until a Pod requesting the PVC is assigned to a specific worker node by the scheduler, ensuring the storage volume is created in the exact same Availability Zone as the node.
- C. It automatically compresses volume data blocks prior to disk write operations.
- D. It enables volume mounting without requiring CSI drivers.

---

### Question 4 — `[STORAGE · Volume Expansion · Single]`
To allow an engineer to dynamically expand the capacity of an existing PVC by editing `spec.resources.requests.storage`, which prerequisite setting MUST be enabled on the underlying `StorageClass`?
- A. `reclaimPolicy: Expand`
- B. `allowVolumeExpansion: true`
- C. `dynamicResize: Enabled`
- D. `volumeMode: Resizable`

---

### Question 5 — `[STORAGE · Volume Reduction · Single]`
An existing PVC has a capacity of 50Gi. Noticing that the workload consumes only 10Gi, a developer edits the PVC specification to reduce storage to `20Gi` and runs `kubectl apply`. What is the outcome?
- A. Kubernetes shrinks the underlying storage filesystem to 20Gi within seconds.
- B. The update request is rejected immediately by the API server with an error: PVC storage capacity can only be increased, never decreased.
- C. All data residing within the PVC volume is wiped.
- D. The PVC transitions to `Pending` status.

---

### Question 6 — `[STORAGE · ReadWriteOncePod · Single]`
Introduced as GA in Kubernetes v1.29, what limitation of traditional `ReadWriteOnce` (RWO) does the `ReadWriteOncePod` (RWOP) access mode resolve?
- A. It allows volume mounting across public internet endpoints.
- B. It guarantees that ONLY **A SINGLE POD** across the entire cluster can access the volume for read-write operations (whereas RWO allows multiple Pods on the same node to mount the volume).
- C. It doubles raw block I/O throughput.
- D. It natively encrypts stored data using KMS keys.

---

### Question 7 — `[STORAGE · Static Provisioning · Single]`
Under the Static Provisioning workflow, which condition is MANDATORY for a PersistentVolumeClaim (PVC) to automatically transition to `Bound` against an existing PersistentVolume (PV)?
- A. The capacity of the PV must be greater than or equal to the capacity requested in the PVC, and the PV's `accessModes` must satisfy the requested `accessModes` of the PVC.
- B. The PV and PVC must be created within the exact same second.
- C. The PVC must explicitly name the target worker node in its PodSpec.
- D. The PV capacity must be strictly less than the PVC requested capacity.

---

### Question 8 — `[STORAGE · Storage Scope · Single]`
In the Kubernetes storage architecture, which statement accurately defines the scope of `PersistentVolume` (PV) and `PersistentVolumeClaim` (PVC) resources?
- A. Both PV and PVC resources are strictly namespaced.
- B. `PersistentVolume` (PV) is a **Cluster-scoped** resource; `PersistentVolumeClaim` (PVC) is a **Namespace-scoped** resource.
- C. Both PV and PVC resources are cluster-scoped.
- D. PV belongs to `kube-system`, whereas PVC belongs to `default`.

---

### Question 9 — `[STORAGE · EmptyDir Medium · Single]`
To create an `emptyDir` volume backed by high-speed host RAM (`tmpfs`) rather than the worker node's persistent disk storage, which attribute must be configured in the volume spec?
- A. `emptyDir.medium: "Memory"`
- B. `emptyDir.type: "RAM"`
- C. `emptyDir.storage: "tmpfs"`
- D. `emptyDir.driver: "fast"`

---

### Question 10 — `[STORAGE · CSI Architecture · Single]`
What is the primary role of the Container Storage Interface (CSI) in Kubernetes?
- A. Providing an open, standardized specification that allows storage vendors (AWS EBS, GCP PD, Ceph, NetApp) to develop out-of-tree volume plugins without modifying core Kubernetes source code.
- B. Managing Linux kernel-level block device encryption.
- C. Regulating overlay network traffic between Pods.
- D. Automating etcd snapshot generation.

---

### Question 11 — `[STORAGE · PVC in Pod · Single]`
Which YAML snippet correctly mounts an existing PVC named `data-pvc` into a container at `/var/data`?
- A.
  ```yaml
  spec:
    containers:
    - name: app
      image: nginx
      volumeMounts:
      - name: my-vol
        mountPath: /var/data
    volumes:
    - name: my-vol
      persistentVolumeClaim:
        claimName: data-pvc
  ```
- B.
  ```yaml
  spec:
    containers:
    - name: app
      image: nginx
      storage:
        pvc: data-pvc
        path: /var/data
  ```
- C.
  ```yaml
  spec:
    volumes:
    - claim: data-pvc
      mount: /var/data
  ```
- D.
  ```yaml
  spec:
    storageClaim: data-pvc
  ```

---

### Question 12 — `[STORAGE · Reclaim Policy Delete · Single]`
A PersistentVolume is dynamically provisioned by a `StorageClass` with `reclaimPolicy: Delete`. What occurs when the user deletes the associated PVC?
- A. The PV enters `Released` status and the cloud storage volume is preserved indefinitely.
- B. Kubernetes deletes the PV resource in the cluster AND invokes the CSI driver to **permanently delete the underlying physical/cloud disk volume**.
- C. Volume data is archived to an object storage bucket for 30 days.
- D. The API server rejects the PVC deletion request.

---

### Question 13 — `[STORAGE · Local Volume · Single]`
When configuring a PersistentVolume of type `local` (binding to a disk attached directly to a specific physical node), which attribute is MANDATORY in the PV specification?
- A. `spec.nodeAffinity` (to explicitly declare which node hosts the physical disk)
- B. `spec.nfs.server`
- C. `spec.cloudProvider`
- D. `spec.reclaimPolicy: Recycle`

---

### Question 14 — `[STORAGE · VolumeMode · Single]`
Which two values are supported by the `spec.volumeMode` field in PersistentVolumes and PersistentVolumeClaims?
- A. `Filesystem` (default) and `Block` (raw block device without a filesystem)
- B. `Read` and `Write`
- C. `SSD` and `HDD`
- D. `Static` and `Dynamic`

---

### Question 15 — `[STORAGE · PVC Protection · Single]`
If a running Pod currently mounts a PVC, and an administrator accidentally executes `kubectl delete pvc <pvc-name>`, what happens?
- A. The Pod is immediately killed and the volume is forcibly detached.
- B. The **Storage Object in Use Protection** finalizer halts PVC deletion; the PVC status remains in `Terminating` until the consuming Pod is terminated, preventing data corruption.
- C. The volume contents are erased while the Pod remains active.
- D. The host node reboots to recover file locks.
