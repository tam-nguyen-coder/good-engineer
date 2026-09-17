# ✅ Nhật ký Validate kiến thức & Cơ chế "CHẮC CHẮN ĐẬU" — Kubernetes CKA/CKAD

> **Ngày rà soát:** 2026-09-15 · **Cập nhật curriculum:** 2026-09-17 · **Phiên bản neo:** Kubernetes **v1.35.x** (phiên bản môi trường thi CKA hiện hành của CNCF / The Linux Foundation).
> **Tiêu chuẩn:** Đối chiếu 100% Task Statements từ **CNCF CKA Curriculum**, các kịch bản thực tế trong **Killer.sh Exam Simulator**, và kinh nghiệm xử lý lỗi phòng thi của các kỹ sư đạt điểm số ≥ 90%.
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

| STT | Domain CNCF | Tỉ trọng | Yêu cầu cốt lõi (Syllabus) | Trạng thái phủ trong Plan |
|---|---|---|---|---|
| **1** | **Troubleshooting** | **30%** | - Gỡ lỗi cụm và các node (Kubelet, containerd, disk, memory)<br>- Gỡ lỗi các thành phần Control Plane (apiserver, etcd, scheduler, controller-manager)<br>- Gỡ lỗi ứng dụng (CrashLoop, OOMKilled 137, Init fail)<br>- Gỡ lỗi network, CoreDNS và service routing<br>- Xem log cấp thấp bằng `journalctl` và `crictl` | ✅ Phủ 100% tại **Tuần 1, 5, 9, 10** |
| **2** | **Cluster Architecture, Installation & Configuration** | **25%** | - Phân quyền RBAC (Role, ClusterRole, RoleBinding, ClusterRoleBinding)<br>- Cài đặt và nâng cấp cụm bằng `kubeadm`<br>- Quản lý cấu hình Kubeconfig và context switching<br>- Backup và Restore database `etcd`<br>- Tạo chứng chỉ người dùng qua K8s CSR API | ✅ Phủ 100% tại **Tuần 1, 8, 9** |
| **3** | **Services & Networking** | **20%** | - Cấu hình ClusterIP, NodePort (30000-32767), LoadBalancer, Headless<br>- Định tuyến Ingress L7 và cấu hình TLS Secret<br>- Kubernetes Gateway API (GatewayClass, Gateway, HTTPRoute)<br>- Phân giải tên miền CoreDNS FQDN<br>- Viết tường lửa NetworkPolicy (Ingress, Egress, AND/OR logic) | ✅ Phủ 100% tại **Tuần 5, 6** |
| **4** | **Workloads & Scheduling** | **15%** | - Quản lý Deployments, Rolling Updates, Rollouts, Rollbacks<br>- Cấu hình DaemonSet, StatefulSet, Job, CronJob (`concurrencyPolicy`)<br>- Lập lịch nâng cao: NodeAffinity, PodAntiAffinity (`topologyKey`)<br>- Cô lập hạ tầng bằng Taints và Tolerations<br>- Cấu hình Resource Requests, Limits, LimitRange, Quotas, QoS Classes | ✅ Phủ 100% tại **Tuần 2, 3, 4** |
| **5** | **Storage** | **10%** | - Khai báo PersistentVolume (PV) và PersistentVolumeClaim (PVC)<br>- Quản lý StorageClass, CSI drivers, Dynamic Provisioning<br>- Cơ chế `volumeBindingMode: WaitForFirstConsumer`<br>- Các chế độ `accessModes` (RWO, ROX, RWX, RWOP v1.29+)<br>- Mở rộng dung lượng volume trực tiếp (Volume Expansion) | ✅ Phủ 100% tại **Tuần 7** |

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

> 🏁 **KẾT LUẬN: BỘ TÀI LIỆU NÀY ĐÃ ĐƯỢC CHUẨN HOÁ 100%. NẾU BẠN HOÀN THÀNH TẤT CẢ CÁC BÀI LAB VÀ ĐẠT ĐIỂM KILLER.SH THEO ĐÚNG HƯỚNG DẪN, BẠN CHẮC CHẮN ĐẬU CKA!**
