# 📝 Practice Questions — Week 5: Services & Core Networking

> **15 Scenario Questions** · Authentic CKA & CKAD exam style · Focus on ClusterIP, NodePort, Headless Service, CoreDNS, Endpoints & kube-proxy.
> 🔒 **Detailed answers & explanations are in a separate file:** [answers.md](answers.md). Attempt all questions before checking!
> Taxonomy Tag: `[Domain · Topic · Question Type]`.
> Back to [Week 5 Plan](README.md) · [Labs](labs.md) · [Master Plan](../../K8S-STUDY-PLAN.md)

---

### Question 1 — `[NET · Service Types · Single]`
An engineer configures a Kubernetes Service with `type: NodePort`. What is the default port range allocated by Kubernetes for statically or dynamically assigned `nodePort` values across cluster nodes?
- A. `1024 – 65535`
- B. `30000 – 32767`
- C. `8000 – 9000`
- D. `20000 – 25000`

---

### Question 2 — `[NET · Endpoints Troubleshooting · Single]`
A Service named `order-service` is created successfully, but client applications calling its ClusterIP encounter connection timeouts. When an engineer runs `kubectl get endpoints order-service`, the `ENDPOINTS` column displays `<none>`. What is the MOST likely cause of this issue?
- A. The backend Pods have run out of memory.
- B. The `kube-proxy` daemon has crashed on all worker nodes.
- C. The `spec.selector` defined on the Service does not match the `metadata.labels` on any running Pod.
- D. The Service has not been assigned a TLS certificate.

---

### Question 3 — `[NET · Headless Service · Single]`
When configuring a Service, if the `spec.clusterIP` field is explicitly set to **`None`**, what is this Service called and how does CoreDNS respond to DNS queries for this Service?
- A. Headless Service; CoreDNS returns the direct individual IP addresses (A records) of all backend Pods rather than a single virtual ClusterIP.
- B. ExternalName Service; CoreDNS forwards the query to an external public DNS resolver.
- C. ClusterIP Service; CoreDNS automatically allocates a random virtual IP within the service CIDR.
- D. Ingress Service; CoreDNS redirects traffic to the Nginx Ingress controller.

---

### Question 4 — `[NET · CoreDNS FQDN · Single]`
An application running in a Pod within the `sales` namespace needs to send HTTP requests to Service `inventory-svc` located in the `warehouse` namespace. What is the correct standard Fully Qualified Domain Name (FQDN) to connect to this Service?
- A. `http://inventory-svc.sales`
- B. `http://inventory-svc.warehouse.svc.cluster.local`
- C. `http://warehouse.inventory-svc.cluster.local`
- D. `http://inventory-svc.svc.cluster.local`

---

### Question 5 — `[NET · kube-proxy Mode · Single]`
What is the default operating mode of `kube-proxy` on most modern standard Kubernetes clusters for handling Layer 4 Service routing and packet filtering?
- A. `userspace`
- B. `iptables`
- C. `nginx`
- D. `ebpf`

---

### Question 6 — `[NET · EndpointSlices · Single]`
Why did Kubernetes introduce `EndpointSlices` to replace the monolithic `Endpoints` resource in large-scale production clusters?
- A. Standard Endpoints store all Pod IPs in a single API object; for Services with thousands of Pods, minor updates produce massive etcd payloads and API server serialization overhead.
- B. Endpoints do not support the UDP transport protocol.
- C. EndpointSlices automatically inject mutual TLS certificates.
- D. Endpoints are hard-limited to a maximum of 10 Pods.

---

### Question 7 — `[CLI · Imperative Expose · Single]`
Which command is the fastest way to expose an existing Deployment named `web-deploy` as a `ClusterIP` Service listening on port `80` and forwarding to target container port `8080`?
- A. `kubectl create service clusterip web-deploy --port=80:8080`
- B. `kubectl expose deployment web-deploy --port=80 --target-port=8080 --type=ClusterIP`
- C. `kubectl run service web-deploy --port=80 --target=8080`
- D. `kubectl apply service web-deploy -p 80:8080`

