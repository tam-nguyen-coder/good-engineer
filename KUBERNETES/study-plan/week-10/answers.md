# ✅ Answers & Explanations — Tuần 10: Troubleshooting Toàn Tập (30% CKA)

> Mở file này sau khi đã hoàn thành 15 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 10](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-A` · `2-B` · `3-A` · `4-B` · `5-B` · `6-A` · `7-A` · `8-B` · `9-A` · `10-A` · `11-B` · `12-A` · `13-A` · `14-A` · `15-B`

---

### Question 1 — Đáp án: **A**
- **Vì sao đúng:** `journalctl -u kubelet -e --no-pager` là lệnh số 1 để xem log của Systemd service trên Linux. Cờ `-u kubelet` lọc theo unit kubelet, `-e` nhảy ngay tới dòng cuối cùng (nơi ghi nhận nguyên nhân crash), và `--no-pager` xuất thẳng ra terminal giúp đọc nhanh.
- 🧠 **Mẹo ghi nhớ:** Kubelet chết -> Xem log ngay bằng **`journalctl -u kubelet -e --no-pager`**.

---

### Question 2 — Đáp án: **B**
- **Vì sao đúng:** Kể từ bản v1.24+, `dockershim` đã bị loại bỏ hoàn toàn khỏi mã nguồn Kubernetes. Kubelet hiện đại bắt buộc phải giao tiếp qua CRI socket chuẩn của Containerd: `unix:///run/containerd/containerd.sock`.
- 🧠 **Mẹo ghi nhớ:** Socket containerd chuẩn: **`unix:///run/containerd/containerd.sock`**.

---

### Question 3 — Đáp án: **A**
- **Vì sao đúng:** Khi API Server bị tắt hoặc crash, toàn bộ lệnh `kubectl` sẽ mất tác dụng vì không còn máy chủ tiếp nhận HTTP request. Do đó, kỹ sư bắt buộc phải sử dụng công cụ cấp thấp của Container Runtime là **`crictl`**: dùng `crictl ps -a` để tìm container apiserver bị `Exited` và `crictl logs <id>` để đọc log báo lỗi.
- 🧠 **Mẹo ghi nhớ:** API Server chết -> Dùng **`crictl`** để xem container và log.

---

### Question 4 — Đáp án: **B**
- **Vì sao đúng:** Khi container bị CrashLoop, container hiện tại vừa mới khởi động nên log thường bị trống hoặc chưa kịp ghi. Cờ **`--previous`** (hoặc `-p`) yêu cầu Kubelet lấy lại toàn bộ log của phiên bản container đã bị crash trước đó, giúp xác định ngay lập tức dòng code hoặc lỗi gây chết ứng dụng.
- 🧠 **Mẹo ghi nhớ:** Xem log container vừa crash: **`kubectl logs <name> --previous`**.

---

### Question 5 — Đáp án: **B**
- **Vì sao đúng:** Mã Exit Code 137 (`128 + 9 SIGKILL`) đi kèm lý do `OOMKilled` chứng minh container bị Linux kernel tiêu diệt vì đòi cấp phát RAM vượt quá ngưỡng trần `resources.limits.memory`. Giải pháp duy nhất là nâng mức limit này lên hoặc tối ưu code để không bị memory leak.
- 🧠 **Mẹo ghi nhớ:** OOMKilled (Exit 137) = **Tăng memory limit** trong PodSpec.

---

### Question 6 — Đáp án: **A**
- **Vì sao đúng:** Private registry yêu cầu xác thực. K8s cung cấp loại Secret đặc thù: `kubernetes.io/dockerconfigjson` (tạo bằng `kubectl create secret docker-registry ...`). Secret này sau đó được gắn vào trường `spec.imagePullSecrets` của Pod để Kubelet có quyền kéo image.
- 🧠 **Mẹo ghi nhớ:** ImagePullBackOff do Private Repo -> Cần **`imagePullSecrets`**.

---

### Question 7 — Đáp án: **A**
- **Vì sao đúng:** Khi Pod bị treo ở trạng thái Terminating (thường do volume không thể unmount an toàn), lệnh `kubectl delete pod <name> --force --grace-period=0` sẽ bỏ qua thời gian ân hạn 30s và lập tức gỡ bỏ đối tượng Pod khỏi etcd.
- 🧠 **Mẹo ghi nhớ:** Xoá cưỡng bức tức thì: **`--force --grace-period=0`** (đã gán vào alias `$now`).

---

### Question 8 — Đáp án: **B**
- **Vì sao đúng:** Kubelet đọc cấu hình từ file `/var/lib/kubelet/config.yaml`. Thuộc tính **`staticPodPath`** (mặc định trỏ vào `/etc/kubernetes/manifests`) quy định thư mục mà Kubelet quét định kỳ để khởi chạy các Static Pods.
- 🧠 **Mẹo ghi nhớ:** Thư mục Static Pod trong kubelet config: **`staticPodPath`**.

---

### Question 9 — Đáp án: **A**
- **Vì sao đúng:** Khi Node bị `DiskPressure = True` (dung lượng ổ đĩa vượt quá ngưỡng eviction threshold, thường là >85%), Kube-scheduler sẽ ngừng xếp Pod mới lên node này (Taint `node.kubernetes.io/disk-pressure:NoSchedule` tự động được kích hoạt), và Kubelet bắt đầu dọn dẹp các dead containers và unused images.
- 🧠 **Mẹo ghi nhớ:** `DiskPressure` = Ngừng nhận Pod mới + Kubelet dọn dẹp đĩa.

---

### Question 10 — Đáp án: **A**
- **Vì sao đúng:** CoreDNS yêu cầu mạng nội bộ (Pod Network) hoạt động để được cấp phát IP. Nếu cụm vừa cài đặt mà chưa có CNI plugin (như Calico hay Flannel), các Pod của CoreDNS sẽ bị kẹt vô thời hạn ở trạng thái `Pending` do không có IP mạng.
- 🧠 **Mẹo ghi nhớ:** Cụm mới cài đặt mà CoreDNS Pending -> **Chưa cài đặt CNI Network Plugin**.

---

### Question 11 — Đáp án: **B**
- **Vì sao đúng:** Endpoints hiển thị `<none>` là dấu hiệu 100% cho thấy Label Selector của Service không khớp với Labels của bất kỳ Pod nào. Chỉ cần sửa lại selector cho khớp chính xác từng ký tự là Service sẽ kết nối được ngay lập tức.
- 🧠 **Mẹo ghi nhớ:** Endpoints `<none>` = So khớp và sửa lại **Label Selector**.

---

### Question 12 — Đáp án: **A**
- **Vì sao đúng:** Lỗi `0/2 nodes are available: 2 Insufficient cpu` từ Scheduler chỉ ra rằng tổng CPU requests của các Pod đã vượt quá năng lực cấp phát (allocatable CPU) của các node. Cần giảm CPU request của Pod hoặc scale thêm node.
- 🧠 **Mẹo ghi nhớ:** `Insufficient cpu/memory` = Giảm `resources.requests` hoặc bổ sung node.

---

### Question 13 — Đáp án: **A**
- **Vì sao đúng:** `crictl` cần file cấu hình `/etc/crictl.yaml` để biết socket của Container Runtime nằm ở đâu. Nội dung cần khai báo: `runtime-endpoint: unix:///run/containerd/containerd.sock`.
- 🧠 **Mẹo ghi nhớ:** Cấu hình crictl: File **`/etc/crictl.yaml`**.

---

### Question 14 — Đáp án: **A**
- **Vì sao đúng:** Kubernetes mặc định yêu cầu tắt hoàn toàn bộ nhớ hoán đổi (swap) trên hệ điều hành Linux để đảm bảo tính toán tài nguyên CPU/RAM chính xác. Lệnh `swapoff -a` tắt swap ngay lập tức trên hệ thống đang chạy.
- 🧠 **Mẹo ghi nhớ:** Kubelet bắt buộc tắt swap: **`swapoff -a`**.

---

### Question 15 — Đáp án: **B**
- **Vì sao đúng:** Quản lý thời gian là yếu tố quyết định đỗ/trượt CKA (120 phút cho 16-17 câu). Dành quá 8 phút cho một câu hỏi Troubleshooting hóc búa sẽ làm bạn không đủ thời gian làm các câu dễ ở phía sau. **Chiến lược chuẩn: Bấm Flag, ghi lại điểm, chuyển ngay sang câu tiếp theo và quay lại sau cùng.**
- 🧠 **Mẹo ghi nhớ:** Kẹt quá 7-8 phút -> **BẤM FLAG VÀ NEXT NGAY**. Không sa lầy!
