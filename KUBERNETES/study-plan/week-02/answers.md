# ✅ Answers & Explanations — Tuần 2: Workloads & Controllers

> Mở file này sau khi đã hoàn thành 15 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 2](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-A` · `2-B` · `3-C` · `4-B` · `5-C` · `6-B` · `7-B` · `8-C` · `9-B` · `10-B` · `11-C` · `12-A` · `13-B` · `14-B` · `15-B`

---

### Question 1 — Đáp án: **A**
- **Vì sao đúng:**
  - `maxSurge: 1`: Cho phép số Pod tối đa vượt ngưỡng replicas: `4 + 1 = 5 Pods`.
  - `maxUnavailable: 0`: Không cho phép bất kỳ Pod nào bị thiếu hụt so với số lượng mong muốn (4), nghĩa là luôn có tối thiểu `4 - 0 = 4 Pods` sẵn sàng.
  - K8s sẽ tạo 1 Pod mới trước, đợi nó `Running & Ready` rồi mới tắt 1 Pod cũ.
- 🧠 **Mẹo ghi nhớ:** `maxUnavailable: 0` = Zero Downtime tuyệt đối, luôn giữ đủ số lượng replicas ban đầu.

---

### Question 2 — Đáp án: **B**
- **Vì sao đúng:** Cú pháp hoàn tác bản rollout chuẩn của `kubectl` là `kubectl rollout undo deployment/<name> --to-revision=<number>`.
- 🧠 **Mẹo ghi nhớ:** Muốn undo về revision cụ thể: `k rollout undo deploy/<name> --to-revision=N`.

---

### Question 3 — Đáp án: **C**
- **Vì sao đúng:** `DaemonSet` sinh ra để giải quyết chính xác bài toán chạy đúng 1 bản sao của Pod trên mọi node (logging agents, monitoring, CNI pods). Khi node mới vào, DaemonSet tự xếp Pod lên; khi node bị xoá, Pod tự bị thu dọn.
- 🧠 **Mẹo ghi nhớ:** "1 Pod trên mỗi node" → Luôn chọn **`DaemonSet`**.

---

### Question 4 — Đáp án: **B**
- **Vì sao đúng:** `StatefulSet` duy trì danh tính cố định: tên Pod bắt đầu từ index `0` (`<name>-0`, `<name>-1`...). Việc tạo và huỷ diễn ra tuần tự nghiêm ngặt (tạo 0 xong mới tới 1; scale down thì xoá từ 2 về 1 rồi về 0).
- 🧠 **Mẹo ghi nhớ:** StatefulSet = Tên có số thứ tự từ 0, khởi tạo và tắt tuần tự.

---

### Question 5 — Đáp án: **C**
- **Vì sao đúng:** StatefulSet yêu cầu một **Headless Service** (`clusterIP: None`) đi kèm để CoreDNS trả về địa chỉ IP thực của từng Pod thành viên theo cú pháp `<pod-name>.<service-name>.<namespace>.svc.cluster.local`.
- 🧠 **Mẹo ghi nhớ:** StatefulSet luôn đi kèm với **Headless Service (`clusterIP: None`)**.

---

### Question 6 — Đáp án: **B**
- **Vì sao đúng:**
  - `concurrencyPolicy: Forbid`: Không cho phép Job mới chạy nếu Job cũ chưa kết thúc.
  - `Allow` (mặc định): Cho phép chạy song song đè lên nhau.
  - `Replace`: Huỷ Job cũ và chạy Job mới ngay lập tức.
- 🧠 **Mẹo ghi nhớ:** Tránh chạy đè trong CronJob → Chọn **`Forbid`**.

---

### Question 7 — Đáp án: **B**
- **Vì sao đúng:** Trong `JobSpec`:
  - `completions`: Tổng số lần hoàn thành cần đạt được.
  - `parallelism`: Số lượng Pod được phép chạy đồng thời tại một thời điểm.
- 🧠 **Mẹo ghi nhớ:** `completions` = Đích đến; `parallelism` = Số làn chạy đồng thời.

---

### Question 8 — Đáp án: **C**
- **Vì sao đúng:** Mặc định `backoffLimit` là **`6` lần**. Sau 6 lần Kubelet thử khởi động lại Pod bị fail mà không thành công, Job sẽ bị đánh dấu là Failed.
- 🧠 **Mẹo ghi nhớ:** Số lần thử lại mặc định của K8s Job là **6**.

---

### Question 9 — Đáp án: **B**
- **Vì sao đúng:** Chiến lược `Recreate` xoá sạch toàn bộ Pod cũ trước rồi mới tạo Pod mới. Nó gây ra Downtime, nhưng bắt buộc phải dùng khi ứng dụng chỉ cho phép 1 instance duy nhất kết nối vào database (chống xung đột ghi dữ liệu).
- 🧠 **Mẹo ghi nhớ:** `Recreate` = Chấp nhận downtime để tránh 2 version cùng ghi vào database.

---

### Question 10 — Đáp án: **B**
- **Vì sao đúng:** Lệnh `kubectl set image deployment/backend app=backend:v2.0` cập nhật image container `app` nhanh nhất mà không cần mở editor.
- 🧠 **Mẹo ghi nhớ:** Đổi image nhanh: `k set image deployment/<name> <container>=<new-image>`.

---

### Question 11 — Đáp án: **C**
- **Vì sao đúng:** Deployment quản lý ReplicaSet, và chính ReplicaSet Controller (vòng lặp trong `kube-controller-manager`) theo dõi số lượng Pod thực tế so với `spec.replicas`. Khi thiếu, ReplicaSet Controller gửi request lên API Server yêu cầu tạo Pod mới.
- 🧠 **Mẹo ghi nhớ:** Deployment quản lý ReplicaSet, **ReplicaSet quản lý số lượng Pods**.

---

### Question 12 — Đáp án: **A**
- **Vì sao đúng:** Kỹ thuật `kubectl rollout pause` tạm dừng việc tạo ReplicaSet mới khi cấu hình thay đổi. Bạn có thể thực hiện nhiều sửa đổi liên tiếp, sau đó chạy `kubectl rollout resume` để K8s gộp tất cả thay đổi vào duy nhất 1 đợt rollout.
- 🧠 **Mẹo ghi nhớ:** Gom nhiều thay đổi Deployment: `rollout pause` -> sửa đổi -> `rollout resume`.

---

### Question 13 — Đáp án: **B**
- **Vì sao đúng:** Kể từ K8s v1.20+, `DaemonSet` pods được quản lý và lập lịch bởi chính **`kube-scheduler`** (thông qua cơ chế NodeAffinity tự động chèn vào PodSpec) thay vì do DaemonSet controller tự gán nodeName như các phiên bản xa xưa.
- 🧠 **Mẹo ghi nhớ:** Mọi Pod (kể cả DaemonSet) trong K8s hiện đại đều do **`kube-scheduler`** xếp chỗ.

---

### Question 14 — Đáp án: **B**
- **Vì sao đúng:** `activeDeadlineSeconds` áp dụng cho Job quy định thời gian sống tối đa của toàn bộ Job. Nếu quá giờ này mà chưa đạt đủ `completions`, K8s sẽ dừng Job và terminate toàn bộ Pod.
- 🧠 **Mẹo ghi nhớ:** Hạn giờ cho Job: **`activeDeadlineSeconds`**.

---

### Question 15 — Đáp án: **B**
- **Vì sao đúng:** Để bảo vệ dữ liệu tối thượng cho cơ sở dữ liệu, khi StatefulSet bị xoá, Kubernetes **KHÔNG BAO GIỜ tự động xoá các PersistentVolumeClaim (PVC)** được tạo ra từ `volumeClaimTemplates`. Admin phải tự xoá PVC thủ công nếu thực sự muốn huỷ dữ liệu.
- 🧠 **Mẹo ghi nhớ:** Xoá StatefulSet **KHÔNG xoá PVC**. Dữ liệu luôn được an toàn!
