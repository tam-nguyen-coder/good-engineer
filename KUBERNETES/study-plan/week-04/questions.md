# 📝 Practice Questions — Week 4: ConfigMaps, Secrets, Probes & SecurityContext

> **15 Scenario Questions** · Authentic CKA & CKAD exam style · Focus on Configuration, Liveness/Readiness/Startup Probes, SecurityContext & Pod Security Standards.
> 🔒 **Detailed answers & explanations are in a separate file:** [answers.md](answers.md). Attempt all questions before checking!
> Taxonomy Tag: `[Domain · Topic · Question Type]`.
> Back to [Week 4 Plan](README.md) · [Labs](labs.md) · [Master Plan](../../K8S-STUDY-PLAN.md)

---

### Question 1 — `[WORKLOAD · ReadinessProbe · Single]`
A web application container inside a Pod has a configured `readinessProbe`. If the `readinessProbe` fails consecutively and exceeds the `failureThreshold`, what action does Kubernetes take?
- A. Kubelet immediately restarts the container.
- B. Kubelet sends a `SIGKILL` to terminate the container and enters `CrashLoopBackOff`.
- C. Kubelet does NOT restart the container; instead, Kubernetes removes the Pod's IP address from the `Endpoints` / `EndpointSlices` of any matching Service to stop routing network traffic to it.
- D. The Pod is deleted from the cluster, and the ReplicaSet launches a replacement Pod.

---

### Question 2 — `[WORKLOAD · LivenessProbe · Single]`
An application experiences an internal software deadlock where its process remains active, but it completely stops responding to incoming requests. Which health check mechanism is specifically designed to detect this frozen state and automatically RESTART the container to recover service?
- A. `StartupProbe`
- B. `ReadinessProbe`
- C. `LivenessProbe`
- D. `HealthProbe`

---

### Question 3 — `[WORKLOAD · StartupProbe · Single]`
A legacy Java enterprise application requires 2 to 3 minutes to warm up and load reference data into memory before it can serve requests. During this startup window, a configured `livenessProbe` frequently fails and repeatedly restarts the container before it finishes warming up. What is the standard, best-practice Kubernetes solution?
- A. Increase `livenessProbe.failureThreshold` to 1000.
- B. Configure a `startupProbe` for the container; while the `startupProbe` is running and has not yet succeeded, it temporarily disables both `livenessProbe` and `readinessProbe`.
- C. Completely remove the `livenessProbe` from the Pod specification.
- D. Convert the application to run as a `DaemonSet`.

---

### Question 4 — `[WORKLOAD · ConfigMap Auto-update · Single]`
An administrator mounts data from a `ConfigMap` into a running Pod. In which of the following scenarios will updates to the ConfigMap key-value pairs **AUTOMATICALLY UPDATE** inside the running container after a propagation delay WITHOUT requiring a Pod restart?
- A. When the ConfigMap is injected as environment variables via `envFrom`.
- B. When the ConfigMap is mounted into the container as a **Volume** (`spec.volumes[].configMap`).
- C. When the ConfigMap is injected via `valueFrom.configMapKeyRef`.
- D. ConfigMap data never automatically updates under any mounting scenario.

---

### Question 5 — `[SECURITY · SecurityContext · Single]`
Which setting in a container's `securityContext` guarantees that the process inside the container is strictly FORBIDDEN from running as root (`UID 0`)?
- A. `privileged: false`
- B. `runAsNonRoot: true`
- C. `allowPrivilegeEscalation: false`
- D. `readOnlyRootFilesystem: true`

---

### Question 6 — `[SECURITY · SecurityContext Capabilities · Single]`
To comply with the principle of least privilege, a security engineer wants to strip ALL default Linux kernel capabilities from a container, while granting only the ability to bind to privileged network ports below 1024 (`NET_BIND_SERVICE`). Which `securityContext` block is CORRECT?
- A.
  ```yaml
  securityContext:
    capabilities:
      drop: ["ALL"]
      add: ["NET_BIND_SERVICE"]
  ```
- B.
  ```yaml
  securityContext:
    capabilities:
      allow: ["NET_BIND_SERVICE"]
  ```
- C.
  ```yaml
  securityContext:
    linux:
      dropAll: true
      addNet: true
  ```
- D.
  ```yaml
  securityContext:
    permissions:
      only: ["NET_BIND_SERVICE"]
  ```

