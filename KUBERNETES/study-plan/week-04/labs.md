# 🧪 Hands-on Labs — Tuần 4: ConfigMaps, Secrets, Probes & SecurityContext

> Thực hành nhúng ConfigMap/Secret vào Pod, cấu hình Health Probes (Liveness/Readiness/Startup), siết chặt bảo mật bằng SecurityContext, và đóng gói/cài đặt component bằng **Kustomize + Helm**.
> Về [plan tuần 4](README.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

---

## Lab 4.1 — Quản lý ConfigMaps & Secrets (Environment vs Volume Mount)

**🎯 Mục tiêu:** Cấu hình Pod đọc Secret qua biến môi trường và đọc ConfigMap được mount thành file với khả năng tự động cập nhật.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Tạo Secret chứa mật khẩu DB và ConfigMap chứa file cấu hình:
   ```bash
   kubectl create secret generic app-credentials \
     --from-literal=DB_USER=postgres \
     --from-literal=DB_PASSWORD=SecretPassword999!

   kubectl create configmap web-theme \
     --from-literal=color=blue \
     --from-literal=title="Production Portal"
   ```

2. Tạo Pod sử dụng cả 2 cơ chế:
   ```bash
   cat << 'EOF' > config-demo.yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: config-app
   spec:
     containers:
     - name: app
       image: busybox:1.28
       command: ["sh", "-c", "while true; do cat /etc/theme/color; sleep 5; done"]
       # 1. Đọc Secret qua Environment Variables
       env:
       - name: DATABASE_USER
         valueFrom:
           secretKeyRef:
             name: app-credentials
             key: DB_USER
       - name: DATABASE_PASSWORD
         valueFrom:
           secretKeyRef:
             name: app-credentials
             key: DB_PASSWORD
       # 2. Mount ConfigMap thành thư mục /etc/theme
       volumeMounts:
       - name: theme-volume
         mountPath: /etc/theme
     volumes:
     - name: theme-volume
       configMap:
         name: web-theme
   EOF

   kubectl apply -f config-demo.yaml
   ```

3. Kiểm tra biến môi trường bên trong Pod:
   ```bash
   kubectl exec config-app -- env | grep DATABASE_
   ```

4. Kiểm tra file được mount từ ConfigMap:
   ```bash
   kubectl exec config-app -- ls -la /etc/theme
   kubectl exec config-app -- cat /etc/theme/title
   ```

5. **Thực nghiệm cập nhật tự động:**
   Sửa ConfigMap đổi `color` từ `blue` sang `gold`:
   ```bash
   kubectl patch configmap web-theme --type=merge -p '{"data":{"color":"gold"}}'
   ```
   Chờ khoảng 10–30 giây và kiểm tra lại log của Pod:
   ```bash
   kubectl logs config-app --tail=5
   ```
   *Quan sát: Log sẽ tự động đổi sang in chữ `gold` mà không cần restart Pod!*

---

## Lab 4.2 — Khắc phục sự cố Liveness vs Readiness Probes

**🎯 Mục tiêu:** Cấu hình cả Liveness và Readiness Probes, chứng minh Readiness Probe ngắt traffic mà không làm chết container.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Tạo Pod Nginx có cả 2 Probes kiểm tra file trong container:
   ```bash
   cat << 'EOF' > probes-demo.yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: probe-pod
     labels:
       app: probe-test
   spec:
     containers:
     - name: web
       image: nginx:alpine
       # Tạo sẵn 2 file healthy
       lifecycle:
         postStart:
           exec:
             command: ["/bin/sh", "-c", "touch /tmp/live; touch /tmp/ready"]
       # Liveness: Nếu mất file /tmp/live -> Restart container
       livenessProbe:
         exec:
           command: ["cat", "/tmp/live"]
         initialDelaySeconds: 5
         periodSeconds: 5
       # Readiness: Nếu mất file /tmp/ready -> Gỡ khỏi service, KHÔNG restart
       readinessProbe:
         exec:
           command: ["cat", "/tmp/ready"]
         initialDelaySeconds: 5
         periodSeconds: 5
   EOF

   kubectl apply -f probes-demo.yaml
   ```

2. Expose Pod thành Service:
   ```bash
   kubectl expose pod probe-pod --port=80 --target-port=80
   kubectl get ep probe-pod
   ```
   *Quan sát: Cột `ENDPOINTS` có hiển thị IP của `probe-pod`.*

3. **Mô phỏng Readiness Failure:** Xoá file `/tmp/ready`:
   ```bash
   kubectl exec probe-pod -- rm /tmp/ready
   sleep 7
   kubectl get pod probe-pod
   kubectl get ep probe-pod
   ```
   *Quan sát: Cột `READY` của Pod chuyển sang `0/1`, cột `RESTARTS` vẫn là `0`! Danh sách `ENDPOINTS` của Service bị rỗng (`<none>`), traffic không thể vào Pod này nữa nhưng container không bị kill!*

4. Khôi phục lại Readiness:
   ```bash
   kubectl exec probe-pod -- touch /tmp/ready
   sleep 7
   kubectl get ep probe-pod
   ```
   *Quan sát: Pod quay lại `1/1 Ready`, Endpoints tự động kết nối lại.*

5. **Mô phỏng Liveness Failure:** Xoá file `/tmp/live`:
   ```bash
   kubectl exec probe-pod -- rm /tmp/live
   sleep 10
   kubectl get pod probe-pod
   ```
   *Quan sát: Cột `RESTARTS` tăng lên 1! Kubelet đã kill container và tạo container mới.*

---

## Lab 4.3 — Cấu hình SecurityContext & Pod Security Standards

**🎯 Mục tiêu:** Cấu hình Pod chạy không quyền root và áp dụng chính sách PSA trên namespace.
**⏱️ ~20 phút**

### Các bước thực hiện:

1. Tạo một namespace an toàn `restricted-ns`:
   ```bash
   kubectl create ns restricted-ns
   kubectl label ns restricted-ns \
     pod-security.kubernetes.io/enforce=restricted \
     pod-security.kubernetes.io/enforce-version=latest
   ```

2. Thử tạo một Pod không an toàn (chạy root mặc định):
   ```bash
   kubectl run bad-pod --image=nginx:alpine -n restricted-ns
   ```
   *Quan sát thông báo lỗi từ API Server: Yêu cầu bị từ chối vì vi phạm Pod Security Standards: `allowPrivilegeEscalation != false`, `runAsNonRoot != true`, `seccompProfile`...*

3. Tạo Pod an toàn chuẩn chỉnh đạt yêu cầu Restricted:
   ```bash
   cat << 'EOF' > secure-pod.yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: secure-app
     namespace: restricted-ns
   spec:
     securityContext:
       runAsNonRoot: true
       runAsUser: 10001
       seccompProfile:
         type: RuntimeDefault
     containers:
     - name: app
       image: busybox:1.28
       command: ["sleep", "3600"]
       securityContext:
         allowPrivilegeEscalation: false
         readOnlyRootFilesystem: true
         capabilities:
           drop:
           - ALL
   EOF

   kubectl apply -f secure-pod.yaml
   kubectl get pod secure-app -n restricted-ns
   ```
   *Quan sát: Pod được khởi tạo thành công ở trạng thái `Running`.*

---

---

## Lab 4.4 — Kustomize: Base + Overlays cho 2 môi trường

**🎯 Mục tiêu:** Dựng một `base` dùng chung rồi đắp 2 overlay `staging` / `production` khác nhau về namespace, số replicas, image tag và ConfigMap — không nhân bản một dòng YAML nào.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Dựng cây thư mục và file base:
   ```bash
   mkdir -p ~/kustomize-lab/base ~/kustomize-lab/overlays/staging ~/kustomize-lab/overlays/production
   cd ~/kustomize-lab

   cat << 'EOF' > base/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: web-app
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: web-app
     template:
       metadata:
         labels:
           app: web-app
       spec:
         containers:
         - name: nginx
           image: nginx:1.25
           ports:
           - containerPort: 80
   EOF

   cat << 'EOF' > base/service.yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: web-app
   spec:
     selector:
       app: web-app
     ports:
     - port: 80
       targetPort: 80
   EOF

   cat << 'EOF' > base/kustomization.yaml
   apiVersion: kustomize.config.k8s.io/v1beta1
   kind: Kustomization
   resources:
     - deployment.yaml
     - service.yaml
   EOF
   ```

2. Overlay `staging` — chỉ đổi namespace và thêm nhãn:
   ```bash
   cat << 'EOF' > overlays/staging/kustomization.yaml
   apiVersion: kustomize.config.k8s.io/v1beta1
   kind: Kustomization
   namespace: staging
   namePrefix: stg-
   labels:
     - pairs:
         env: staging
       includeSelectors: true
   resources:
     - ../../base
   EOF
   ```

3. Overlay `production` — đổi replicas, image tag, và sinh ConfigMap tên cố định:
   ```bash
   cat << 'EOF' > overlays/production/kustomization.yaml
   apiVersion: kustomize.config.k8s.io/v1beta1
   kind: Kustomization
   namespace: production
   namePrefix: prod-
   labels:
     - pairs:
         env: production
       includeSelectors: true
   resources:
     - ../../base
   images:
     - name: nginx
       newTag: 1.27-alpine
   replicas:
     - name: web-app
       count: 4
   configMapGenerator:
     - name: app-settings
       literals:
         - LOG_LEVEL=warn
   generatorOptions:
     disableNameSuffixHash: true
   EOF
   ```

4. **Xem trước** (bước không bao giờ được bỏ) rồi mới apply:
   ```bash
   kubectl kustomize overlays/production/

   kubectl create namespace staging
   kubectl create namespace production
   kubectl apply -k overlays/staging/
   kubectl apply -k overlays/production/
   ```

5. Kiểm chứng kết quả:
   ```bash
   kubectl get deploy,svc,cm -n staging
   kubectl get deploy,svc,cm -n production

   # Production phải là 4 replicas, image 1.27-alpine, ConfigMap tên SẠCH (không hash)
   kubectl get deploy prod-web-app -n production \
     -o jsonpath='{.spec.replicas}{"\t"}{.spec.template.spec.containers[0].image}{"\n"}'
   kubectl get cm -n production
   ```

### ✅ Kết quả mong đợi:
- `staging`: Deployment `stg-web-app`, **1** replica, image `nginx:1.25`.
- `production`: Deployment `prod-web-app`, **4** replicas, image `nginx:1.27-alpine`, ConfigMap tên đúng `prod-app-settings` (namePrefix có áp dụng, nhưng **không có hash-suffix**).
- Service selector ở cả hai overlay đã tự động được bổ sung nhãn `env` — đó là tác dụng của `includeSelectors: true`.

### 🔬 Thử nghiệm thêm (hiểu bản chất hash-suffix):
Xoá `generatorOptions` khỏi overlay production rồi chạy lại `kubectl apply -k overlays/production/`. Quan sát ConfigMap mới mọc thêm hậu tố băm. Đổi `LOG_LEVEL=warn` thành `LOG_LEVEL=debug`, apply lần nữa → tên ConfigMap đổi lần nữa. Đây chính là cơ chế khiến workload tham chiếu tới nó tự rolling restart khi config thay đổi.

---

## Lab 4.5 — Helm: Cài, nâng cấp, soi và rollback một cluster component

**🎯 Mục tiêu:** Thực hiện trọn vòng đời một Helm release đúng như dạng task hay gặp trong CKA: `repo add` → `show values` → `install` → `upgrade` → `history` → `rollback`.
**⏱️ ~25 phút**

> 📦 Nếu máy chưa có Helm:
> ```bash
> curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
> helm version
> ```

### Các bước thực hiện:

1. Thêm repo và khảo sát chart **trước khi** cài:
   ```bash
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm repo update

   helm search repo bitnami/nginx --versions | head
   helm show chart bitnami/nginx | head -20
   helm show values bitnami/nginx > /tmp/nginx-defaults.yaml
   wc -l /tmp/nginx-defaults.yaml
   ```

2. Render offline để biết chính xác chart sẽ tạo ra cái gì (**không** chạm cluster):
   ```bash
   helm template demo bitnami/nginx --set replicaCount=2 | grep -E '^kind:|^  name:'
   ```

3. Cài đặt vào namespace riêng, override 2 giá trị:
   ```bash
   helm install web bitnami/nginx \
     --namespace web-demo --create-namespace \
     --set replicaCount=2 \
     --set service.type=ClusterIP

   helm list -n web-demo
   kubectl get all -n web-demo
   ```

4. Nâng cấp release và xem lịch sử revision:
   ```bash
   helm upgrade web bitnami/nginx -n web-demo \
     --set replicaCount=4 \
     --set service.type=ClusterIP

   helm history web -n web-demo
   kubectl get deploy -n web-demo
   ```

5. Soi cấu hình thực tế của release:
   ```bash
   # Chỉ những gì mình đã override
   helm get values web -n web-demo

   # TẤT CẢ values, kể cả mặc định của chart
   helm get values web -n web-demo -a | head -30

   # YAML thực sự đang nằm trong cluster
   helm get manifest web -n web-demo | grep -E '^kind:|replicas:'
   ```

6. Hoàn tác về revision 1 và kiểm chứng:
   ```bash
   helm rollback web 1 -n web-demo
   helm history web -n web-demo
   kubectl get deploy -n web-demo   # Phải quay về 2 replicas
   ```

7. Bài tập phản xạ — chứng minh `helm list` bị giới hạn namespace:
   ```bash
   helm list                 # Rỗng (đang ở namespace default)
   helm list -A              # Thấy release 'web' ở web-demo
   ```

### ✅ Kết quả mong đợi:
- `helm history web -n web-demo` hiển thị **3 revision**: `1 deployed→superseded`, `2 superseded`, `3 deployed (rollback to 1)`.
- Sau rollback, Deployment quay lại **2 replicas**.
- `helm list` không có gì còn `helm list -A` thì có → khắc sâu thói quen luôn gõ `-A`.

### 🧠 Ghi vào sổ tay phòng thi:
| Đề bài yêu cầu | Lệnh |
|---|---|
| "install chart X into namespace Y" | `helm install <rel> <chart> -n Y --create-namespace` |
| "what values is release Z using?" | `helm get values Z -n <ns> -a` |
| "how many releases in the cluster?" | `helm list -A` |
| "revert the component" | `helm history` → `helm rollback <rel> <rev> -n <ns>` |
| "write the manifests to a file, do not apply" | `helm template <rel> <chart> > out.yaml` |


---

## 🧹 Dọn dẹp:
```bash
kubectl delete pod config-app probe-pod
kubectl delete svc probe-pod
kubectl delete secret app-credentials
kubectl delete configmap web-theme
kubectl delete ns restricted-ns
kubectl delete ns staging production web-demo --ignore-not-found
helm uninstall web -n web-demo 2>/dev/null
rm -rf ~/kustomize-lab
```
