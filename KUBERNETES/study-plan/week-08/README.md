# 🔐 Tuần 8 — Security, Authentication, RBAC & Cluster Hardening

> **Domain:** Cluster Architecture, Installation & Configuration (25%) & Security · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 8/10
>
> **Điều hướng:** [⬅️ Tuần 7](../week-07/README.md) · [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [Tuần 9 ➡️](../week-09/README.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Hiểu trọn vẹn mô hình **Authentication & Authorization** trong Kubernetes: K8s **không có bảng User database** trong etcd! Danh tính con người được xác thực qua **X.509 Client Certificates** hoặc OpenID Connect (OIDC).
- Cấu hình file **`kubeconfig`** (`~/.kube/config`): Làm việc với `clusters`, `users`, `contexts`, và chuyển đổi ngữ cảnh an toàn bằng `kubectl config use-context`.
- Phân biệt **User Account** (dành cho con người, xác thực qua certs bên ngoài) và **ServiceAccount** (dành cho ứng dụng/Pod chạy bên trong cluster, cấp phát token qua TokenRequest API).
- Làm chủ 4 đối tượng RBAC: **`Role`**, **`ClusterRole`**, **`RoleBinding`**, và **`ClusterRoleBinding`**.
- Thuần thục lệnh kiểm tra quyền hạn **`kubectl auth can-i`** — công cụ kiểm tra nhanh nhất trong bài thi CKA.
- Cấu hình **Encryption at Rest** cho etcd để mã hoá Kubernetes Secrets bằng provider `aescbc` hoặc `kms`.

---

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Authentication, PKI & Kubeconfig (~3h)

```text
               +-------------------------------------------+
               |                  REQUEST                  |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |         1. AUTHENTICATION (AuthN)         |
               |       (X.509 Certs, Bearer Token)         |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |          2. AUTHORIZATION (AuthZ)         |
               |       (RBAC: Role & RoleBinding)          |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |         3. ADMISSION CONTROLLERS          |
               |       (Mutating -> Validating)            |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |              ETCD STORAGE                 |
               +-------------------------------------------+
```

#### 1. Cấu trúc một Kubeconfig file
Kubeconfig bao gồm 3 phần ghép lại với nhau:
- **`clusters`**: Địa chỉ API Server + CA certificate.
- **`users`**: Client certificate + Client private key (hoặc token).
- **`contexts`**: Sự kết hợp giữa 1 `cluster` + 1 `user` + 1 `namespace` mặc định.
- Lệnh đổi context phòng thi:
  ```bash
  kubectl config use-context cluster1-admin
  kubectl config set-context --current --namespace=dev
  ```

#### 2. ServiceAccount & Bound Tokens (v1.24+)
- Khi tạo Pod, Kubelet tự động mount một projected volume chứa JWT token của ServiceAccount tại `/var/run/secrets/kubernetes.io/serviceaccount/token`.
- Token này có hạn sử dụng ngắn hạn (thường là 1 giờ) và tự động xoay vòng (TokenRequest API).

---

### 🅱️ Buổi B — RBAC: Roles, ClusterRoles & Bindings (~3.5h)

```text
                      SCOPE: 1 NAMESPACE               SCOPE: TOÀN CLUSTER
             +----------------------------------+----------------------------------+
QUYỀN HẠN:   |             [ Role ]             |         [ ClusterRole ]          |
             |   (get, list, create pods trong  |  (list nodes, pv, namespaces,    |
             |        namespace "dev")          |  hoặc template pods cho mọi ns)  |
             +----------------------------------+----------------------------------+
                              |                                  |
                              v                                  v
GÁN QUYỀN:   +----------------------------------+----------------------------------+
             |         [ RoleBinding ]          |      [ ClusterRoleBinding ]      |
             |  (Gán Role hoặc ClusterRole cho  | (Gán ClusterRole cho User/Group  |
             |  User trong phạm vi 1 Namespace) |     trên TOÀN BỘ CLUSTER)        |
             +----------------------------------+----------------------------------+
```

#### Lệnh Imperative tạo nhanh RBAC (BẮT BUỘC DÙNG TRONG CKA):
```bash
# 1. Tạo Role chỉ cho phép get, list, watch trên Pods trong namespace 'dev':
kubectl create role pod-reader --verb=get,list,watch --resource=pods -n dev

# 2. Tạo ClusterRole cho phép quản lý Nodes và PersistentVolumes:
kubectl create clusterrole node-admin --verb=get,list,create,delete --resource=nodes,pv

# 3. Tạo RoleBinding gán Role 'pod-reader' cho user 'john':
kubectl create rolebinding read-pods-john --role=pod-reader --user=john -n dev

# 4. Gán ClusterRole 'node-admin' cho một ServiceAccount:
kubectl create clusterrolebinding sa-node-admin --clusterrole=node-admin --serviceaccount=kube-system:my-sa
```

#### Bí kíp kiểm tra quyền siêu tốc với `kubectl auth can-i`:
```bash
# Kiểm tra xem user john có được phép xoá deployment trong namespace dev không:
kubectl auth can-i delete deployments --as john -n dev

# Kiểm tra xem ServiceAccount trong namespace prod có được xem secret không:
kubectl auth can-i get secrets --as system:serviceaccount:prod:web-sa -n prod
```

---

### 🅲 Buổi C — Encrypting Secret Data at Rest (~2.5h)

Mặc định, Kubernetes lưu trữ Secrets trong etcd dưới dạng **Plaintext Base64 encoded** (bất kỳ ai truy cập được etcd đều có thể đọc toàn bộ mật khẩu). Để mã hoá:
1. Tạo file cấu hình `EncryptionConfiguration` với provider `aescbc` hoặc `secretbox`.
2. Sửa file static pod manifest `/etc/kubernetes/manifests/kube-apiserver.yaml`, thêm cờ:
   `--encryption-provider-config=/etc/kubernetes/enc/enc.yaml`.
3. Mount file mã hoá vào container của API Server.
4. Chạy lệnh cập nhật để mã hoá các Secret cũ:
   `kubectl get secrets -A -o json | kubectl replace -f -`.

---

### 🅳 Buổi D — Practice & Review (~2h)

- Hoàn thành các bài lab phân quyền người dùng và service account trong [labs.md](labs.md).
- Giải quyết bài toán: Cho một ServiceAccount bị lỗi `403 Forbidden` khi đọc ConfigMap, dùng RBAC cấp quyền tối thiểu (Least Privilege).

---

## 🚪 Cổng tự kiểm tra Tuần 8 (Self-check Gate)

1. [ ] Có thể dùng `RoleBinding` để gán một `ClusterRole` cho một User được không? Kết quả quyền hạn của User đó sẽ như thế nào? *(Đáp án: ĐƯỢC. Đây là kỹ thuật phổ biến. Quyền hạn trong ClusterRole sẽ được áp dụng NHƯNG CHỈ TRONG PHẠM VI 1 NAMESPACE của RoleBinding đó).*
2. [ ] Lệnh kiểm tra xem User `alice` có quyền tạo Pod trong namespace `marketing` là gì? *(Đáp án: `kubectl auth can-i create pods -n marketing --as alice`).*
3. [ ] Định dạng đầy đủ khi giả lập một ServiceAccount tên `worker-sa` ở namespace `app` trong lệnh `kubectl auth can-i` là gì? *(Đáp án: `--as system:serviceaccount:app:worker-sa`).*
