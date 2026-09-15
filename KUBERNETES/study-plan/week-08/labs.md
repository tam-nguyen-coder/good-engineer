# 🧪 Hands-on Labs — Tuần 8: RBAC & Authentication Management

> Thực hành tạo ServiceAccount, phân quyền Least Privilege bằng Role/RoleBinding và kiểm tra với `kubectl auth can-i`.
> Về [plan tuần 8](README.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

---

## Lab 8.1 — Cấu hình Role & RoleBinding cho ServiceAccount

**🎯 Mục tiêu:** Tạo một ServiceAccount dành cho Pod ứng dụng, giới hạn quyền chỉ được đọc ConfigMap trong namespace `app-dev`, và kiểm chứng Pod không thể đọc Secret.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Tạo namespace và ServiceAccount:
   ```bash
   kubectl create ns app-dev
   kubectl create serviceaccount api-reader-sa -n app-dev
   ```

2. Tạo dữ liệu mẫu (1 ConfigMap và 1 Secret):
   ```bash
   kubectl create configmap public-info --from-literal=status=active -n app-dev
   kubectl create secret generic secret-token --from-literal=token=XYZ123 -n app-dev
   ```

3. Tạo Role chỉ cho phép `get`, `list` trên tài nguyên `configmaps`:
   ```bash
   kubectl create role config-reader-role \
     --verb=get,list \
     --resource=configmaps \
     -n app-dev
   ```

4. Gán Role cho ServiceAccount qua RoleBinding:
   ```bash
   kubectl create rolebinding bind-api-reader \
     --role=config-reader-role \
     --serviceaccount=app-dev:api-reader-sa \
     -n app-dev
   ```

5. **Kiểm tra quyền hạn bằng `kubectl auth can-i`:**
   ```bash
   # 1. Kiểm tra xem có đọc được ConfigMap không (Kỳ vọng: yes):
   kubectl auth can-i get configmaps -n app-dev --as system:serviceaccount:app-dev:api-reader-sa

   # 2. Kiểm tra xem có tạo được ConfigMap không (Kỳ vọng: no):
   kubectl auth can-i create configmaps -n app-dev --as system:serviceaccount:app-dev:api-reader-sa

   # 3. Kiểm tra xem có đọc được Secret không (Kỳ vọng: no):
   kubectl auth can-i get secrets -n app-dev --as system:serviceaccount:app-dev:api-reader-sa

   # 4. Kiểm tra xem có xem được Pod ở namespace khác (default) không (Kỳ vọng: no):
   kubectl auth can-i get configmaps -n default --as system:serviceaccount:app-dev:api-reader-sa
   ```

---

## Lab 8.2 — ClusterRole kết hợp RoleBinding (Giới hạn phạm vi)

**🎯 Mục tiêu:** Sử dụng ClusterRole sẵn có của Kubernetes hoặc tự định nghĩa để gán cho User thông qua RoleBinding, chứng minh quyền hạn chỉ có hiệu lực cục bộ trong namespace.
**⏱️ ~20 phút**

### Các bước thực hiện:

1. Tạo một ClusterRole chung tên `deployment-manager`:
   ```bash
   kubectl create clusterrole deployment-manager \
     --verb=get,list,create,update,delete \
     --resource=deployments
   ```

2. Tạo RoleBinding trong namespace `team-blue` gán ClusterRole này cho user `developer-bob`:
   ```bash
   kubectl create ns team-blue
   kubectl create ns team-red

   kubectl create rolebinding bob-deploy-blue \
     --clusterrole=deployment-manager \
     --user=developer-bob \
     -n team-blue
   ```

3. **Kiểm tra quyền với `auth can-i`:**
   - Trong namespace `team-blue` (Kỳ vọng: `yes`):
     ```bash
     kubectl auth can-i create deployments -n team-blue --as developer-bob
     ```
   - Trong namespace `team-red` (Kỳ vọng: `no`):
     ```bash
     kubectl auth can-i create deployments -n team-red --as developer-bob
     ```
   *Kết luận: RoleBinding đã giới hạn phạm vi của ClusterRole chỉ nằm gói gọn bên trong namespace `team-blue`.*

---

## 🧹 Dọn dẹp:
```bash
kubectl delete ns app-dev team-blue team-red
kubectl delete clusterrole deployment-manager
```
