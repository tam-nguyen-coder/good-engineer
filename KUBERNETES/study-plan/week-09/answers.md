# ✅ Answers & Explanations — Tuần 9: Cluster Maintenance & etcd

> Mở file này sau khi đã hoàn thành 15 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 9](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-B` · `2-A` · `3-B` · `4-A` · `5-B` · `6-B` · `7-B` · `8-A` · `9-A` · `10-B` · `11-A` · `12-B` · `13-A` · `14-A` · `15-C`

---

### Question 1 — Đáp án: **B**
- **Vì sao đúng:** `etcdctl` mặc định ở một số bản cũ có thể trỏ về API v2. Để thao tác với cơ sở dữ liệu Kubernetes hiện đại (etcd v3), bắt buộc phải export biến môi trường: **`export ETCDCTL_API=3`**.
- 🧠 **Mẹo ghi nhớ:** Luôn gõ **`ETCDCTL_API=3`** trước mọi câu lệnh etcdctl.

---

### Question 2 — Đáp án: **A**
- **Vì sao đúng:** Lệnh `etcdctl snapshot restore` yêu cầu một thư mục trống hoặc chưa tồn tại. Nếu bạn trỏ trực tiếp vào thư mục data đang chạy `/var/lib/etcd`, lệnh sẽ từ chối thực hiện để tránh làm hỏng database. Thao tác chuẩn: Khôi phục vào một thư mục mới (ví dụ `/var/lib/etcd-restored`) rồi sửa static pod manifest trỏ sang thư mục mới đó.
- 🧠 **Mẹo ghi nhớ:** Restore etcd **bắt buộc dùng `--data-dir` mới**!

---

### Question 3 — Đáp án: **B**
- **Vì sao đúng:** Các Pod có gắn volume kiểu `emptyDir` sẽ bị mất dữ liệu khi bị xoá khỏi node. Do đó, lệnh `kubectl drain` mặc định sẽ dừng lại để bảo vệ bạn khỏi mất dữ liệu vô ý. Thêm cờ **`--delete-emptydir-data`** để xác nhận đồng ý xoá dữ liệu tạm đó và tiếp tục drain.
- 🧠 **Mẹo ghi nhớ:** Drain dính emptyDir -> Thêm **`--delete-emptydir-data`**.

---

### Question 4 — Đáp án: **A**
- **Vì sao đúng:** Các Pod thuộc `DaemonSet` được gắn chặt vào từng node. Nếu drain đuổi nó đi thì nó cũng không thể chạy ở node khác. Do đó lệnh `kubectl drain` bắt buộc phải có cờ **`--ignore-daemonsets`** để bỏ qua và để nguyên DaemonSet pods tiếp tục chạy.
- 🧠 **Mẹo ghi nhớ:** Drain node luôn kèm **`--ignore-daemonsets`**.

---

### Question 5 — Đáp án: **B**
- **Vì sao đúng:** Quy trình nâng cấp Control Plane chuẩn bằng kubeadm:
  1. Drain node controlplane.
  2. Nâng cấp binary `kubeadm`.
  3. Chạy `kubeadm upgrade apply v1.31.0` để nâng cấp cấu hình cluster.
  4. Nâng cấp binary `kubelet` và `kubectl`.
  5. Restart service `kubelet`.
  6. Uncordon node.
- 🧠 **Mẹo ghi nhớ:** Quy trình CP: Drain -> Upgrade kubeadm -> Apply -> Upgrade kubelet/kubectl -> Restart -> Uncordon.

---

### Question 6 — Đáp án: **B**
- **Vì sao đúng:** Khác với Control Plane đầu tiên (dùng `kubeadm upgrade apply`), tất cả các Worker Nodes (và các secondary CP nodes) đều sử dụng lệnh **`kubeadm upgrade node`** để cập nhật cấu hình local.
- 🧠 **Mẹo ghi nhớ:** Nâng cấp Worker Node dùng **`kubeadm upgrade node`**.

---

### Question 7 — Đáp án: **B**
- **Vì sao đúng:** Theo chính sách Kubernetes Version Skew Policy, Kubelet trên Worker Node có thể chạy phiên bản cũ hơn API Server tối đa 2 minor versions (và lên tới 3 minor versions từ K8s v1.28 trở đi). Tuy nhiên, Kubelet **KHÔNG BAO GIỜ được phép có phiên bản cao hơn** API Server.
- 🧠 **Mẹo ghi nhớ:** Kubelet có thể thấp hơn API Server, nhưng **không bao giờ được cao hơn**.

---

### Question 8 — Đáp án: **A**
- **Vì sao đúng:**
  - `kubectl cordon`: Chỉ đổi trạng thái node sang `SchedulingDisabled`, chặn Pod mới, để nguyên Pod cũ.
  - `kubectl drain`: Vừa cordon, vừa thực hiện trục xuất (evict) toàn bộ các Pod đang chạy sang các node khác để sẵn sàng tắt máy.
- 🧠 **Mẹo ghi nhớ:** Cordon = Chặn vào; Drain = Chặn vào + Đuổi người đang ở ra.

---

### Question 9 — Đáp án: **A**
- **Vì sao đúng:** Chuẩn của `kubeadm` lưu trữ chứng chỉ etcd tại thư mục riêng biệt:
  - CA: `/etc/kubernetes/pki/etcd/ca.crt`
  - Cert: `/etc/kubernetes/pki/etcd/server.crt`
  - Key: `/etc/kubernetes/pki/etcd/server.key`
- 🧠 **Mẹo ghi nhớ:** Chứng chỉ etcd nằm tại **`/etc/kubernetes/pki/etcd/`**.

---

### Question 10 — Đáp án: **B**
- **Vì sao đúng:** Kubelet có tính năng File Watcher đối với thư mục manifest địa phương (`/etc/kubernetes/manifests/`). Khi bạn chỉnh sửa bất kỳ file nào trong thư mục này (như `etcd.yaml`), Kubelet tự động phát hiện mã băm (hash) của file thay đổi và tự động restart Pod tương ứng trong vòng vài giây mà không cần can thiệp thủ công.
- 🧠 **Mẹo ghi nhớ:** Sửa static pod YAML -> Kubelet **tự động restart pod**.

---

### Question 11 — Đáp án: **A**
- **Vì sao đúng:** Để đảm bảo tính ổn định của hạ tầng, các gói K8s trên Ubuntu luôn được đặt ở trạng thái `hold` bằng lệnh `apt-mark hold`. Khi cần nâng cấp, ta phải `unhold` để trình quản lý APT cho phép cài đặt phiên bản mới.
- 🧠 **Mẹo ghi nhớ:** Nâng cấp Ubuntu K8s: `apt-mark unhold ...` trước khi `apt install`.

---

### Question 12 — Đáp án: **B**
- **Vì sao đúng:** Lệnh `etcdctl --write-out=table snapshot status <file.db>` in ra bảng chi tiết chứa thông tin Revision, Total Keys, và Total Size của file backup, chứng minh snapshot không bị corrupt.
- 🧠 **Mẹo ghi nhớ:** Xem status snapshot: `etcdctl --write-out=table snapshot status ...`.

---

### Question 13 — Đáp án: **A**
- **Vì sao đúng:** Lệnh `kubeadm certs check-expiration` quét toàn bộ thư mục `/etc/kubernetes/pki` và hiển thị bảng hạn dùng còn lại của tất cả các chứng chỉ (apiserver, etcd, front-proxy, scheduler, controller-manager).
- 🧠 **Mẹo ghi nhớ:** Kiểm tra hạn cert: **`kubeadm certs check-expiration`**.

---

### Question 14 — Đáp án: **A**
- **Vì sao đúng:** Lệnh `kubeadm certs renew all` gia hạn tất cả các chứng chỉ nội bộ thêm 1 năm trong vòng 1 giây duy nhất.
- 🧠 **Mẹo ghi nhớ:** Gia hạn toàn bộ chứng chỉ: **`kubeadm certs renew all`**.

---

### Question 15 — Đáp án: **C**
- **Vì sao đúng:** Lệnh `kubectl uncordon <node-name>` gỡ bỏ trạng thái `SchedulingDisabled`, đưa Node trở lại trạng thái `Ready` để tiếp tục nhận các Pod mới từ Kube-scheduler.
- 🧠 **Mẹo ghi nhớ:** Bảo trì xong mở cửa lại cho Node: **`kubectl uncordon`**.
