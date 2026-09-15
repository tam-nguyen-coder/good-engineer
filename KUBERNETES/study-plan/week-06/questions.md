# 📝 Practice Questions — Week 6: Ingress, Gateway API & NetworkPolicies

> **15 Scenario Questions** · Authentic CKA & CKAD exam style · Focus on L7 Routing, TLS Ingress, Gateway API & NetworkPolicy Microsegmentation.
> 🔒 **Detailed answers & explanations are in a separate file:** [answers.md](answers.md). Attempt all questions before checking!
> Taxonomy Tag: `[Domain · Topic · Question Type]`.
> Back to [Week 6 Plan](README.md) · [Labs](labs.md) · [Master Plan](../../K8S-STUDY-PLAN.md)

---

### Question 1 — `[NET · Ingress API · Single]`
Since Kubernetes v1.22+, which official, GA API group and version is MANDATORY when defining an `Ingress` resource (replacing the deprecated and removed `extensions/v1beta1`)?
- A. `networking.k8s.io/v1`
- B. `extensions/v2`
- C. `ingress.k8s.io/v1`
- D. `apps/v1`

---

### Question 2 — `[NET · Ingress PathType · Single]`
In a modern Kubernetes Ingress v1 manifest, which set represents all valid options for the `pathType` attribute?
- A. `Prefix`, `Exact`, `ImplementationSpecific`
- B. `Regex`, `Wildcard`, `Standard`
- C. `Strict`, `Loose`, `Default`
- D. `Path`, `Domain`, `Subdomain`

---

### Question 3 — `[NET · NetworkPolicy Default Deny · Single]`
An engineer needs to enforce a strict zero-trust posture by dropping ALL incoming (Ingress) network traffic destined for ANY Pod in the `finance` namespace. Which manifest implements this requirement correctly?
- A.
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: deny-all
    namespace: finance
  spec:
    podSelector: {}
    policyTypes:
    - Ingress
  ```
- B.
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: deny-all
    namespace: finance
  spec:
    action: BlockAll
  ```
- C.
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: deny-all
    namespace: finance
  spec:
    podSelector:
      matchLabels:
        status: all
  ```
- D.
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: deny-all
  spec:
    ingress: []
  ```

---

### Question 4 — `[NET · NetworkPolicy CNI · Single]`
An engineer creates and applies a NetworkPolicy in a test cluster running pure Flannel CNI. However, traffic between Pods continues unimpeded, and no packets are blocked. What is the root cause?
- A. Pure Flannel does not implement the NetworkPolicy specification; an enforcement provider such as Calico, Cilium, or Canal must be installed for NetworkPolicies to take effect.
- B. The engineer failed to restart Kubelet across the worker nodes.
- C. CoreDNS must be restarted whenever a NetworkPolicy is created.
- D. NetworkPolicy enforcement applies exclusively to UDP packets.

---

### Question 5 — `[NET · Ingress TLS · Single]`
To configure TLS termination on a Kubernetes Ingress resource, which `type` must the Secret storing the SSL/TLS certificate and private key have?
- A. `Opaque`
- B. `kubernetes.io/tls`
- C. `kubernetes.io/ssh-auth`
- D. `kubernetes.io/service-account-token`

---

### Question 6 — `[NET · NetworkPolicy Logic · Single]`
Examine the following NetworkPolicy snippet:
```yaml
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          project: myproject
    - podSelector:
        matchLabels:
          role: frontend
```
Which logical condition is evaluated between the `namespaceSelector` and `podSelector`?
- A. An **AND** condition: Incoming Pods MUST have label `role: frontend` AND concurrently reside within a namespace labeled `project: myproject`.
- B. An **OR** condition: Traffic is allowed from ANY Pod within a namespace labeled `project: myproject` OR from any Pod labeled `role: frontend` within the current namespace.
- C. A **NOT** condition: Traffic from namespace `myproject` is explicitly blocked.
- D. The manifest syntax is invalid and will be rejected by the API server.

---

### Question 7 — `[NET · NetworkPolicy Logic · Single]`
How should the configuration in Question 6 be adjusted to enforce an **AND** condition (allowing traffic ONLY from Pods labeled `role: frontend` that reside inside namespaces labeled `project: myproject`)?
- A. Insert the keyword `operator: AND` between the two selectors.
- B. Combine both `namespaceSelector` and `podSelector` under a SINGLE list item `-` in the `from` array.
- C. Create two distinct NetworkPolicy objects in the same namespace.
- D. Change `policyTypes` to `Both`.

