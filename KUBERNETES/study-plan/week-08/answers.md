# ✅ Answers & Explanations — Tuần 8: Security, Authentication & RBAC

> Mở file này sau khi đã hoàn thành 15 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 8](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-B` · `2-A` · `3-B` · `4-B` · `5-B` · `6-A` · `7-B` · `8-B` · `9-B` · `10-C` · `11-B` · `12-B` · `13-A` · `14-A` · `15-B`

---

### Question 1 — Đáp án: **B**
- **Vì sao đúng:** Khi một `ClusterRole` được gán thông qua một **`RoleBinding`**, phạm vi quyền hạn của nó sẽ bị thu hẹp và CHỈ CÓ HIỆU LỰC TRONG NAMESPACE của RoleBinding đó (ở đây là namespace `development`). Đây là kỹ thuật tái sử dụng quyền rất phổ biến trong Kubernetes.
- 🧠 **Mẹo ghi nhớ:** ClusterRole + **RoleBinding** = Quyền chỉ có trong **1 Namespace**.

---

### Question 2 — Đáp án: **A**
- **Vì sao đúng:** Lệnh `kubectl auth can-i <action> <resource> -n <ns> --as <user>` là công cụ số 1 để kiểm tra quyền. Đối với ServiceAccount, định dạng tên đầy đủ khi giả lập danh tính là: `system:serviceaccount:<namespace>:<sa-name>`.
- 🧠 **Mẹo ghi nhớ:** Giả lập ServiceAccount: `--as system:serviceaccount:<ns>:<sa-name>`.

---

### Question 3 — Đáp án: **B**
- **Vì sao đúng:** Kubernetes không quản lý bảng User trong etcd. Danh tính của con người được xác thực dựa trên chữ ký trong chứng chỉ số X.509 Client Certificate (trường `CN` là username, trường `O` là group) do K8s CA ký, hoặc qua OIDC tokens.
- 🧠 **Mẹo ghi nhớ:** K8s **không có User database** trong etcd; xác thực qua X.509 Certs hoặc OIDC.

---

### Question 4 — Đáp án: **B**
- **Vì sao đúng:** Kể từ bản v1.24+, tính năng `BoundServiceAccountTokenVolume` chuyển sang GA. K8s không còn tự động tạo các Secret chứa token vĩnh viễn nữa nhằm siết chặt bảo mật. Token hiện nay được sinh ra theo yêu cầu qua TokenRequest API, có hạn sử dụng và gắn chặt với vòng đời của Pod.
- 🧠 **Mẹo ghi nhớ:** K8s 1.24+ **không tự tạo Secret** cho ServiceAccount.

---

### Question 5 — Đáp án: **B**
- **Vì sao đúng:** Các workload ứng dụng như `Deployments`, `DaemonSets`, `StatefulSets`, `ReplicaSets` đều thuộc nhóm API Group có tên là **`"apps"`**.
- 🧠 **Mẹo ghi nhớ:** Deployment/StatefulSet thuộc `apiGroups: ["apps"]`.

---

### Question 6 — Đáp án: **A**
- **Vì sao đúng:** Để xem log của Pod, quyền cần cấp trong RBAC là trên sub-resource **`pods/logs`**.
- 🧠 **Mẹo ghi nhớ:** Xem log Pod trong RBAC = resource **`pods/logs`**.

---

### Question 7 — Đáp án: **B**
- **Vì sao đúng:** Lệnh phê duyệt yêu cầu cấp chứng chỉ trong Kubernetes là `kubectl certificate approve <csr-name>`.
- 🧠 **Mẹo ghi nhớ:** Duyệt chứng chỉ = **`kubectl certificate approve`**.

---

### Question 8 — Đáp án: **B**
- **Vì sao đúng:** Context trong Kubeconfig định nghĩa một bộ 3: Ta đang kết nối tới **Cluster** nào, bằng danh tính **User** nào, và làm việc trên **Namespace** mặc định nào.
- 🧠 **Mẹo ghi nhớ:** Context = Cluster + User + Default Namespace.

---

### Question 9 — Đáp án: **B**
- **Vì sao đúng:** Lệnh chuyển đổi context chuẩn trong Kubernetes CLI: `kubectl config use-context <context-name>`.
- 🧠 **Mẹo ghi nhớ:** Đổi context trong phòng thi: **`kubectl config use-context ...`**.

---

### Question 10 — Đáp án: **C**
- **Vì sao đúng:** `ClusterRoleBinding` có quyền hạn trên toàn bộ cụm và có thể liên kết ClusterRole tới Users, Groups hoặc ServiceAccounts.
- 🧠 **Mẹo ghi nhớ:** ClusterRoleBinding áp dụng toàn cụm cho User/Group/SA.

---

### Question 11 — Đáp án: **B**
- **Vì sao đúng:** Nhóm Core API Group (được ký hiệu bằng chuỗi rỗng `""`) chứa các tài nguyên nguyên thuỷ ban đầu của Kubernetes như `pods`, `services`, `configmaps`, `secrets`, `namespaces`, `nodes`, `persistentvolumes`.
- 🧠 **Mẹo ghi nhớ:** Pods, Services, ConfigMaps, Secrets thuộc `apiGroups: [""]`.

---

### Question 12 — Đáp án: **B**
- **Vì sao đúng:** `kube-apiserver` là thành phần duy nhất đọc ghi trực tiếp vào `etcd`. Do đó, cấu hình mã hoá dữ liệu tĩnh (EncryptionConfiguration) phải được cung cấp cho API Server thông qua cờ `--encryption-provider-config`.
- 🧠 **Mẹo ghi nhớ:** Encryption at Rest cấu hình tại **`kube-apiserver`**.

---

### Question 13 — Đáp án: **A**
- **Vì sao đúng:** Trong PodSpec, trường `spec.serviceAccountName` được dùng để gán ServiceAccount cho Pod (trước đây có trường `serviceAccount` nhưng đã deprecated).
- 🧠 **Mẹo ghi nhớ:** Gán SA cho Pod: **`spec.serviceAccountName`**.

---

### Question 14 — Đáp án: **A**
- **Vì sao đúng:** Khi subject trong RoleBinding là `User` hoặc `Group`, trường `apiGroup` bắt buộc phải là **`rbac.authorization.k8s.io`**. Riêng đối với `ServiceAccount`, trường `apiGroup` để trống hoặc không khai báo (vì SA là core resource).
- 🧠 **Mẹo ghi nhớ:** Subject User/Group đi kèm `apiGroup: rbac.authorization.k8s.io`.

---

### Question 15 — Đáp án: **B**
- **Vì sao đúng:** Mọi chứng chỉ PKI cốt lõi của cụm được công cụ `kubeadm` khởi tạo đều nằm cố định tại thư mục **`/etc/kubernetes/pki`** (và `/etc/kubernetes/pki/etcd` cho etcd).
- 🧠 **Mẹo ghi nhớ:** Chứng chỉ cluster luôn nằm tại **`/etc/kubernetes/pki`**.
