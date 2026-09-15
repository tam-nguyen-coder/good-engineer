# 🧪 Hands-on Labs — Tuần 4: ConfigMaps, Secrets, Probes & SecurityContext

> Thực hành nhúng ConfigMap/Secret vào Pod, cấu hình Health Probes (Liveness/Readiness/Startup), và siết chặt bảo mật bằng SecurityContext.
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

## 🧹 Dọn dẹp:
```bash
kubectl delete pod config-app probe-pod
kubectl delete svc probe-pod
kubectl delete secret app-credentials
kubectl delete configmap web-theme
kubectl delete ns restricted-ns
```