---

### Question 8 — `[NET · Service TargetPort · Single]`
In a Kubernetes Service manifest, what is the distinction between `port` and `targetPort`?
- A. `port` is the port exposed on the container; `targetPort` is the port exposed on the Service.
- B. `port` is the port exposed by the Service to callers; `targetPort` is the actual port where the container process is listening inside the Pod.
- C. `port` and `targetPort` must always have identical numerical values.
- D. `targetPort` is only valid when configuring NodePort Services.

---

### Question 9 — `[NET · ExternalName Service · Single]`
What is the primary architectural purpose of a Service with `type: ExternalName`?
- A. Mapping an internal Kubernetes Service name to an external DNS CNAME record (e.g., `db.external-cloud.com`) without proxying traffic through kube-proxy.
- B. Exposing an application to the public internet using an external cloud public IP address.
- C. Load balancing traffic across two distinct Kubernetes clusters.
- D. Creating static DNS aliases for Static Pods.

---

### Question 10 — `[NET · CoreDNS Pod Placement · Single]`
In a standard Kubernetes cluster initialized with kubeadm, in which namespace and controller type are CoreDNS Pods deployed?
- A. Namespace `default`, as a `DaemonSet`
- B. Namespace `kube-system`, as a `Deployment`
- C. Namespace `kube-public`, as a `StatefulSet`
- D. Namespace `kube-node-lease`, as a `Static Pod`

---

### Question 11 — `[NET · Kube-proxy IPVS · Single]`
What is the primary performance advantage of running `kube-proxy` in `ipvs` mode over `iptables` mode in clusters running tens of thousands of Services?
- A. IPVS consumes excessive RAM to maximize network caching.
- B. IPVS uses kernel hash tables with $O(1)$ lookup complexity rather than sequential rule traversal $O(N)$ in iptables chains, preventing latency degradation as Service counts scale.
- C. IPVS operates without requiring Linux kernel networking modules.
- D. IPVS automatically issues SSL/TLS certificates.

---

### Question 12 — `[NET · Service SessionAffinity · Single]`
To ensure that all requests originating from a specific client IP address are consistently routed to the same backend Pod at Layer 4 (Sticky Sessions), which field must be configured in the Service specification?
- A. `spec.sessionAffinity: ClientIP`
- B. `spec.stickySession: true`
- C. `spec.cookieAffinity: Enabled`
- D. `spec.loadBalancerSourceRanges: ClientIP`

---

### Question 13 — `[NET · Kubernetes Network Model · Single]`
Which of the following principles is a fundamental tenet of the Kubernetes Network Model?
- A. Every Pod can communicate with every other Pod across all nodes without utilizing Network Address Translation (NAT).
- B. Pods residing on different worker nodes must pass through a centralized NAT gateway.
- C. Each container inside the same Pod is assigned a distinct IP address.
- D. Worker nodes cannot communicate directly with Pods via the Pod IP address.

---

### Question 14 — `[NET · NodePort Routing · Single]`
A Service of type `NodePort` is created with `nodePort: 31000`. An external client sends a request to the IP address of Worker Node 1 on port 31000, but the actual backend Pod is running on Worker Node 2. What happens?
- A. The request is rejected, and the client receives a connection refused error.
- B. `kube-proxy` on Worker Node 1 intercepts the packet and forwards it across the overlay network to the backend Pod on Worker Node 2.
- C. Kubelet automatically migrates the Pod from Worker Node 2 to Worker Node 1.
- D. The request is routed back to the Control Plane for rerouting.

---

### Question 15 — `[NET · CoreDNS Debugging · Single]`
When cluster workloads report that they cannot resolve internal Service names, what should an administrator verify first?
- A. Verify that the `coredns` Pods in namespace `kube-system` are in `Running` state and that the `kube-dns` Service exists with valid endpoints.
- B. Reboot all worker nodes in the cluster.
- C. Delete `/etc/resolv.conf` on the host machine.
- D. Upgrade the underlying container runtime version.
