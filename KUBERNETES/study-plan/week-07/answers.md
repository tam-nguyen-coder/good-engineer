# ✅ Answers & Explanations — Tuần 7: Storage Architecture

> Mở file này sau khi đã hoàn thành 15 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 7](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-B` · `2-A` · `3-B` · `4-B` · `5-B` · `6-B` · `7-A` · `8-B` · `9-A` · `10-A` · `11-A` · `12-B` · `13-A` · `14-A` · `15-B`

---

### Question 1 — Đáp án: **B**
- **Vì sao đúng:** Với `reclaimPolicy: Retain`, khi PVC bị xoá, PV sẽ chuyển sang trạng thái **`Released`**. Dữ liệu bên trong không bị xoá, nhưng PV này chưa thể gán cho PVC khác cho đến khi Quản trị viên can thiệp xử lý hoặc xoá `claimRef`.
- 🧠 **Mẹo ghi nhớ:** `Retain` = Giữ lại dữ liệu, PV chuyển sang `Released`.

---

### Question 2 — Đáp án: **A**
- **Vì sao đúng:**
  - `ReadWriteOnce` (RWO): Đọc ghi trên 1 node duy nhất.
  - `ReadOnlyMany` (ROX): Đọc trên nhiều node.
  - `ReadWriteMany` (RWX): Đọc và Ghi đồng thời từ nhiều Pod trên **nhiều node khác nhau** (thường dùng NFS / AWS EFS).
- 🧠 **Mẹo ghi nhớ:** RWX = Read-Write across Many nodes.

---

### Question 3 — Đáp án: **B**
- **Vì sao đúng:** `volumeBindingMode: WaitForFirstConsumer` hoãn việc gọi CSI driver tạo ổ cứng cho tới khi Pod được Scheduler gán vào 1 Node cụ thể. Điều này ngăn chặn triệt để lỗi "Volume ở Zone A nhưng Pod lại nằm ở Zone B".
- 🧠 **Mẹo ghi nhớ:** Multi-AZ cluster luôn dùng **`WaitForFirstConsumer`**.

---

### Question 4 — Đáp án: **B**
- **Vì sao đúng:** Để cho phép mở rộng dung lượng PVC trực tiếp, `StorageClass` bắt buộc phải có thuộc tính **`allowVolumeExpansion: true`**.
- 🧠 **Mẹo ghi nhớ:** Mở rộng dung lượng đĩa -> Cần `allowVolumeExpansion: true`.

---

### Question 5 — Đáp án: **B**
- **Vì sao đúng:** Các hệ thống file và Storage Controller của Kubernetes chỉ hỗ trợ mở rộng (Scale Up), **tuyệt đối không hỗ trợ thu nhỏ (Shrink/Reduce)** dung lượng volume vì nguy cơ làm hỏng hệ thống file và mất dữ liệu. API Server sẽ trả về lỗi ngay lập tức.
- 🧠 **Mẹo ghi nhớ:** K8s PVC chỉ có thể tăng, **KHÔNG THỂ GIẢM** dung lượng.

---

### Question 6 — Đáp án: **B**
- **Vì sao đúng:** RWO (`ReadWriteOnce`) cho phép nhiều Pod trên cùng một Node cùng ghi vào đĩa. `ReadWriteOncePod` (RWOP - GA v1.29) siết chặt hơn nữa: Chỉ duy nhất **1 Pod đơn lẻ** trong toàn cluster được phép mount volume đó, ngăn chặn việc 2 container ghi đè dữ liệu lên nhau.
- 🧠 **Mẹo ghi nhớ:** `RWOP` = Đúng 1 Pod duy nhất được mount đọc-ghi.

---

### Question 7 — Đáp án: **A**
- **Vì sao đúng:** Trong Static Provisioning, bộ điều khiển so khớp PVC với PV nếu: dung lượng của PV $\ge$ dung lượng của PVC, `accessModes` tương thích, và `storageClassName` khớp nhau.
- 🧠 **Mẹo ghi nhớ:** Dung lượng PV phải $\ge$ PVC, AccessModes phải bao hàm.

---

### Question 8 — Đáp án: **B**
- **Vì sao đúng:** `PersistentVolume` (PV) là tài nguyên hạ tầng do Admin quản lý ở mức toàn cụm (**Cluster-scoped**), không có namespace. Trong khi `PersistentVolumeClaim` (PVC) là yêu cầu của developer bên trong một **Namespace** cụ thể (**Namespaced**).
- 🧠 **Mẹo ghi nhớ:** PV = Toàn cụm (Cluster-scoped); PVC = Trong Namespace (Namespaced).

---

### Question 9 — Đáp án: **A**
- **Vì sao đúng:** Mặc định `emptyDir` lưu trữ trên ổ đĩa của Node. Nếu đặt `emptyDir.medium: "Memory"`, Kubernetes sẽ mount một phân vùng RAM dạng `tmpfs`, cho tốc độ đọc ghi cực nhanh (nhưng tiêu tốn bộ nhớ RAM của Pod).
- 🧠 **Mẹo ghi nhớ:** Lưu tạm trên RAM -> `emptyDir.medium: "Memory"`.

---

### Question 10 — Đáp án: **A**
- **Vì sao đúng:** Container Storage Interface (CSI) là chuẩn công nghiệp mở giúp tách biệt mã nguồn của Kubernetes Core khỏi các driver lưu trữ của bên thứ ba, cho phép cài đặt driver qua DaemonSet hoặc Deployment mà không cần build lại mã nguồn K8s.
- 🧠 **Mẹo ghi nhớ:** CSI = Chuẩn giao tiếp driver lưu trữ mở của Kubernetes.

---

### Question 11 — Đáp án: **A**
- **Vì sao đúng:** Khai báo chuẩn: Trong `spec.volumes` định nghĩa volume kiểu `persistentVolumeClaim` trỏ vào `claimName`. Trong `spec.containers[].volumeMounts` mount volume đó vào đường dẫn `mountPath`.
- 🧠 **Mẹo ghi nhớ:** Cặp đôi hoàn hảo: `volumes.persistentVolumeClaim` + `volumeMounts.mountPath`.

---

### Question 12 — Đáp án: **B**
- **Vì sao đúng:** `reclaimPolicy: Delete` (thường là mặc định của dynamic provisioning) sẽ tự động kích hoạt CSI driver xoá luôn cả tài nguyên lưu trữ vật lý (như AWS EBS Volume) trên cloud khi PVC bị xoá.
- 🧠 **Mẹo ghi nhớ:** `reclaimPolicy: Delete` = Xoá PVC là xoá luôn cả đĩa vật lý.

---

### Question 13 — Đáp án: **A**
- **Vì sao đúng:** Volume kiểu `local` gắn với một ổ cứng cố định trên một máy vật lý cụ thể, do đó K8s bắt buộc PV phải có trường `spec.nodeAffinity` để Kube-scheduler biết node nào có ổ đĩa này để xếp Pod vào đúng node đó.
- 🧠 **Mẹo ghi nhớ:** PV kiểu `local` bắt buộc phải có **`nodeAffinity`**.

---

### Question 14 — Đáp án: **A**
- **Vì sao đúng:** `volumeMode` hỗ trợ 2 chế độ:
  - `Filesystem` (Mặc định): Mount vào thư mục hệ thống file.
  - `Block`: Mount trực tiếp thiết bị khối (raw block device) cho các database tối ưu sâu (như Oracle/Ceph).
- 🧠 **Mẹo ghi nhớ:** VolumeMode: **`Filesystem`** hoặc **`Block`**.

---

### Question 15 — Đáp án: **B**
- **Vì sao đúng:** Cơ chế bảo vệ **Storage Object in Use Protection** gắn Finalizer `kubernetes.io/pvc-protection` vào PVC. Nếu PVC đang được mount bởi một Pod đang hoạt động, lệnh xoá sẽ hoãn lại cho đến khi Pod bị chấm dứt hoàn toàn, tránh việc đĩa bị ngắt đột ngột gây hỏng ứng dụng.
- 🧠 **Mẹo ghi nhớ:** PVC đang dùng mà bị xoá sẽ treo ở **`Terminating`** cho đến khi Pod tắt.