---

### Question 7 — `[SECURITY · Pod Security Standards (PSA) · Single]`
Since the complete removal of `PodSecurityPolicy` (PSP) in Kubernetes v1.25+, which built-in admission mechanism is used to enforce Pod Security Standards (Privileged, Baseline, Restricted)?
- A. Custom Resource Definitions named `SecurityPolicy`.
- B. Special standardized control labels applied to individual **Namespaces**.
- C. Direct modifications to `/etc/kubernetes/manifests/kube-apiserver.yaml`.
- D. Mandatory installation of third-party admission plugins.

---

### Question 8 — `[SECURITY · PSA Label Modes · Single]`
When applying Pod Security Admission labels to a Namespace, which mode will **COMPLETELY BLOCK** (reject the creation of) any Pod that violates the configured security standard level?
- A. `warn`
- B. `audit`
- C. `enforce`
- D. `strict`

---

### Question 9 — `[WORKLOAD · Secret Creation CLI · Single]`
Which command creates a generic Secret named `db-pass` in namespace `dev`, containing the key `password` with the value `mypassword123`?
- A. `kubectl create secret generic db-pass --from-literal=password=mypassword123 -n dev`
- B. `kubectl create secret password mypassword123 --name=db-pass -n dev`
- C. `kubectl set secret db-pass password=mypassword123 -n dev`
- D. `kubectl run secret db-pass --value=mypassword123 -n dev`

---

### Question 10 — `[SECURITY · ReadOnlyRootFilesystem · Single]`
When a container is hardened with `readOnlyRootFilesystem: true`, how should temporary files (such as local caches or logs in `/tmp` or `/var/cache`) be handled safely without disabling root filesystem protection?
- A. Disable the `readOnlyRootFilesystem` flag.
- B. Enable `privileged: true`.
- C. Mount an **`emptyDir`** volume at the specific directory paths where temporary writes occur.
- D. Use a `hostPath` volume pointing to `/root`.

---

### Question 11 — `[WORKLOAD · Probes Probe Types · Single]`
When using an `httpGet` action for Liveness or Readiness Probes, which HTTP status code range does Kubernetes consider a SUCCESSFUL health check?
- A. Exactly status code `200`
- B. Greater than or equal to `200` and strictly less than `400` (`200 <= statusCode < 400`)
- C. Greater than or equal to `200` and strictly less than `500`
- D. Any status code other than `500`

---

### Question 12 — `[WORKLOAD · Secret Encoding · Single]`
When inspecting a Secret object using `kubectl get secret my-secret -o yaml`, in what format are values in the `data` field represented?
- A. Asymmetric RSA 2048-bit encryption
- B. One-way SHA-256 cryptographic hash
- C. Standard plaintext Base64 encoding (decodable via `base64 -d`)
- D. AES-GCM 256-bit symmetric cipher

---

### Question 13 — `[WORKLOAD · PreStop Hook · Single]`
In the Kubernetes container lifecycle, when does the `preStop` hook execute?
- A. Immediately before container initialization.
- B. Immediately after the container process begins execution.
- C. Immediately when Kubelet receives a container termination event, BEFORE Kubelet sends the `SIGTERM` signal to the container process.
- D. After the container has already received `SIGKILL`.

---

### Question 14 — `[WORKLOAD · EnvFrom · Single]`
A `ConfigMap` named `app-env` contains 20 key-value pairs. A developer wants to inject all 20 entries into a container as environment variables without writing 20 individual `valueFrom` statements. Which PodSpec construct satisfies this?
- A. `spec.containers[].env: all`
- B. `spec.containers[].envFrom: [{ configMapRef: { name: app-env } }]`
- C. `spec.containers[].inject: app-env`
- D. `spec.containers[].environmentVariables: app-env`

---

### Question 15 — `[SECURITY · SecurityContext allowPrivilegeEscalation · Single]`
What Linux kernel mechanism does the setting `allowPrivilegeEscalation: false` enforce?
- A. It prevents child processes from gaining more privileges than their parent process (such as executing binaries with `setuid` or `setgid` flags like `sudo`).
- B. It prevents the container from exceeding its configured CPU quota.
- C. It blocks outbound network egress to public IP addresses.
- D. It blocks cluster users from running `kubectl exec`.
