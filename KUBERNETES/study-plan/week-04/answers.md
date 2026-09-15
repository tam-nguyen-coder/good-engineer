# ✅ Answers & Explanations — Tuần 4: ConfigMaps, Secrets & Security

> Mở file này sau khi đã hoàn thành 15 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 4](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-C` · `2-C` · `3-B` · `4-B` · `5-B` · `6-A` · `7-B` · `8-C` · `9-A` · `10-C` · `11-B` · `12-C` · `13-C` · `14-B` · `15-A`

---

### Question 1 — Đáp án: **C**
- **Vì sao đúng:** `ReadinessProbe` chỉ dùng để xác định xem Pod có sẵn sàng nhận lưu lượng mạng hay không. Nếu failed, Kubelet KHÔNG restart container; K8s chỉ loại bỏ IP của Pod ra khỏi danh sách `Endpoints` của Service để ngừng forward traffic.
- 🧠 **Mẹo ghi nhớ:** Readiness Fail = **Ngắt traffic** (không restart).

---

### Question 2 — Đáp án: **C**
- **Vì sao đúng:** `LivenessProbe` dùng để kiểm tra sự sống còn của ứng dụng. Khi app bị deadlock hoặc treo vô thời hạn, probe này thất bại và Kubelet sẽ **restart container** để tự phục hồi.
- 🧠 **Mẹo ghi nhớ:** Liveness Fail = **Restart container**.

---

### Question 3 — Đáp án: **B**
- **Vì sao đúng:** `StartupProbe` sinh ra dành riêng cho ứng dụng khởi động chậm. Trong suốt thời gian StartupProbe đang chạy (chưa thành công), nó sẽ tạm thời "tắt tiếng" (vô hiệu hoá) cả Liveness và Readiness Probes, ngăn không cho Liveness probe kill oan container khi app đang load context.
- 🧠 **Mẹo ghi nhớ:** App khởi động chậm -> Bổ sung **`StartupProbe`**.

---

### Question 4 — Đáp án: **B**
- **Vì sao đúng:** Khi một ConfigMap được mount dưới dạng **Volume**, Kubelet có một chu kỳ đồng bộ (sync loop) ngầm định kỳ. Khi ConfigMap thay đổi trên etcd, Kubelet sẽ cập nhật nội dung các file trong thư mục mount mà không cần restart Pod. Ngược lại, nếu inject qua biến môi trường (`env`/`envFrom`), biến môi trường được nạp lúc process khởi động nên bắt buộc phải restart Pod mới nhận giá trị mới.
- 🧠 **Mẹo ghi nhớ:** Muốn tự cập nhật không cần restart -> Mount ConfigMap dạng **Volume**.

---

### Question 5 — Đáp án: **B**
- **Vì sao đúng:** `runAsNonRoot: true` yêu cầu Kubelet kiểm tra image trước khi start: nếu user mặc định của image là `UID 0` (root) và PodSpec không chỉ định `runAsUser` khác 0, Kubelet sẽ từ chối khởi động container.
- 🧠 **Mẹo ghi nhớ:** Cấm chạy root -> `runAsNonRoot: true`.

---

### Question 6 — Đáp án: **A**
- **Vì sao đúng:** Cú pháp chuẩn của Linux Capabilities trong K8s: `securityContext.capabilities.drop: ["ALL"]` để bỏ hết mọi quyền thừa, sau đó `add: ["NET_BIND_SERVICE"]` để chỉ mở quyền bind port < 1024.
- 🧠 **Mẹo ghi nhớ:** Least privilege kernel: `drop: ["ALL"]`, `add: ["..."]`.

---

### Question 7 — Đáp án: **B**
- **Vì sao đúng:** Pod Security Admission (PSA) trong K8s hiện đại hoàn toàn không dùng CRD phức tạp. Nó được kích hoạt cực kỳ đơn giản thông qua các nhãn trên Namespace, ví dụ: `pod-security.kubernetes.io/enforce: restricted`.
- 🧠 **Mẹo ghi nhớ:** PSA kích hoạt bằng **Labels trên Namespace**.

---

### Question 8 — Đáp án: **C**
- **Vì sao đúng:** PSA hỗ trợ 3 modes:
  - `enforce`: Chặn đứng (reject) request tạo Pod nếu vi phạm.
  - `warn`: Vẫn cho tạo Pod nhưng hiển thị cảnh báo cho user trên terminal.
  - `audit`: Vẫn cho tạo Pod nhưng âm thầm ghi log vi phạm vào Audit Log.
- 🧠 **Mẹo ghi nhớ:** Chặn hoàn toàn = **`enforce`**.

---

### Question 9 — Đáp án: **A**
- **Vì sao đúng:** Cú pháp tạo generic secret nhanh: `kubectl create secret generic <name> --from-literal=<key>=<value> -n <ns>`.
- 🧠 **Mẹo ghi nhớ:** Tạo secret: `kubectl create secret generic ... --from-literal=...`.

---

### Question 10 — Đáp án: **C**
- **Vì sao đúng:** Khi rootfs bị khoá chỉ đọc (`readOnlyRootFilesystem: true`), giải pháp chuẩn Cloud-native là mount volume tạm thời kiểu `emptyDir: {}` vào các thư mục ứng dụng cần ghi file (như `/tmp`, `/app/logs`). Hệ thống file gốc vẫn được bảo vệ, trong khi ứng dụng vẫn hoạt động bình thường.
- 🧠 **Mẹo ghi nhớ:** `readOnlyRootFilesystem` kết hợp `emptyDir` mount vào `/tmp`.

---

### Question 11 — Đáp án: **B**
- **Vì sao đúng:** Theo chuẩn của Kubernetes, bất kỳ mã HTTP nào từ **`200 đến 399`** (`200 <= code < 400`) đều được coi là chẩn đoán thành công (Success). Mã `>= 400` được tính là thất bại (Failure).
- 🧠 **Mẹo ghi nhớ:** HTTP probe thành công khi mã nằm trong khoảng **`[200, 399]`**.

---

### Question 12 — Đáp án: **C**
- **Vì sao đúng:** Mặc định trong Kubernetes, Secret **KHÔNG ĐƯỢC MÃ HOÁ BẢO MẬT** trong etcd mà chỉ được encode dạng Base64. Base64 là cơ chế encoding, không phải mã hoá (encryption). Bất kỳ ai có quyền `get secret` đều có thể decode ra plaintext.
- 🧠 **Mẹo ghi nhớ:** K8s Secret mặc định chỉ là **Base64 encoding** (chưa mã hoá ở etcd).

---

### Question 13 — Đáp án: **C**
- **Vì sao đúng:** Khi Kubelet nhận lệnh xoá Pod, nó sẽ thực thi `preStop` hook TRƯỚC TIÊN. Container vẫn tiếp tục chạy trong khi `preStop` đang thực hiện (ví dụ chạy script rút node khỏi load balancer nội bộ). Sau khi `preStop` hoàn thành, Kubelet mới gửi tín hiệu `SIGTERM`.
- 🧠 **Mẹo ghi nhớ:** `preStop` chạy **trước khi gửi SIGTERM**.

---

### Question 14 — Đáp án: **B**
- **Vì sao đúng:** Cú pháp `envFrom` cho phép nhập toàn bộ các cặp key-value từ một ConfigMap hoặc Secret thành các biến môi trường cùng tên trong container trong 1 dòng cấu hình duy nhất.
- 🧠 **Mẹo ghi nhớ:** Nhập hàng loạt biến -> Dùng **`envFrom`**.

---

### Question 15 — Đáp án: **A**
- **Vì sao đúng:** `allowPrivilegeEscalation: false` can thiệp vào tầng kernel Linux, bật cờ `no_new_privs`. Điều này ngăn chặn triệt để việc một tiến trình leo thang đặc quyền thông qua các binary có cờ `setuid` hoặc `setgid` (như `sudo`, `su`, `passwd`).
- 🧠 **Mẹo ghi nhớ:** `allowPrivilegeEscalation: false` = Chặn leo thang đặc quyền qua setuid/setgid.
