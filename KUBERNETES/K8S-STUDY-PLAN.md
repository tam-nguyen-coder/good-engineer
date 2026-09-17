# 🎯 Kế hoạch luyện thi Certified Kubernetes Administrator (CKA) & Master Kubernetes Production

> Tài liệu này là **lộ trình học + checklist toàn diện** cho Kubernetes, xây theo đúng phương pháp và cấu trúc đã chuẩn hoá trong `DVA-C02` và `KAFKA`.
> Bạn đã có nền tảng vững chắc về AWS (`SAA-C03`, `DVA-C02`), Docker container (`ECS`/`Fargate`/`ECR`), networking (`VPC`, `ALB`), và streaming (`Kafka`) → Kubernetes **là mảnh ghép hạ tầng & container orchestration quan trọng nhất** để hoàn thiện profile Senior/Lead Cloud & Platform Engineer.
> Đích đo lường chuẩn quốc tế: **CKA (Certified Kubernetes Administrator)** từ CNCF / The Linux Foundation — bao trọn ~85% kiến thức của **CKAD (Application Developer)**.
> CKA **KHÔNG PHẢI** bài thi trắc nghiệm (Multiple Choice) như AWS mà là **100% THỰC HÀNH HANDS-ON TRÊN TERMINAL THẬT** (Performance-based exam): giải quyết sự cố, viết YAML, cấu hình networking, backup etcd, upgrade cluster ngay trên command line dưới áp lực thời gian.
>
> **📅 Kế hoạch đã chốt:** **10 tuần × ~10–12h/tuần (~110 giờ)**. Mục tiêu: **làm chủ Kubernetes trên production** và **đậu CKA với điểm an toàn ≥ 85%** — mỗi tuần có *cổng tự kiểm tra*, bài lab thực chiến, và cơ chế đảm bảo đậu (xem [§3](#3-lộ-trình-học-theo-tuần)).
>
> **Phiên bản neo:** Kubernetes **v1.35.x** — đúng phiên bản môi trường thi CKA hiện hành (CRI: `containerd`, Pod Security Admission thay thế PSP, Gateway API GA, Sidecar containers built-in, taint manager tách rời đã stable từ v1.34). Ngày lập kế hoạch: 2026-09-15 · **Ngày rà soát & cập nhật curriculum: 2026-09-17**.
>
> ⚠️ **Lưu ý curriculum:** Từ 18/02/2025 CNCF đã cập nhật syllabus CKA, bổ sung vào Domain *Cluster Architecture*: **Helm & Kustomize**, **CRDs & Operators**, **HA control plane**, **extension interfaces (CNI/CSI/CRI)**; và vào Domain *Workloads*: **workload autoscaling (HPA)**. Toàn bộ các mục này đã được bổ sung vào lộ trình (Tuần 1, 3, 4, 9).

---

## 📑 Mục lục

1. [Tổng quan kỳ thi CKA (Certified Kubernetes Administrator)](#1-tổng-quan-kỳ-thi-cka)
2. [Kubernetes nhìn từ người đã học AWS & Docker — Tận dụng cái đã biết](#2-kubernetes-nhìn-từ-người-đã-học-aws--docker)
3. [Lộ trình học chi tiết 10 tuần (~10–12h/tuần) + Cơ chế đảm bảo đậu](#3-lộ-trình-học-theo-tuần)
4. [Kiến thức theo Domain CKA chính thức](#4-kiến-thức-theo-domain-cka)
5. [Deep-dive từng thành phần trọng tâm](#5-deep-dive-từng-thành-phần-trọng-tâm)
6. [Những con số, Cổng mạng & Config PHẢI thuộc lòng](#6-những-con-số-cổng-mạng--config-phải-thuộc-lòng)
7. [Bảng phản xạ: Tình huống / Triệu chứng → Tài nguyên / Lệnh `kubectl`](#7-bảng-phản-xạ-tình-huống--tài-nguyên--lệnh-kubectl)
8. [Thực hành hands-on (Labs bắt buộc)](#8-thực-hành-hands-on)
9. [Tài nguyên học tập & Bộ công cụ phòng thi](#9-tài-nguyên-học-tập--bộ-công-cụ-phòng-thi)
10. [Chiến lược làm bài thi thực hành 100% Performance-based](#10-chiến-lược-làm-bài-thi-thực-hành)
11. [✅ CHECKLIST TOÀN DIỆN](#11-checklist-toàn-diện)

---

## 1. Tổng quan kỳ thi CKA

| Hạng mục | Chi tiết |
|---|---|
| **Tên chứng chỉ** | Certified Kubernetes Administrator (**CKA**) |
| **Đơn vị cấp** | Cloud Native Computing Foundation (**CNCF**) & **The Linux Foundation** |
| **Hình thức thi** | **100% Hands-on Performance-based** (thao tác trực tiếp trên terminal trình duyệt PSI) |
| **Số câu hỏi / Task** | **15 – 20 tasks thực hành** (thường ~17) trên nhiều Kubernetes clusters khác nhau |
| **Thời gian** | **120 phút (2 giờ)** (~7–8 phút/task — tốc độ gõ phím & dùng lệnh imperative quyết định thành bại) |
| **Điểm đậu** | **66% (66/100)**. Mục tiêu cá nhân: **≥ 85%** |
| **Chi phí** | **445 USD** (thường có sale Cyber Monday / KubeCon còn ~250–300 USD, bao gồm **1 lần thi lại miễn phí - Free Retake** và **2 sessions Killer.sh simulator**) |
| **Môi trường thi** | Remote Proctored qua PSI Secure Browser. Cung cấp terminal Ubuntu xterm với `kubectl`, `kubeadm`, `etcdctl`, `crictl`, `vim`, `tmux`. Cluster chạy **Kubernetes v1.35** (CNCF cập nhật môi trường thi theo quý, bám sát release mới nhất). |
| **Tài liệu được tra cứu** | Mở **1 tab duy nhất** truy cập: `kubernetes.io/docs` (kể cả ô search nội bộ), `kubernetes.io/blog`, **`helm.sh/docs`**, **`gateway-api.sigs.k8s.io`**. ⚠️ `github.com/kubernetes` **KHÔNG còn** trong danh sách cho phép — mở ra có thể bị proctor cảnh cáo. Luôn kiểm tra lại trang *Important Instructions* ngay trước ngày thi. |
| **Hiệu lực** | **2 năm** (từ 01/2024, Linux Foundation chuẩn hoá hiệu lực các chứng chỉ K8s về 2 năm) |
| **Chứng chỉ liên quan** | **CKAD** (Application Developer - tập trung workloads/deployment), **CKS** (Security Specialist - yêu cầu phải có CKA trước) |

### Tỉ trọng 5 Domain CKA (Linux Foundation Exam Curriculum)

| Domain | Tên Domain | Tỉ trọng | ~Số task | Trọng tâm |
|---|---|---|---|---|
| **1** | **Troubleshooting** | **30%** | ~5 tasks | ⭐⭐⭐ Cao nhất (Sửa node NotReady, Pod CrashLoopBackOff, fix etcd/kube-apiserver crash, network break) |
| **2** | **Cluster Architecture, Installation & Configuration** | **25%** | ~4 tasks | ⭐⭐⭐ Rất cao (Kubeadm upgrade, etcd backup/restore, RBAC Role/RoleBinding, Kubelet config) |
| **3** | **Services & Networking** | **20%** | ~3 tasks | ⭐⭐⭐ Cao (Service ClusterIP/NodePort, Ingress, NetworkPolicy microsegmentation, CoreDNS) |
| **4** | **Workloads & Scheduling** | **15%** | ~2-3 tasks | ⭐⭐ Trung bình (Deployments, Rollouts, DaemonSet, Pod affinity/anti-affinity, taints/tolerations) |
| **5** | **Storage** | **10%** | ~1-2 tasks | ⭐⭐ Trung bình (PersistentVolume, PersistentVolumeClaim, StorageClass, HostPath/Local, Volume resize) |

> 💡 **Domain 1 + 2 = 55%**. Đặc thù của CKA là khả năng **gỡ lỗi (Troubleshooting) chiếm tới 30%**. Nếu chỉ biết viết YAML tạo Pod mà không biết sửa khi node `NotReady` hoặc `kube-apiserver` không khởi động được, bạn sẽ trượt. Lộ trình này thiết kế song song cả 2 kỹ năng: **xây dựng** và **sửa chữa khi vỡ vụn**.

---

## 2. Kubernetes nhìn từ người đã học AWS & Docker

### ✅ Cái bạn ĐÃ CÓ (Tận dụng ngay)

| Khái niệm AWS / Docker đã biết | Tương đương trong Kubernetes | Điểm khác biệt cần lưu ý |
|---|---|---|
| **Docker Container** | **Container** (chạy bên trong Pod) | Trong K8s, đơn vị nhỏ nhất quản lý không phải container mà là **Pod** |
| **Amazon ECS Task Definition** | **Pod Spec / Deployment Spec** | K8s Pod có thể chứa nhiều container chia sẻ chung Network IP (`localhost`) & Storage Volumes |
| **Amazon ECS Service** | **Deployment / StatefulSet** | K8s Deployment quản lý ReplicaSet, hỗ trợ Declarative Rollout/Rollback và Self-healing tự động |
| **AWS ALB / NLB** | **Ingress Controller / Gateway API** & **Service LoadBalancer** | Ingress là Layer 7 HTTP/HTTPS routing. Service NodePort/LoadBalancer ánh xạ Layer 4 |
| **Security Groups / NACL** | **NetworkPolicy** | NetworkPolicy quản lý firewall Layer 3/4 ở mức Pod. Cần CNI hỗ trợ (Calico, Cilium), Flannel cơ bản không lọc được |
| **AWS IAM Role / Policy** | **ServiceAccount + Role/RoleBinding (RBAC)** | Phân quyền bên trong cluster dùng K8s RBAC API. Kết nối ra AWS IAM bên ngoài dùng EKS IRSA (IAM Roles for Service Accounts) |
| **AWS Secrets Manager / SSM Param** | **Kubernetes Secret / ConfigMap** | K8s Secret mặc định chỉ encode Base64 (chưa mã hoá ở etcd trừ khi cấu hình EncryptionConfiguration) |
| **Amazon EBS / EFS** | **PV (PersistentVolume) / PVC** qua CSI Driver | Dynamic Provisioning qua `StorageClass` kết nối tới AWS EBS/EFS CSI driver |
| **CloudWatch Alarms / Metrics** | **Metrics Server / Prometheus + Grafana** | K8s dùng `kubectl top node/pod` cho HPA (Horizontal Pod Autoscaler) |
| **EC2 User Data / Launch Template** | **Kubelet config / Cloud-init** | Node join cluster qua `kubeadm join` với discovery token và hash CA |

### 🔥 Cái MỚI / SÂU HƠN CẦN LÀM CHỦ (Bắt buộc cho CKA)

- **Kiến trúc Control Plane tự quản (Self-hosted/Hard way)**: Hiểu tường tận cách `kube-apiserver`, `etcd`, `kube-controller-manager`, `kube-scheduler` tương tác qua mutual TLS (mTLS).
- **Làm chủ `etcd`**: Raft consensus algorithm, snapshot backup, restore disaster recovery bằng `etcdctl`, phân biệt endpoint client (2379) và peer (2380).
- **Quy trình nâng cấp Cluster (Cluster Upgrade)**: Dùng `kubeadm upgrade plan/apply` theo đúng thứ tự nghiêm ngặt (Control plane trước -> Worker node sau; drain -> upgrade -> uncordon).
- **Kỹ năng Linux & Troubleshooting hệ thống**: `systemctl status kubelet`, `journalctl -u kubelet -f`, `crictl ps`, `crictl logs`, đọc static pod manifests tại `/etc/kubernetes/manifests/`.
- **Cơ chế Networking K8s (IP-per-Pod)**: Cách CNI cấp IP, `kube-proxy` dịch iptables/IPVS, CoreDNS xử lý phân giải tên miền nội bộ (`<service>.<ns>.svc.cluster.local`).
- **Tốc độ gõ phím & Imperative `kubectl`**: Khả năng tạo YAML mẫu trong 5 giây bằng `--dry-run=client -o yaml`, thuần thục Vim (căn lề tab 2 spaces, copy/paste nhiều dòng).

> 🧠 **Câu thần chú chuyển tư duy:** Trên AWS EKS, AWS quản lý hoàn toàn Control Plane (`etcd`, `apiserver`), bạn chỉ tương tác qua `kubectl`. Trong kỳ thi CKA và môi trường Production thực thụ, **BẠN LÀ NGƯỜI QUẢN TRỊ TOÀN BỘ CỤM** — khi API server tắt thở, etcd hỏng chứng chỉ, node mất kết nối, bạn là người mở SSH vào node, mở `journalctl` và sửa từng file config.

---

## 3. Lộ trình học theo tuần

> **Kế hoạch: 10 tuần × ~10–12h/tuần (~110 giờ).**
> - **Tuần 1–4:** Core Fundamentals, Workloads, Advanced Scheduling & Lifecycle (Bao trọn CKAD).
> - **Tuần 5–7:** Services, Ingress, Advanced Networking, Security & Storage Architecture.
> - **Tuần 8–9:** Cluster Maintenance, Upgrade, etcd HA Backup/Restore & Production Hardening.
> - **Tuần 10:** Troubleshooting chuyên sâu (chiếm 30% đề) + Luyện đề Killer.sh 100% thời gian thực + Thi.

### ⏱️ Nhịp học mỗi tuần (~11h — chia 4 buổi)

| Buổi | Thời lượng | Nội dung |
|---|---|---|
| **A — Core Concepts & Architecture** | ~3h | Đọc K8s Official Documentation + Video chuyên sâu, phân tích sơ đồ luồng dữ liệu |
| **B — Hands-on CLI & Manifests** | ~3.5h | Tự tay thao tác trên cụm multi-node (Kind / Minikube / Kubeadm VM), luyện imperative command |
| **C — Deep-dive & Break-and-Fix** | ~2.5h | Cố tình làm hỏng cấu hình (inject bugs), thực hành tra cứu log và phục hồi hệ thống |
| **D — CKA Exam Simulator & Review** | ~2h | Giải 15–20 task thực hành dưới áp lực đồng hồ đếm ngược → ghi chú bẫy đề vào sổ tay |

---

### 🗓️ Chi tiết 10 tuần — Mỗi tuần một chủ đề trọng tâm

| Tuần | Trọng tâm | Domain CKA | Mốc kiểm tra quan trọng | Chi tiết & Lab |
|---|---|---|---|---|
| **1** | **Kiến trúc K8s & Control Plane** + Setup Lab Multi-node + `kubectl` Imperative Pro | ARCH (25%) | ⚡ Thành thạo `kubectl` generator trong 5s; hiểu rõ luồng API Request | [week-01/](study-plan/week-01/README.md) · [Labs](study-plan/week-01/labs.md) |
| **2** | **Workloads & Controllers** (Deployments, Rollouts, DaemonSet, StatefulSet, Jobs) | WORKLOAD (15%) | ⚡ Triển khai Zero-downtime rolling update & Canary, xử lý Rollback | [week-02/](study-plan/week-02/README.md) · [Labs](study-plan/week-02/labs.md) |
| **3** | **Pod Scheduling & Resource Management** (Affinity, Taints/Tolerations, QoS, Quotas) | SCHED (15%) | ⚡ Điều phối Pod chính xác theo node label, cô lập node bằng Taints | [week-03/](study-plan/week-03/README.md) · [Labs](study-plan/week-03/labs.md) |
| **4** | **Config, Probes & Lifecycle** (ConfigMap, Secret, Health Probes, Sidecar Native) | WORKLOAD (15%) | ⚡ Cấu hình Liveness/Readiness/Startup probes; K8s 1.28+ native sidecar | [week-04/](study-plan/week-04/README.md) · [Labs](study-plan/week-04/labs.md) |
| **5** | **Services & Networking Core** (ClusterIP, NodePort, LoadBalancer, Headless, CoreDNS) | NET (20%) | ⚡ Debug luồng gói tin iptables/IPVS, test phân giải DNS pod-to-service | [week-05/](study-plan/week-05/README.md) · [Labs](study-plan/week-05/labs.md) |
| **6** | **Ingress, Gateway API & NetworkPolicy** (L7 Routing, TLS, Pod Microsegmentation) | NET (20%) | 🎯 **Checkpoint Mini-mock 1: Workloads & Networking (≥ 75%)** | [week-06/](study-plan/week-06/README.md) · [Labs](study-plan/week-06/labs.md) |
| **7** | **Storage Architecture** (Volumes, PV, PVC, StorageClass, Dynamic Provisioning) | STORAGE (10%) | ⚡ Cấu hình PVC gắn vào Pod, xử lý reclaim policy và volume expansion | [week-07/](study-plan/week-07/README.md) · [Labs](study-plan/week-07/labs.md) |
| **8** | **Security & RBAC** (Certificates PKI, Kubeconfig, ServiceAccount, Roles, PSS/PSA) | ARCH (25%) | ⚡ Tạo User mới bằng CSR, giới hạn quyền namespace qua RoleBinding | [week-08/](study-plan/week-08/README.md) · [Labs](study-plan/week-08/labs.md) |
| **9** | **Cluster Maintenance, Upgrade & etcd Disaster Recovery** (Kubeadm, Drain, etcdctl) | ARCH (25%) | ⚡ Backup etcd, wipe database, restore thành công; nâng cấp cluster N -> N+1 | [week-09/](study-plan/week-09/README.md) · [Labs](study-plan/week-09/labs.md) |
| **10** | **Troubleshooting toàn tập (30%) + Killer.sh Simulator + Thi CKA** | TROUBLE (30%) | 🏁 **Killer.sh Session 1 & 2 (≥ 85%) → Đặt lịch thi thật** | [week-10/](study-plan/week-10/README.md) · [Labs](study-plan/week-10/labs.md) |

---

### ✅ Cơ chế ĐẢM BẢO ĐẬU (Performance-based Guarantee)

1. **Quy tắc "Không gõ YAML từ con số không" (Zero-boilerplate Rule):**
   - 100% cấu hình trong phòng thi phải được sinh bằng lệnh imperative:
     `kubectl run ... --dry-run=client -o yaml > pod.yaml`
     `kubectl create deployment ... --dry-run=client -o yaml > deploy.yaml`
   - Tuyệt đối không tự gõ tay `apiVersion`, `kind`, `metadata` từ đầu để tránh lỗi indentation (thụt dòng).
2. **Cổng kiểm tra tốc độ (Speed Gate):**
   - Mỗi task thi thật chỉ được phép làm trong **6 – 7 phút**. Nếu bị kẹt quá 8 phút ở 1 task → `flag` câu hỏi, ghi lại số điểm (%) của task và chuyển ngay sang câu tiếp theo.
3. **Cơ chế kiểm chứng lại (Verify before Moving):**
   - Sau khi tạo hoặc sửa bất kỳ tài nguyên nào, LUÔN LUÔN dùng lệnh kiểm tra trạng thái hoạt động:
     - Đã tạo Pod? → `kubectl get pod <name> -w` (đợi status `Running` và `1/1 Ready`).
     - Đã sửa Service? → `kubectl get ep <service-name>` (đảm bảo Endpoints có danh sách IP Pod).
     - Đã restore etcd? → `kubectl get nodes` (đảm bảo apiserver phản hồi và nodes `Ready`).
4. **Ngưỡng thi thử trên Killer.sh:**
   - Đề thi thử Killer.sh được CNCF tặng kèm khi mua voucher CKA có độ khó cao hơn đề thi thật khoảng **30–40%**.
   - **Chỉ đi thi thật khi làm Killer.sh đạt ≥ 80–85 điểm** trong lần làm thứ hai (sau khi đã review kỹ toàn bộ giải thích).

---

## 4. Kiến thức theo Domain CKA

### 🟦 1. Troubleshooting (30% — Tỉ trọng cao nhất)
- **Task 1.1: Troublehoot Cluster Nodes**: Node chuyển trạng thái `NotReady`. Kiểm tra dịch vụ `systemctl status kubelet`, xem log `journalctl -u kubelet -e`. Kiểm tra dung lượng ổ đĩa (`df -h`), bộ nhớ (`free -m`), runtime containerd (`systemctl status containerd`, `crictl info`). Sửa file cấu hình kubelet `/var/lib/kubelet/config.yaml`.
- **Task 1.2: Troubleshoot Control Plane Components**: Khắc phục sự cố static pod manifests tại `/etc/kubernetes/manifests/` (`kube-apiserver.yaml`, `kube-controller-manager.yaml`, `kube-scheduler.yaml`, `etcd.yaml`). Xem log container cấp thấp bằng `crictl ps -a` và `crictl logs <container-id>` khi apiserver không chạy.
- **Task 1.3: Troubleshoot Workloads & Applications**: Debug lỗi `CrashLoopBackOff` (lỗi code, thiếu biến môi trường), `ImagePullBackOff` / `ErrImagePull` (sai tag, sai registry secret), `OOMKilled` (vượt memory limit, exit code 137), `CreateContainerConfigError` (thiếu ConfigMap/Secret), `Pending` (không đủ tài nguyên, dính Taint hoặc nodeSelector không khớp). Dùng `kubectl logs`, `kubectl describe`, `kubectl get events`.
- **Task 1.4: Troubleshoot Services & Networking**: Kiểm tra kết nối DNS qua CoreDNS (`kubectl get pods -n kube-system -l k8s-app=kube-dns`). Test phân giải tên miền bằng `nslookup` hoặc `dig` trong temporary pod (`kubectl run test-dns --image=busybox:1.28 --rm -it -- nslookup ...`). Kiểm tra iptables/kube-proxy, kiểm tra selectors trên Service có khớp chính xác Labels của Pod không.

### 🟩 2. Cluster Architecture, Installation & Configuration (25%)
- **Task 2.1: Role-Based Access Control (RBAC)**: Tạo `Role`, `ClusterRole`, `RoleBinding`, `ClusterRoleBinding`. Gán quyền theo verbs (`get`, `list`, `watch`, `create`, `delete`) trên resources cụ thể. Kiểm tra quyền hạn bằng `kubectl auth can-i <verb> <resource> --as <user> -n <namespace>`. Cấu hình `ServiceAccount` và Bound ServiceAccount Tokens.
- **Task 2.2: Kubeadm Cluster Deployment & Upgrade**: Khởi tạo cluster với `kubeadm init`, join worker node bằng `kubeadm join`. Nâng cấp cluster an toàn:
  1. `kubectl drain <cp-node> --ignore-daemonsets`
  2. Nâng cấp `kubeadm` (`apt-get install -y kubeadm=...`)
  3. `kubeadm upgrade apply v...`
  4. Nâng cấp `kubelet` & `kubectl`, khởi động lại service
  5. `kubectl uncordon <cp-node>`
  6. Lặp lại cho từng worker node với `kubeadm upgrade node`.
- **Task 2.3: Backup & Restore etcd Database**: Lưu snapshot etcd bằng lệnh `etcdctl snapshot save` sử dụng chứng chỉ client certs (`/etc/kubernetes/pki/etcd/`). Kiểm tra tính toàn vẹn với `etcdctl snapshot status`. Phục hồi cụm từ file snapshot với `etcdctl snapshot restore --data-dir=<new-path>` và trỏ lại volume path trong manifest static pod etcd.
- **Task 2.4: Managing Kubeconfig**: Cấu hình và quản lý file `~/.kube/config`, làm việc với clusters, users, contexts. Chuyển đổi context nhanh bằng `kubectl config use-context <name>`.

### 🟨 3. Services & Networking (20%)
- **Task 3.1: Service Networking**: Cấu hình và hiểu rõ các loại Service: `ClusterIP` (nội bộ), `NodePort` (cổng 30000-32767 trên tất cả các node), `LoadBalancer` (tích hợp cloud provider), `Headless Service` (`clusterIP: None` dùng cho StatefulSet). Quản lý `Endpoints` và `EndpointSlices`.
- **Task 3.2: Ingress Controllers & Ingress Resources**: Viết manifest `Ingress` định tuyến Layer 7 (host-based và path-based routing). Cấu hình TLS termination với Kubernetes Secret kiểu `kubernetes.io/tls`.
- **Task 3.3: Kubernetes Gateway API**: Hiểu mô hình kế thừa hiện đại của Ingress: tách quyền giữa Cluster Operator (`GatewayClass`, `Gateway`) và Application Developer (`HTTPRoute`, `GRPCRoute`).
- **Task 3.4: NetworkPolicy**: Triển khai chính sách tường lửa bảo vệ Pod. Thiết lập `default-deny` ingress/egress. Sử dụng `podSelector`, `namespaceSelector`, `ipBlock`, và port specifications để thực hiện microsegmentation.
- **Task 3.5: CoreDNS Configuration**: Cấu hình ConfigMap `coredns` trong namespace `kube-system` (thêm custom upstream DNS, custom hosts).

### 🟪 4. Workloads & Scheduling (15%)
- **Task 4.1: Deployments & Rolling Updates**: Quản lý chiến lược nâng cấp ứng dụng: `RollingUpdate` (`maxSurge`, `maxUnavailable`) vs `Recreate`. Kiểm tra tiến trình rollout bằng `kubectl rollout status`, xem lịch sử bằng `kubectl rollout history`, hoàn tác khi gặp sự cố bằng `kubectl rollout undo`.
- **Task 4.2: Specialized Workloads**: Cấu hình `DaemonSet` (chạy 1 bản sao trên mọi node cho logging/monitoring), `StatefulSet` (danh tính mạng ổn định, volume riêng biệt cho database), `Job` & `CronJob` (chạy tác vụ theo lô, lịch cron, quản lý `concurrencyPolicy`).
- **Task 4.3: Manual & Advanced Scheduling**:
  - Gán Pod thủ công vào node bằng trường `nodeName`.
  - Sử dụng `nodeSelector` và `nodeAffinity` (`requiredDuringSchedulingIgnoredDuringExecution` vs `preferredDuringSchedulingIgnoredDuringExecution`).
  - Phân tán Pod bằng `podAntiAffinity` (đảm bảo tính sẵn sàng cao không bị dồn Pod vào 1 node/zone).
  - Tách biệt hạ tầng với `Taints` (`key=value:NoSchedule`) trên Node và `Tolerations` tương ứng trên Pod.
- **Task 4.4: Static Pods**: Tạo và quản lý Pod độc lập không thông qua API server, do kubelet tự quản lý từ thư mục manifest địa phương (mặc định `/etc/kubernetes/manifests/`).

### 🟫 5. Storage (10%)
- **Task 5.1: Persistent Volumes (PV) & Claims (PVC)**: Khai báo PV (Static provisioning) với các loại storage (`hostPath`, `nfs`, cloud disk). Tạo PVC để yêu cầu dung lượng lưu trữ. Gắn PVC vào Pod thông qua `volumes` và `volumeMounts`.
- **Task 5.2: Storage Classes & Dynamic Provisioning**: Cấu hình `StorageClass` với provisioner phù hợp, thiết lập `reclaimPolicy` (`Delete` vs `Retain`) và `volumeBindingMode` (`Immediate` vs `WaitForFirstConsumer` — trì hoãn tạo ổ đĩa cho đến khi Pod được lập lịch tới Node cụ thể).
- **Task 5.3: Volume Operations**: Nâng cấp mở rộng dung lượng volume (`allowVolumeExpansion: true`), hiểu rõ các `accessModes`: `ReadWriteOnce` (RWO), `ReadOnlyMany` (ROX), `ReadWriteMany` (RWX), `ReadWriteOncePod` (RWOP).

---

## 5. Deep-dive từng thành phần trọng tâm

### ⭐ 1. Kiến trúc Control Plane & Kubelet (Trọng tâm CKA #1)
- **`kube-apiserver`**: Cửa ngõ duy nhất của cluster. Tất cả các thành phần khác (kể cả etcd, scheduler, kubelet) đều chỉ nói chuyện với API server. Stateless, scale out bằng cách chạy nhiều bản sao phía sau Load Balancer. Chứng thực qua mTLS (`/etc/kubernetes/pki/`).
- **`etcd`**: Key-value store phân tán lưu toàn bộ trạng thái của cluster. Sử dụng thuật toán đồng thuận Raft. Cần số node lẻ (1, 3, 5) để tránh split-brain (quản lý quorum: `(N/2) + 1`).
- **`kube-scheduler`**: Theo dõi các Pod mới tạo chưa có `nodeName` và chọn ra Node tối ưu nhất qua 2 pha: **Filtering** (lọc node đủ điều kiện tài nguyên/taints) và **Scoring** (chấm điểm node tốt nhất theo affinity/phân tán).
- **`kube-controller-manager`**: Chạy vô số vòng lặp điều khiển (control loops: Node Controller, Deployment Controller, EndpointSlice Controller, Namespace Controller) để đưa trạng thái thực tế (Current State) về trạng thái mong muốn (Desired State).
- **`kubelet`**: Agent chạy trên từng Worker Node (dưới dạng Linux Systemd Service, không chạy trong container). Giao tiếp với Container Runtime qua **CRI** (`containerd`), quản lý vòng đời container, kiểm tra Health Check Probes, gắn Volume, báo cáo trạng thái Node về API server.
- **`kube-proxy`**: Quản lý luật mạng trên từng Node, dịch Service ClusterIP/NodePort thành IP thực của Pod thông qua `iptables` hoặc `IPVS` mode.
- **Bẫy thi:** Khi API server bị treo hoặc sửa sai file manifest tại `/etc/kubernetes/manifests/`, lệnh `kubectl` sẽ trả về lỗi `The connection to the server <host>:6443 was refused`. Để sửa, phải SSH trực tiếp vào node control plane, xem log container bằng `crictl ps -a` và `crictl logs`.

### ⭐ 2. etcd Backup & Disaster Recovery (Câu hỏi 100% xuất hiện trong CKA)
- **Biến môi trường `ETCDCTL_API` (đọc kỹ):**
  ```bash
  export ETCDCTL_API=3   # Chỉ cần cho etcdctl < 3.4
  ```
  > ⚠️ Từ **etcdctl v3.4 trở lên, API v3 đã là mặc định** — môi trường thi CKA v1.35 dùng etcd 3.5/3.6 nên **KHÔNG bắt buộc** export biến này. Gõ thêm cũng vô hại (nhiều tài liệu cũ vẫn ghi), nhưng đừng mất thời gian và đừng hoảng khi không thấy nó trong đáp án mẫu.
- **Lệnh Backup Snapshot:**
  ```bash
  etcdctl --endpoints=https://127.0.0.1:2379 \
    --cacert=/etc/kubernetes/pki/etcd/ca.crt \
    --cert=/etc/kubernetes/pki/etcd/server.crt \
    --key=/etc/kubernetes/pki/etcd/server.key \
    snapshot save /opt/snapshot-backup.db
  ```
- **Lệnh Verify Snapshot:**
  ```bash
  etcdctl --write-out=table snapshot status /opt/snapshot-backup.db
  ```
- **Lệnh Restore Snapshot sang thư mục data mới:**
  ```bash
  etcdctl snapshot restore /opt/snapshot-backup.db \
    --data-dir=/var/lib/etcd-restored
  ```
- **Bước quyết định sau khi Restore:** Mở file `/etc/kubernetes/manifests/etcd.yaml`, tìm trường `hostPath` của volume `etcd-data` và đổi từ `/var/lib/etcd` thành `/var/lib/etcd-restored`. Kubelet sẽ tự động restart pod etcd với dữ liệu mới khôi phục.

### ⭐ 3. RBAC (Authentication & Authorization)
- **Luồng chứng thực & phân quyền:**
  1. Client gửi request kèm X.509 Client Cert / Bearer Token.
  2. API server xác thực danh tính (**Authentication**).
  3. API server kiểm tra quyền hạn (**Authorization** via RBAC).
  4. Admission Controllers kiểm tra & sửa đổi request trước khi ghi vào etcd.
- **Role vs ClusterRole:**
  - `Role`: Giới hạn trong phạm vi **1 Namespace** cụ thể (Pods, Deployments, Services, ConfigMaps).
  - `ClusterRole`: Có hiệu lực trên **toàn bộ Cluster** (Nodes, Namespaces, PVs, StorageClasses) HOẶC định nghĩa quyền chung để tái sử dụng trên nhiều namespace.
- **RoleBinding vs ClusterRoleBinding:**
  - `RoleBinding`: Gắn `Role` (hoặc `ClusterRole`) cho User/Group/ServiceAccount trong **1 Namespace**.
  - `ClusterRoleBinding`: Gắn `ClusterRole` cho User/Group/ServiceAccount trên **toàn Cluster**.
- **Lệnh kiểm tra quyền hạn cực nhanh (Life Saver trong phòng thi):**
  ```bash
  kubectl auth can-i create deployment --as dev-user -n development
  kubectl auth can-i delete nodes --as system:serviceaccount:prod:app-sa
  ```

### ⭐ 4. NetworkPolicy (Bảo vệ luồng mạng Pod-to-Pod)
- **Nguyên lý cốt lõi:**
  - Nếu một Pod **chưa được chọn** bởi bất kỳ `NetworkPolicy` nào → Pod ở trạng thái **Non-isolated** (nhận/gửi traffic tự do).
  - Ngay khi Pod **được chọn** bởi 1 `NetworkPolicy` (`podSelector`) → Pod chuyển sang trạng thái **Isolated**. Tất cả traffic không được định nghĩa rõ ràng trong `ingress` hoặc `egress` sẽ bị **DROP toàn bộ** (Default Deny).
- **Quy tắc phân biệt `namespaceSelector` vs `podSelector`:**
  - Viết cùng 1 object trong danh sách `from` (dấu `-` chung) → điều kiện **AND** (Phải thuộc Namespace X VÀ có nhãn Pod Y).
  - Viết tách thành 2 object riêng trong `from` (2 dấu `-` khác nhau) → điều kiện **OR** (Thuộc Namespace X HOẶC có nhãn Pod Y).

### ⭐ 5. Storage: PV, PVC & StorageClass Binding
- **Vòng đời Storage:**
  1. Admin tạo `StorageClass` hoặc tạo sẵn `PersistentVolume` (dung lượng, access mode, reclaim policy).
  2. Developer tạo `PersistentVolumeClaim` để request dung lượng.
  3. Control plane khớp các tiêu chí (Capacity, AccessModes, StorageClassName) và tiến hành **Bind** PVC vào PV.
  4. Developer khai báo volume trong Pod trỏ tới `claimName`.
- **Chế độ VolumeBindingMode:**
  - `Immediate`: PV được tạo và bind ngay khi PVC xuất hiện (nguy cơ: PV gắn ở Zone A, nhưng Pod sau này bị Scheduler xếp vào Zone B → lỗi không gắn được disk).
  - `WaitForFirstConsumer`: Trì hoãn việc tạo và bind PV cho đến khi Pod đầu tiên dùng PVC này được lập lịch vào 1 Node cụ thể (khuyến nghị số 1 cho multi-zone cluster).

---

## 6. Những con số, Cổng mạng & Config PHẢI thuộc lòng

> Trong phòng thi CKA, việc dừng lại để search google xem port nào của etcd hay range NodePort là bao nhiêu sẽ làm bạn mất điểm vì hết giờ. Hãy học thuộc bảng này:

### 🌐 Cổng mạng mặc định (Default Network Ports)

| Thành phần | Cổng mặc định | Giao thức / Mục đích |
|---|---|---|
| **`kube-apiserver`** | **`6443`** | HTTPS REST API client giao tiếp với cluster |
| **`etcd` client** | **`2379`** | Giao tiếp giữa API server và etcd |
| **`etcd` peer** | **`2380`** | Đồng bộ dữ liệu Raft giữa các etcd node |
| **`kubelet` API** | **`10250`** | API server gọi kubelet (lấy logs, exec, metrics) |
| **`kube-scheduler`** | **`10259`** | Cổng an toàn HTTPS của scheduler |
| **`kube-controller-manager`** | **`10257`** | Cổng an toàn HTTPS của controller-manager |
| **`NodePort Services`** | **`30000 – 32767`** | Dải cổng mặc định expose trên Node IP cho NodePort |
| **`CoreDNS`** | **`53`** | UDP/TCP phân giải tên miền trong cluster |

### ⏱️ Thông số Thời gian & Giới hạn Cần nhớ

| Tham số / Khái niệm | Giá trị mặc định / Quy chuẩn | Ý nghĩa trong vận hành & đề thi |
|---|---|---|
| **`terminationGracePeriodSeconds`** | **`30s`** | Thời gian chờ từ `SIGTERM` đến khi gửi `SIGKILL` |
| **`--node-monitor-grace-period`** | **`50s`** (từ v1.32; trước đó là `40s`) | Thời gian node-lifecycle-controller không nhận heartbeat trước khi đánh Node thành `NotReady` |
| **`tolerationSeconds`** của taint `node.kubernetes.io/not-ready:NoExecute` | **`300s (5 phút)`** | Thời gian Pod được phép bám trụ trên Node `NotReady` trước khi bị evict. ⚠️ Cờ cũ `--pod-eviction-timeout` của `kube-controller-manager` **đã bị gỡ bỏ** (từ v1.27) — cơ chế hiện tại là **taint-based eviction**, chỉnh bằng `tolerations` trong Pod spec |
| **Liveness/Readiness probe defaults** | `periodSeconds: 10`, `timeoutSeconds: 1`, `failureThreshold: 3` | Tần suất và ngưỡng đếm trước khi restart Pod hoặc gỡ khỏi Service |
| **OOMKilled Exit Code** | **`137`** (`128 + 9` SIGKILL) | Container bị nhân Linux kill vì vượt quá Memory Limits |
| **Graceful Exit Code** | **`143`** (`128 + 15` SIGTERM) | Container kết thúc bình thường khi nhận lệnh dừng |
| **Error in Code Exit Code** | **`1`** | Lỗi runtime bên trong ứng dụng |
| **DNS Format chuẩn Service** | `<svc>.<ns>.svc.cluster.local` | Địa chỉ FQDN đầy đủ để truy vấn Service từ namespace khác |
| **DNS Format chuẩn Pod** | `<pod-ip-thay-dấu-chấm-bằng-gạch>.<ns>.pod.cluster.local` | Ví dụ IP `10-244-1-5.default.pod.cluster.local` |

---

## 7. Bảng phản xạ: Tình huống → Tài nguyên / Lệnh `kubectl`

> Kỹ năng phản xạ giúp giải quyết bài thi CKA trong chớp mắt: Đọc đề bài → Bật ngay câu lệnh / giải pháp.

| Tình huống / Yêu cầu trong bài thi | Phản xạ tới tài nguyên / Lệnh CLI chuẩn xác |
|---|---|
| Tạo Pod Nginx nhanh nhất | `kubectl run my-pod --image=nginx` |
| Tạo file YAML mẫu cho Pod / Deployment | Thêm `--dry-run=client -o yaml > file.yaml` |
| Expose Pod thành Service ClusterIP trên cổng 80 | `kubectl expose pod my-pod --port=80 --target-port=80` |
| Expose Deployment thành Service NodePort cổng 30080 | `kubectl expose deploy my-dep --type=NodePort --port=80` rồi sửa `nodePort: 30080` |
| Lấy file YAML của tài nguyên đang chạy sạch sẽ | `kubectl get deploy my-dep -o yaml --show-managed-fields=false` rồi xoá tay `status`, `uid`, `resourceVersion`, `creationTimestamp`. ⚠️ **`kubectl neat` KHÔNG được cài trong phòng thi** — chỉ dùng được ở lab local |
| Xem tài nguyên chiếm CPU/Memory | `kubectl top nodes` / `kubectl top pods --sort-by=memory` |
| Tìm xem Pod nào đang chạy trên Node nào | `kubectl get pods -o wide -A` |
| Xem toàn bộ log của Pod có nhiều container | `kubectl logs <pod-name> -c <container-name> --previous` |
| Node trạng thái `NotReady` | SSH vào Node → `systemctl status kubelet` → `journalctl -u kubelet -e --no-pager` |
| Không cho Pod mới lên Node để chuẩn bị bảo trì | `kubectl cordon <node-name>` |
| Di dời toàn bộ Pod khỏi Node một cách an toàn | `kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --force` |
| Đưa Node quay trở lại nhận Pod | `kubectl uncordon <node-name>` |
| Đổi Namespace làm việc mặc định trong Terminal | `kubectl config set-context --current --namespace=<ns-name>` |
| Thêm Taint chặn xếp Pod lên Node | `kubectl taint nodes <node-name> key=value:NoSchedule` |
| Gỡ bỏ Taint khỏi Node | `kubectl taint nodes <node-name> key=value:NoSchedule-` (thêm dấu trừ ở cuối) |
| Đổi Image của Deployment trực tiếp | `kubectl set image deployment/my-dep nginx=nginx:1.25` |
| Hoàn tác phiên bản Deployment bị lỗi | `kubectl rollout undo deployment/my-dep` |
| Kiểm tra quyền của một User | `kubectl auth can-i list pods -n prod --as alice` |
| Sửa trực tiếp resource mà không cần tải file | `kubectl edit <resource> <name>` |
| Test kết nối HTTP ngay bên trong cluster | `kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- curl <url>` |

---

## 8. Thực hành hands-on

> **CKA là bài thi thực hành 100%.** Nếu chỉ đọc lý thuyết mà không gõ phím, cơ hội đậu là 0%. Dưới đây là các nhóm bài lab bắt buộc phải làm đi làm lại nhiều lần.

### 🧪 Nhóm 1: Thiết lập môi trường Lab Multi-node Local
- [ ] Dựng cụm Kubernetes Multi-node (1 Control Plane, 2 Worker Nodes) bằng **Kind (Kubernetes in Docker)** với file config `kind-config.yaml`.
- [ ] Cấu hình alias `k=kubectl`, bật Bash Auto-completion, cấu hình file `.vimrc` tối ưu cho việc căn chỉnh YAML (`set ts=2 sw=2 et paste`).
- [ ] Dùng `kubectl` tạo Namespace, Pod, ReplicaSet, Deployment thuần bằng lệnh imperative.

### 🧪 Nhóm 2: Workloads, Deployments & Scheduling
- [ ] Triển khai một Deployment với 5 bản sao (replicas), thực hiện Rolling Update sang image mới, theo dõi trạng thái `rollout status`, thực hiện tạm dừng (`pause`), tiếp tục (`resume`), và `undo` về phiên bản cũ.
- [ ] Cấu hình `DaemonSet` chạy Fluentd logging agent trên mọi worker node.
- [ ] Cấu hình `Taints` trên Worker Node 1 (`tier=backend:NoSchedule`) và tạo Pod có `Tolerations` tương ứng.
- [ ] Sử dụng `nodeAffinity` để ép buộc Pod chỉ chạy trên các node có label `topology.kubernetes.io/zone=us-east-1a`.
- [ ] Cấu hình Multi-container Pod với Native Sidecar container (K8s 1.28+ `restartPolicy: Always` trong `initContainers`).

### 🧪 Nhóm 3: Networking & Services
- [ ] Tạo Deployment Backend và expose bằng Service `ClusterIP`.
- [ ] Tạo Temporary Pod trong cluster, truy vấn backend thông qua FQDN CoreDNS (`<svc>.<ns>.svc.cluster.local`).
- [ ] Cài đặt Ingress Controller (Nginx Ingress) và viết Ingress Resource định tuyến theo đường dẫn `/api` và `/web`.
- [ ] Thiết lập NetworkPolicy: Khởi tạo chính sách `default-deny-all`, sau đó chỉ mở cổng 80 cho các Pod mang nhãn `role=frontend`.

### 🧪 Nhóm 4: Storage PV/PVC & StorageClass
- [ ] Tạo PersistentVolume kiểu `hostPath` với dung lượng 2Gi, accessMode `ReadWriteOnce`, reclaimPolicy `Retain`.
- [ ] Tạo PersistentVolumeClaim yêu cầu 1Gi storage và kiểm tra trạng thái tự động Bind vào PV.
- [ ] Gắn PVC vào một Pod Nginx tại đường dẫn `/usr/share/nginx/html`. Tạo file `index.html`, xoá Pod và tạo Pod mới để kiểm chứng dữ liệu không bị mất.

### 🧪 Nhóm 5: Security & RBAC
- [ ] Tạo private key và Certificate Signing Request (CSR) cho user `developer`. Ký duyệt certificate bằng `kubectl certificate approve`.
- [ ] Tạo `Role` cho phép `get`, `list`, `create` trên Pods trong namespace `dev`.
- [ ] Tạo `RoleBinding` gán Role trên cho user `developer`. Kiểm tra quyền bằng `kubectl auth can-i`.
- [ ] Cấu hình Pod Security Admission (PSA) ở mức `restricted` trên một namespace và quan sát Pod bị chặn khi vi phạm SecurityContext.

### 🧪 Nhóm 6: Cluster Administration & Troubleshooting (Cốt lõi CKA)
- [ ] **Thực hành etcd Backup & Restore:** Lưu snapshot etcd của cụm đang chạy, xoá thử một Deployment quan trọng, thực hiện restore snapshot vào thư mục mới và trỏ lại etcd manifest để khôi phục lại Deployment đã mất.
- [ ] **Thực hành Kubeadm Upgrade:** Nâng cấp cụm từ bản v1.34 lên v1.35 theo đúng quy trình: drain node -> upgrade kubeadm -> upgrade apply -> upgrade kubelet/kubectl -> uncordon node.
- [ ] **Break-and-Fix Lab:**
  - Làm hỏng file cấu hình `/var/lib/kubelet/config.yaml` và debug bằng `journalctl` để sửa lại.
  - Sửa sai port hoặc certificate path trong `/etc/kubernetes/manifests/kube-apiserver.yaml` và khắc phục khi `kubectl` mất kết nối.
  - Sửa lỗi CoreDNS bị treo khiến các service trong cluster không gọi được nhau qua tên miền.

---

## 9. Tài nguyên học tập & Bộ công cụ phòng thi

### 🎯 Bộ Đề Thi Thử Thực Tế (100% Tiếng Anh Chuẩn Format Thi Thật)
Để làm quen với áp lực thời gian và giao diện dòng lệnh trên Linux Foundation, repo cung cấp **3 bộ Mock Exam thực chiến toàn diện (mỗi đề 17 tasks, 120 phút)**:
- 🛡️ **[Tài Liệu Validate Kiến Thức "Chắc Chắn Đậu" (VALIDATION.md)](study-plan/VALIDATION.md)** — Bảng tổng kiểm kê kiến thức hiện đại (K8s v1.35), Top 12 bẫy thi CKA và lệnh cấp cứu.
- 📝 **[Real Mock Exam 01: Core Standard Exam (17 Tasks)](real-exam-mocks/REAL-MOCK-EXAM-01.md)** — Kubeadm Upgrade, ETCD Backup & Restore, Node NotReady, RBAC, NetworkPolicy, Ingress TLS, CSR.
- 📝 **[Real Mock Exam 02: Killer.sh Advanced Scenarios (17 Tasks)](real-exam-mocks/REAL-MOCK-EXAM-02.md)** — Multi-AZ Storage `WaitForFirstConsumer`, Secondary Scheduler, StatefulSet, CronJob forbid, Kubelet cgroup mismatch.
- 📝 **[Real Mock Exam 03: Speed, Accuracy & Modern Scenarios (17 Tasks)](real-exam-mocks/REAL-MOCK-EXAM-03.md)** — Secret Encryption at rest, Gateway API `HTTPRoute`, Kube-proxy fix, PDB drain, PV retain reclaim.
- 📌 **[Hướng dẫn quy chế thi & barem chấm điểm Mock Exam](real-exam-mocks/README.md)**

### 📖 Tài liệu ôn tập & Khóa học khuyến nghị
1. **Khóa học Video #1 thị trường:**
   - **Certified Kubernetes Administrator (CKA) with Practice Tests** của **Mumshad Mannambeth (KodeKloud)** trên Udemy / KodeKloud platform. Khóa học có hệ thống lab tương tác trực quan xuất sắc nhất cho người mới bắt đầu.
2. **Kỳ thi thử giả lập bắt buộc:**
   - **Killer.sh CKA Simulator**: Đi kèm miễn phí 2 lượt khi đăng ký thi CKA. Đây là "thao trường" rèn luyện tốt nhất thế giới hiện nay cho CKA, độ khó cao hơn đề thật giúp bạn tự tin tuyệt đối.
3. **Trang tài liệu được phép mở trong phòng thi:**
   - [Kubernetes Documentation](https://kubernetes.io/docs/)
   - [Kubernetes Tasks](https://kubernetes.io/docs/tasks/)
   - [Kubernetes Reference Sheets (Cheat Sheet)](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

### 🛠️ Bộ phím tắt & Cấu hình môi trường phòng thi (Gõ ngay khi vào thi)

Khi vừa bắt đầu làm bài thi CKA, việc đầu tiên cần làm trong terminal (chỉ mất 30 giây) là thiết lập các alias và cấu hình Vim:

```bash
# 1. Alias cho kubectl và namespace
alias k=kubectl
alias kgp="kubectl get pods"
alias kgs="kubectl get svc"
alias kgd="kubectl get deploy"

# 2. Cấu hình dry-run nhanh
export do="--dry-run=client -o yaml"
export now="--force --grace-period=0"

# 3. Bật autocompletion cho alias k
source <(kubectl completion bash)
complete -o default -F __start_kubectl k

# 4. Cấu hình Vim tối ưu căn dòng YAML (Ghi vào ~/.vimrc)
cat <<EOF > ~/.vimrc
set tabstop=2
set shiftwidth=2
set expandtab
set paste
set number
EOF
```

> 💡 **Cách dùng biến `$do` và `$now`:**
> - Tạo nhanh Pod YAML: `k run my-pod --image=nginx $do > pod.yaml`
> - Tạo nhanh Deployment: `k create deploy my-dep --image=nginx --replicas=3 $do > deploy.yaml`
> - Xoá Pod ngay lập tức không cần đợi 30s: `k delete pod bad-pod $now`

---

## 10. Chiến lược làm bài thi thực hành

1. **QUAN TRỌNG NHẤT: Chuyển đổi ngữ cảnh Context trước mỗi câu hỏi:**
   - Ở đầu mỗi task thi CKA, đề bài **LUÔN CUNG CẤP 1 DÒNG LỆNH ĐỔI CONTEXT** (Ví dụ: `kubectl config use-context k8s`).
   - **BẮT BUỘC COPY VÀ CHẠY LỆNH NÀY ĐẦU TIÊN!** Nếu làm đúng hết các bước nhưng làm trên sai cluster context, bạn sẽ bị **0 điểm** cho task đó.
2. **Chú ý Namespace:**
   - Đọc kỹ yêu cầu task xem cần tạo tài nguyên ở Namespace nào. Nếu đề bài yêu cầu tạo trong namespace `finance` mà bạn tạo ở `default`, hệ thống chấm điểm tự động sẽ đánh trượt câu đó.
   - Mẹo: Chuyển namespace mặc định cho task dài: `k config set-context --current --namespace=finance`.
3. **Ưu tiên lệnh Imperative thay vì viết YAML thủ công:**
   - Tạo Service, Deployment, Job, ConfigMap, Secret, ServiceAccount bằng `kubectl create ...` hoặc `kubectl expose ...`.
   - Chỉ dùng file YAML khi đề bài yêu cầu các tham số phức tạp mà CLI không hỗ trợ (như volume mounts, affinity, securityContext).
4. **Chiến lược quản lý thời gian:**
   - Có khoảng **16 câu trong 120 phút** → trung bình **7 phút/câu**.
   - Các câu dễ (tạo Pod, expose Service, scale deployment, tạo RoleBinding) giải quyết trong **2–3 phút**.
   - Dành thời gian tiết kiệm được cho các câu khó (Upgrade cluster, Restore etcd, Debug node NotReady - tốn ~10-12 phút).
   - Câu nào đọc đề thấy mơ hồ hoặc debug quá 8 phút chưa ra → **Flag** lại và chuyển ngay sang câu tiếp theo.
5. **Kiểm tra kết quả trước khi sang câu mới:**
   - Luôn chạy `k get <resource>` hoặc `curl` để chứng minh giải pháp của mình đang thực sự hoạt động.

---

## 11. CHECKLIST TOÀN DIỆN

> Hãy tick từng mục khi bạn **đã hiểu bản chất lý thuyết + tự tay gõ lệnh thành thạo trên terminal**.

### 📋 A. Chuẩn bị & Thiết lập môi trường
- [ ] Đăng ký voucher thi CKA tại The Linux Foundation (tận dụng mã giảm giá nếu có).
- [ ] Setup cluster thực hành local (Kind / Minikube multi-node) trên máy tính cá nhân.
- [ ] Nắm vững cách cấu hình `.bashrc` và `.vimrc` phục vụ việc viết YAML siêu tốc.
- [ ] Thuộc lòng các bookmark hữu ích trên `kubernetes.io/docs` để tra cứu nhanh.

### 🏗️ B. Kiến trúc & Cấu hình Cluster (25%)
- [ ] Giải thích luồng tương tác giữa các thành phần Control Plane và Worker Node.
- [ ] Khởi tạo cụm mới bằng `kubeadm init` và join node bằng `kubeadm join`.
- [ ] Thực hiện quy trình nâng cấp toàn diện Kubeadm Cluster từ bản v1.34 lên v1.35.
- [ ] Thực hiện backup etcd snapshot ra file `.db` sử dụng chứng chỉ PKI chính xác.
- [ ] Thực hiện restore etcd snapshot và khởi động lại control plane thành công.
- [ ] Tạo và quản lý Role, ClusterRole, RoleBinding, ClusterRoleBinding.
- [ ] Kiểm tra quyền người dùng thành thạo với lệnh `kubectl auth can-i`.
- [ ] Cấu hình file `kubeconfig`, quản lý contexts, users và clusters.

### 📦 C. Workloads & Scheduling (15%)
- [ ] Tạo Pod, Deployment, DaemonSet, StatefulSet, Job, CronJob bằng imperative CLI.
- [ ] Cấu hình Rolling Update: `maxSurge`, `maxUnavailable`, kiểm tra rollout status & rollback.
- [ ] Cấu hình Multi-container Pod (Sidecar pattern, Init Containers, K8s 1.28+ native sidecar).
- [ ] Sử dụng `nodeSelector` và `nodeAffinity` (required vs preferred).
- [ ] Cấu hình `podAntiAffinity` để phân tán Pod trên các Node khác nhau.
- [ ] Thiết lập `Taints` trên Node và `Tolerations` trên Pod.
- [ ] Tạo và quản lý Static Pod thông qua thư mục `/etc/kubernetes/manifests/`.
- [ ] Cấu hình Resource Requests, Limits, LimitRange và ResourceQuota.

### ⚙️ D. Configuration & Application Lifecycle
- [ ] Tạo ConfigMap từ file, literal, env-file và inject vào Pod (env, envFrom, volume).
- [ ] Tạo Secret (Opaque, TLS, docker-registry) và mount an toàn vào container.
- [ ] Cấu hình LivenessProbe, ReadinessProbe, StartupProbe (HTTP, TCP, Exec).
- [ ] Cấu hình `SecurityContext` (runAsUser, runAsNonRoot, capabilities, privileged).
- [ ] Áp dụng Pod Security Standards (PSS) và Pod Security Admission (PSA).

### 🌐 E. Services & Networking (20%)
- [ ] Phân biệt và tạo các loại Service: ClusterIP, NodePort, LoadBalancer, Headless.
- [ ] Kiểm tra phân giải tên miền nội bộ qua CoreDNS bằng utility pod.
- [ ] Viết Ingress resource định tuyến đa host/path và cấu hình TLS Secret termination.
- [ ] Viết NetworkPolicy giới hạn lưu lượng mạng: default-deny, ingress rules, egress rules.
- [ ] Nắm vững khái niệm Gateway API (GatewayClass, Gateway, HTTPRoute).

### 💾 F. Storage (10%)
- [ ] Khai báo PersistentVolume (PV) kiểu hostPath/local với dung lượng và accessMode chuẩn.
- [ ] Khai báo PersistentVolumeClaim (PVC) và gắn thành công vào Deployment/Pod.
- [ ] Cấu hình `StorageClass` hỗ trợ dynamic provisioning và `WaitForFirstConsumer`.
- [ ] Thực hiện mở rộng kích thước volume (Volume Expansion).

### 🔧 G. Troubleshooting Toàn Tập (30%)
- [ ] Sửa lỗi Node `NotReady` (do Kubelet chết, thiếu ổ đĩa, sai config runtime containerd).
- [ ] Đọc log hệ thống cấp thấp bằng `journalctl -u kubelet -e` và `crictl logs`.
- [ ] Khắc phục Control Plane crash (sai tham số trong static pod manifest, hết hạn cert).
- [ ] Khắc phục Pod lỗi: `CrashLoopBackOff`, `ImagePullBackOff`, `Pending`, `OOMKilled`.
- [ ] Khắc phục lỗi Network/DNS: CoreDNS pod pending, Service selector không khớp label Pod.

### 🏁 H. Luyện thi thực chiến & Đăng ký thi
- [ ] Hoàn thành toàn bộ bài tập lab trong khóa học KodeKloud CKA.
- [ ] Kích hoạt lượt thi thử Killer.sh Session 1: Thi bấm giờ 120 phút, phân tích chi tiết mọi task sai.
- [ ] Ôn tập lại các điểm yếu, cày nát các kịch bản Troubleshooting.
- [ ] Kích hoạt Killer.sh Session 2: Đạt điểm **≥ 85/100**.
- [ ] Kiểm tra phòng thi, máy tính (webcam, mic, không gian yên tĩnh không có màn hình phụ).
- [ ] Tự tin bước vào phòng thi chính thức và lấy chứng chỉ CKA!

---

## 📌 Tóm tắt 1 dòng để nhớ

> **Bản chất của CKA là tốc độ thực hành và kỹ năng gỡ lỗi.** Hãy dùng **Imperative command để tạo YAML trong 5 giây**, thuộc lòng **cổng mạng & cú pháp etcdctl/kubeadm**, và luôn nhớ **đổi context + kiểm tra trạng thái hoạt động trước khi chuyển task**.
