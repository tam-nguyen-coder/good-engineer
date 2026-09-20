# ✅ Nhật ký Validate kiến thức & Cơ chế "CHẮC CHẮN ĐẬU" — Kubernetes CKA/CKAD

> **Ngày rà soát:** 2026-09-15 · **Cập nhật curriculum:** 2026-09-17 · **Phiên bản neo:** Kubernetes **v1.35.x** (phiên bản môi trường thi CKA hiện hành của CNCF / The Linux Foundation).
> **Tiêu chuẩn:** Đối chiếu từng dòng Task Statement của **CNCF CKA Curriculum bản 18/02/2025**, các kịch bản thực tế trong **Killer.sh Exam Simulator**, và kinh nghiệm xử lý lỗi phòng thi của các kỹ sư đạt điểm số ≥ 90%.
> **Mục tiêu tối thượng:** Đảm bảo **KHÔNG BỊ LỦNG BẤT KỲ LỖ HỔNG KIẾN THỨC NÀO**, triệt tiêu toàn bộ rủi ro mất điểm ngớ ngẩn, và đảm bảo kết quả **CHẮC CHẮN ĐẬU (≥ 85%)**.

---

## 📑 Mục lục rà soát

1. [Bảng đối chiếu 100% Domain CKA Curriculum (Zero-gap Audit)](#1-bảng-đối-chiếu-100-domain-cka-curriculum)
2. [Top 12 Cạm bẫy gây TRƯỢT CKA nhiều nhất & Thuốc giải độc](#2-top-12-cạm-bẫy-gây-trượt-cka-nhiều-nhất)
3. [Quy trình kiểm tra tính hợp lệ bài làm (Validation Checklist từng câu)](#3-quy-trình-kiểm-tra-tính-hợp-lệ-bài-làm)
4. [Bộ lệnh "Cứu mạng khẩn cấp" trong phòng thi](#4-bộ-lệnh-cứu-mạng-khẩn-cấp-trong-phòng-thi)
5. [Chiến lược chinh phục Killer.sh & Thiết lập biên an toàn điểm số](#5-chiến-lược-chinh-phục-killersh)

---

## 1. Bảng đối chiếu 100% Domain CKA Curriculum

> 📌 **Nguồn đối chiếu:** *CKA Curriculum* của The Linux Foundation, bản có hiệu lực từ **18/02/2025** (áp dụng cho môi trường thi **v1.35**).
> Bản curriculum này bổ sung 5 competency so với syllabus cũ: **Helm & Kustomize**, **HA control plane**, **extension interfaces (CNI/CSI/CRI)**, **CRDs & Operators**, và **workload autoscaling**. Bảng dưới đây đối chiếu **từng dòng** của syllabus chính thức, không gộp.

### 1️⃣ Cluster Architecture, Installation & Configuration — 25%

| Competency chính thức (CNCF) | Phủ tại | Trạng thái |
|---|---|---|
| Manage role based access control (RBAC) | Tuần 8 | ✅ |
| Prepare underlying infrastructure for installing a Kubernetes cluster | Tuần 1 (Kind multi-node), Tuần 9 (kubeadm init/join, cgroup driver, containerd) | ✅ |
| Create and manage Kubernetes clusters using kubeadm | Tuần 9 | ✅ |
| Manage the lifecycle of Kubernetes clusters | Tuần 9 (upgrade N→N+1, drain/uncordon, cert renewal, etcd DR) | ✅ |
| **Implement and configure a highly-available control plane** | **Tuần 9 — Buổi C+** (stacked vs external etcd, quorum `(N/2)+1`, `--control-plane-endpoint`, `--upload-certs`, LB, leader election) · [Lab 9.3](week-09/labs.md) | 🆕 ✅ |
| **Use Helm and Kustomize to install cluster components** | **Tuần 4 — Buổi C+** · [Lab 4.4 Kustomize](week-04/labs.md) · [Lab 4.5 Helm](week-04/labs.md) · Q16–Q20 | 🆕 ✅ |
| **Understand extension interfaces (CNI, CSI, CRI, etc.)** | **Tuần 1 — Buổi C+** (ai gọi interface nào + triệu chứng khi hỏng) · Q21–Q23 | 🆕 ✅ |
| **Understand CRDs, install and configure operators** | **Tuần 9 — Buổi C++** · [Lab 9.4](week-09/labs.md) · Q19–Q21 | 🆕 ✅ |

### 2️⃣ Workloads & Scheduling — 15%

| Competency chính thức (CNCF) | Phủ tại | Trạng thái |
|---|---|---|
| Understand application deployments and how to perform rolling update and rollbacks | Tuần 2 | ✅ |
| Use ConfigMaps and Secrets to configure applications | Tuần 4 | ✅ |
| **Configure workload autoscaling** | **Tuần 3 — Buổi C+** (HPA `autoscaling/v2`, Utilization vs AverageValue, `behavior`, HPA/VPA/CA) · [Lab 3.4](week-03/labs.md) · Q16, Q17, Q19 | 🆕 ✅ |
| Understand the primitives used to create robust, self-healing, application deployments | Tuần 2 (ReplicaSet, DaemonSet, StatefulSet), Tuần 4 (probes) | ✅ |
| Configure Pod admission and scheduling (limits, node affinity, etc.) | Tuần 3 (affinity, taints, QoS, quotas), Tuần 4 (PSA) | ✅ |

### 3️⃣ Services & Networking — 20%

| Competency chính thức (CNCF) | Phủ tại | Trạng thái |
|---|---|---|
| Understand connectivity between Pods | Tuần 5, Tuần 1 (CNI cấp IP, IP-per-Pod) | ✅ |
| Define and enforce Network Policies | Tuần 6 (kèm cảnh báo NetworkPolicy chỉ hiệu lực khi CNI hỗ trợ) | ✅ |
| Use ClusterIP, NodePort, LoadBalancer service types and endpoints | Tuần 5 | ✅ |
| Use the Gateway API to manage Ingress traffic | Tuần 6 · Mock 03 Task 5 | ✅ |
| Know how to use Ingress controllers and Ingress resources | Tuần 6 | ✅ |
| Understand and use CoreDNS | Tuần 5 | ✅ |

### 4️⃣ Storage — 10%

| Competency chính thức (CNCF) | Phủ tại | Trạng thái |
|---|---|---|
| Implement storage classes and dynamic volume provisioning | Tuần 7 | ✅ |
| Configure volume types, access modes and reclaim policies | Tuần 7 (RWO/ROX/RWX/RWOP, Retain vs Delete) | ✅ |
| Manage persistent volumes and persistent volume claims | Tuần 7 · Tuần 1 (chẩn đoán PVC Pending qua CSI driver) | ✅ |

### 5️⃣ Troubleshooting — 30%

| Competency chính thức (CNCF) | Phủ tại | Trạng thái |
|---|---|---|
| Troubleshoot clusters and nodes | Tuần 9, Tuần 10 · Tuần 1 (phân biệt hỏng CRI/CNI/CSI) | ✅ |
| Troubleshoot cluster components | Tuần 9, Tuần 10 (static pod manifests, `crictl`) | ✅ |
| **Monitor cluster and application resource usage** | **Tuần 3 — Buổi C+** (Metrics Server, `kubectl top`, phân biệt usage vs allocated) · Q18 | 🆕 ✅ |
| Manage and evaluate container output streams | Tuần 10 (`kubectl logs -c --previous`, `crictl logs`, `journalctl -u kubelet`) | ✅ |
| Troubleshoot services and networking | Tuần 5, Tuần 6, Tuần 10 | ✅ |

> ⚠️ **Cảnh báo về tính thời sự:** bảng trên đúng tại thời điểm **2026-09-17**. CNCF cập nhật môi trường thi **theo quý** và có thể chỉnh curriculum bất cứ lúc nào.
> **Trước khi đặt lịch thi, hãy tự đối chiếu lại** với [trang CKA chính thức](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/) và trang *Important Instructions*. Lần rà soát này phát hiện plan đang bám theo syllabus cũ hơn curriculum thật **khoảng 18 tháng** — đừng để lặp lại.

### 📄 Tài liệu được phép mở trong phòng thi (đã cập nhật)

| Được phép | Ghi chú |
|---|---|
| `https://kubernetes.io/docs/` | Bao gồm cả ô **search nội bộ** của trang; **không** được mở kết quả trỏ ra ngoài |
| `https://kubernetes.io/blog/` | |
| `https://helm.sh/docs/` | 🆕 Thêm cùng đợt curriculum bổ sung Helm |
| `https://gateway-api.sigs.k8s.io/` | 🆕 Dành cho các task Gateway API |
| ❌ `https://github.com/kubernetes/` | **KHÔNG còn** trong danh sách cho phép — mở ra có thể bị proctor cảnh cáo |

---

## 2. Top 12 Cạm bẫy gây TRƯỢT CKA nhiều nhất

> ⚠️ Đây là 12 nguyên nhân trực tiếp khiến thí sinh trượt CKA dù đã học rất nhiều. Hãy đọc thuộc lòng cách khắc phục:

### ❌ Bẫy 1: Quên chuyển Context ở đầu mỗi câu hỏi
- **Hậu quả:** Làm đúng 100% các bước nhưng làm trên sai cluster context → **0 ĐIỂM NGAY LẬP TỨC**.
- **Thuốc giải:** Đề bài luôn để 1 dòng lệnh màu xanh lá ở đầu task (ví dụ: `kubectl config use-context k8s`). **QUY TẮC BẮT BUỘC: Đọc đề việc đầu tiên là copy và chạy lệnh đổi context này.**

### ❌ Bẫy 2: Nhầm lẫn Namespace
- **Hậu quả:** Đề yêu cầu tạo Service trong namespace `staging`, nhưng tạo nhầm ở `default`. Hệ thống chấm thi tự động (auto-grader) kiểm tra trong `staging` thấy rỗng → **0 điểm**.
- **Thuốc giải:** Luôn thêm cờ `-n <namespace>` trong mọi câu lệnh imperative HOẶC chuyển namespace làm việc tạm thời: `k config set-context --current --namespace=<ns>`.

### ❌ Bẫy 3: Phục hồi etcd đè trực tiếp lên thư mục data cũ
- **Hậu quả:** Chạy lệnh `etcdctl snapshot restore /tmp/snap.db --data-dir=/var/lib/etcd` khiến tiến trình etcd bị conflict file lock, API server sập hoàn toàn và không thể khởi động lại.
- **Thuốc giải:** Tham số `--data-dir` khi restore **BẮT BUỘC PHẢI TRỎ VÀO MỘT THƯ MỤC MỚI** (Ví dụ: `/var/lib/etcd-backup-restored`). Sau đó sửa file `/etc/kubernetes/manifests/etcd.yaml`, đổi đường dẫn `hostPath` của volume `etcd-data` trỏ sang thư mục mới đó.

### ❌ Bẫy 4: Lỗi NetworkPolicy vô tình chặn luôn cả CoreDNS (Port 53)
- **Hậu quả:** Cấu hình NetworkPolicy hạn chế `Egress`, nhưng quên không mở egress UDP/TCP port 53 tới CoreDNS. Kết quả: Pod không thể phân giải tên miền bất kỳ Service nào, ứng dụng tê liệt hoàn toàn.
- **Thuốc giải:** Khi viết NetworkPolicy có chặn Egress, LUÔN LUÔN thêm một rule cho phép ra cổng 53:
  ```yaml
  egress:
  - ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
  ```

### ❌ Bẫy 5: Nhầm lẫn giữa điều kiện AND và OR trong NetworkPolicy
- **Hậu quả:** Viết nhầm quy tắc khiến Pod bị lộ lọt mạng hoặc bị chặn oan.
- **Thuốc giải:**
  - **OR:** Hai dấu gạch đầu dòng `-` riêng biệt trong danh sách `from`.
  - **AND:** Chung một dấu gạch đầu dòng `-` cho cả `namespaceSelector` và `podSelector`.

### ❌ Bẫy 6: Nâng cấp Kubeadm nhảy cóc phiên bản
- **Hậu quả:** Đang ở v1.33 mà cố tình nâng thẳng lên v1.35 → Kubeadm báo lỗi incompatible version và cụm bị hỏng cluster state.
- **Thuốc giải:** Chỉ được phép nâng cấp tối đa 1 minor version tại một thời điểm (ví dụ: `1.34.x` lên `1.35.x`).

### ❌ Bẫy 7: Quên unhold gói phần mềm khi cài đặt APT trên Ubuntu
- **Hậu quả:** Chạy `apt-get install kubeadm=1.35.0` nhưng terminal báo `kubeadm set on hold`, không cài được bản mới.
- **Thuốc giải:** Phải chạy `apt-mark unhold kubeadm kubelet kubectl` trước khi cài, hoặc thêm cờ `--allow-change-held-packages`. Cài xong thì khoá lại: `apt-mark hold kubeadm kubelet kubectl`.

### ❌ Bẫy 8: Nhầm lẫn giữa `kubeadm upgrade apply` và `kubeadm upgrade node`
- **Hậu quả:** Chạy lệnh `kubeadm upgrade apply` trên Worker Node khiến lệnh bị lỗi và dừng nâng cấp.
- **Thuốc giải:**
  - **Control Plane Node đầu tiên:** Dùng `kubeadm upgrade apply v1.35.0`.
  - **Tất cả các Worker Node (và các CP node phụ):** Dùng `kubeadm upgrade node`.

### ❌ Bẫy 9: Sai chính tả đường dẫn trong Static Pod Manifest
- **Hậu quả:** Sửa file trong `/etc/kubernetes/manifests/` nhưng gõ sai indentation hoặc sai đường dẫn certificate. API server tắt thở, `kubectl` không kết nối được.
- **Thuốc giải:** Trước khi sửa bất kỳ file manifest nào trong `/etc/kubernetes/manifests/`, LUÔN LUÔN copy tạo 1 bản backup dự phòng:
  `cp /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/kube-apiserver.yaml.bak`.

### ❌ Bẫy 10: Tưởng rằng `docker` command vẫn dùng được trên Node
- **Hậu quả:** SSH vào node và gõ `docker ps`, nhận được thông báo `docker: command not found` hoặc danh sách rỗng, lúng túng mất 10 phút.
- **Thuốc giải:** Kubernetes hiện đại dùng `containerd`. Bắt buộc dùng lệnh **`crictl`**:
  `crictl ps`, `crictl pods`, `crictl logs <id>`, `crictl inspect <id>`.

### ❌ Bẫy 11: Chạy `kubectl drain` bị từ chối do Pod có volume `emptyDir` hoặc DaemonSet
- **Hậu quả:** Lệnh drain bị abort, node không được bảo trì.
- **Thuốc giải:** Luôn dùng đầy đủ 3 cờ hộ mệnh:
  `kubectl drain <node> --ignore-daemonsets --delete-emptydir-data --force`.

### ❌ Bẫy 12: Gõ tay YAML từ đầu dẫn đến sai thụt lề 2 spaces
- **Hậu quả:** Dành 15 phút chỉ để dò xem dòng 42 bị lệch 1 dấu cách ở đâu.
- **Thuốc giải:** 100% sinh YAML bằng lệnh `--dry-run=client -o yaml > file.yaml`. Bật `.vimrc` căn tab 2 spaces (`set ts=2 sw=2 et paste`).

---

## 3. Quy trình kiểm tra tính hợp lệ bài làm (Validation Checklist)

> ⚡ Trước khi gõ lệnh chuyển sang task tiếp theo, thực hiện kiểm tra 4 bước trong **20 giây**:

1. [ ] **Đúng Namespace:** `kubectl get <resource> -n <đúng_namespace_đề_yêu_cầu>`.
2. [ ] **Đúng Tên Đối Tượng:** Kiểm tra từng ký tự tên Pod/Service/PVC (ví dụ đề bảo `web-api-svc` thì không được đặt là `web-api`).
3. [ ] **Trạng thái sẵn sàng (Ready Status):**
   - Pod phải đạt `Running` và `1/1 Ready`.
   - Deployment phải đạt `Replicas Available`.
   - PVC phải đạt trạng thái `Bound`.
4. [ ] **Kiểm tra kết nối thực tế:**
   - Tạo Service? → `kubectl get ep <svc-name>` (đảm bảo cột ENDPOINTS có IP).
   - Expose Web? → `curl http://<ip>:<port>` xem có trả về HTTP 200 không.

---

## 4. Bộ lệnh "Cứu mạng khẩn cấp" trong phòng thi

```bash
# 1. Xem 20 dòng log lỗi cuối cùng của Kubelet
journalctl -u kubelet -e --no-pager -n 20

# 2. Xem log của container trước khi bị crash
kubectl logs <pod-name> --previous -n <namespace>

# 3. Lọc toàn bộ events lỗi (Warning) trong cụm
kubectl get events -A --field-selector type=Warning --sort-by=.metadata.creationTimestamp

# 4. Xoá Pod bị treo ngay lập tức không cần đợi 30 giây
kubectl delete pod <bad-pod> --force --grace-period=0

# 5. Xem toàn bộ IP và Node của Pods trên tất cả namespaces
kubectl get pods -o wide -A

# 6. Sắp xếp Pod theo lượng tiêu thụ RAM
kubectl top pods -A --sort-by=memory
```

---

## 5. Chiến lược chinh phục Killer.sh & Thiết lập biên an toàn điểm số

1. **Hiểu rõ tính chất của Killer.sh:**
   - Đề thi Killer.sh (2 sessions miễn phí kèm voucher CKA) được cố tình thiết kế **dài hơn và khó hơn đề thi thật ~30–40%** (nhiều kịch bản lắt léo, thời gian eo hẹp).
   - Nếu bạn làm lần 1 đạt 50–60 điểm: **Đó là chuyện hoàn toàn bình thường!**
2. **Quy trình tối ưu 2 Sessions:**
   - **Session 1 (Học hỏi & Đào sâu):** Làm bài thi nghiêm túc trong 120 phút. Sau khi hết giờ, cluster sẽ mở trong 36 giờ. Hãy đọc từng dòng giải thích của Killer.sh, ghi lại toàn bộ các câu lệnh hay và các bẫy bạn đã dính.
   - **Ôn tập 3–5 ngày:** Làm lại các bài lab trong `KUBERNETES/study-plan/` cho thuần thục các lỗ hổng phát hiện ở Session 1.
   - **Session 2 (Sát hạch chuẩn):** Kích hoạt session thứ 2 và làm lại. **MỤC TIÊU: ĐẠT ≥ 85 ĐIỂM.**
3. **Ngưỡng biên an toàn (Safety Margin):**
   - Điểm đỗ chính thức của CKA là **66/100**.
   - Bằng việc luyện tập đạt **≥ 85/100 trên Killer.sh**, bạn đã tạo ra một **biên an toàn cực lớn (+19%)**. Biên độ này thừa sức hấp thụ áp lực tâm lý phòng thi, giao diện trình duyệt PSI giật lag, hoặc 1–2 câu hỏi mới lạ trong đề thật.

> 🏁 **KẾT LUẬN:** Bộ tài liệu này đã được đối chiếu **từng dòng** với CKA Curriculum bản 18/02/2025 (môi trường thi v1.35). Hoàn thành toàn bộ lab + đạt ≥ 85 điểm Killer.sh ở session 2 sẽ cho bạn biên an toàn rất lớn so với ngưỡng đậu 66.
>
> 📌 **Một việc bạn vẫn phải tự làm:** kiểm tra lại curriculum và danh sách domain được phép tra cứu trên trang chính thức **ngay trước ngày thi**. CNCF cập nhật môi trường thi theo quý — không tài liệu tĩnh nào thay thế được bước kiểm tra 2 phút này.