---

### Question 8 — `[NET · Gateway API Architecture · Single]`
In the Kubernetes Gateway API architecture, which resource is specifically targeted at **Application Developers** to declare detailed Layer 7 routing rules (such as Path matching, Header inspection, and Canary traffic splitting)?
- A. `GatewayClass`
- B. `Gateway`
- C. `HTTPRoute`
- D. `IngressClass`

---

### Question 9 — `[NET · Gateway API Roles · Single]`
In the Kubernetes Gateway API personas model, which role is typically responsible for provisioning and managing `Gateway` lifecycle resources?
- A. Application Developer
- B. Cluster Operator / Platform Engineer
- C. Cloud Infrastructure Provider
- D. Database Administrator

---

### Question 10 — `[NET · Ingress Controller vs Resource · Single]`
What is the fundamental difference between an Ingress Resource and an Ingress Controller?
- A. The Ingress Resource is the running reverse proxy process (e.g. Nginx Pod); the Ingress Controller is the YAML manifest.
- B. The Ingress Resource is a declarative YAML specification defining routing rules; the Ingress Controller is the active daemon (e.g., ingress-nginx) that monitors Ingress Resources and configures the actual load balancer.
- C. Ingress Controller and Ingress Resource refer to the exact same object.
- D. The Ingress Controller executes on worker nodes, while Ingress Resources execute in etcd.

---

### Question 11 — `[NET · NetworkPolicy DNS Trap · Single]`
After configuring a NetworkPolicy with `policyTypes: ["Egress"]` for a backend microservice, the application suddenly fails to establish connections with its database, even though database egress rules are open. What is the most common reason?
- A. Kubelet process hung on the worker node.
- B. The Egress policy inadvertently dropped all outbound DNS queries (UDP/TCP port 53) to CoreDNS, preventing the application from resolving the database Service hostname.
- C. The CNI daemon lost network connectivity.
- D. Missing mutual TLS certificates.

---

### Question 12 — `[NET · Ingress rewrite-target · Single]`
When using the Nginx Ingress Controller, which annotation is standardly employed to strip URL path prefixes (e.g., rewriting `/app/users` to `/users` before proxying to the backend service)?
- A. `nginx.ingress.kubernetes.io/rewrite-target: /`
- B. `nginx.ingress.kubernetes.io/strip-prefix: "true"`
- C. `nginx.ingress.kubernetes.io/path-override: none`
- D. `nginx.ingress.kubernetes.io/redirect: permanent`

---

### Question 13 — `[NET · NetworkPolicy ipBlock · Single]`
Which NetworkPolicy snippet allows ingress traffic from the CIDR block `192.168.1.0/24` while EXCLUDING the specific IP `192.168.1.50/32`?
- A.
  ```yaml
  ingress:
  - from:
    - ipBlock:
        cidr: 192.168.1.0/24
        except:
        - 192.168.1.50/32
  ```
- B.
  ```yaml
  ingress:
  - from:
    - ipBlock:
        allow: 192.168.1.0/24
        deny: 192.168.1.50/32
  ```
- C.
  ```yaml
  ingress:
  - from:
    - cidr: 192.168.1.0/24 - 192.168.1.50/32
  ```
- D.
  ```yaml
  ingress:
  - exclude: 192.168.1.50/32
  ```

---

### Question 14 — `[NET · IngressClass · Single]`
When multiple Ingress Controllers operate simultaneously in the same cluster (e.g., Traefik and Nginx), how does an Ingress resource explicitly declare which controller must reconcile it?
- A. By specifying the `spec.ingressClassName` field in the Ingress manifest.
- B. By prefixing the Ingress resource name with the controller name.
- C. By labeling the parent Namespace.
- D. By restarting the target Ingress Controller.

---

### Question 15 — `[NET · NetworkPolicy Isolation State · Single]`
A newly deployed Pod runs in a namespace where no NetworkPolicies are defined. What is the network isolation state of this Pod?
- A. Isolated (All incoming and outgoing traffic is blocked by default).
- B. Non-isolated (The Pod can send and receive network traffic freely to and from any source).
- C. Read-only mode.
- D. Traffic is restricted to localhost only.
