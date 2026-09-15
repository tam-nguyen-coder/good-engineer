# 🧪 Hands-on Labs — Tuần 2: Workloads & Controllers

> Thực hành quản lý Deployment, RollingUpdate, Rollback, DaemonSet và Jobs.
> Về [plan tuần 2](README.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

---

## Lab 2.1 — Rolling Updates & Rollback kịch bản lỗi

**🎯 Mục tiêu:** Triển khai một ứng dụng, nâng cấp phiên bản bằng RollingUpdate, mô phỏng lỗi tải image và hoàn tác về bản cũ.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Tạo Deployment ban đầu với image `nginx:1.24-alpine` có 4 replicas:
   ```bash
   kubectl create deployment web-app --image=nginx:1.24-alpine --replicas=4
   kubectl rollout status deployment/web-app
   ```

2. Kiểm tra ReplicaSet đang quản lý:
   ```bash
   kubectl get rs -l app=web-app
   ```
   *Ghi nhận lại tên ReplicaSet hiện tại (ví dụ: `web-app-7b89...` có 4 desired/current).*

3. Cấu hình chiến lược `RollingUpdate` với `maxSurge: 1` và `maxUnavailable: 0`:
   ```bash
   kubectl patch deployment web-app --type=strategic -p '{"spec":{"strategy":{"rollingUpdate":{"maxSurge":1,"maxUnavailable":0}}}}'
   ```

4. Nâng cấp Deployment lên image mới `nginx:1.25-alpine`:
   ```bash
   kubectl set image deployment/web-app nginx=nginx:1.25-alpine
   kubectl rollout status deployment/web-app
   ```

5. Kiểm tra danh sách ReplicaSets:
   ```bash
   kubectl get rs -l app=web-app
   ```
   *Quan sát: Sẽ xuất hiện 2 ReplicaSets (RS cũ có 0 replicas, RS mới có 4 replicas).*

6. **Mô phỏng sự cố:** Cập nhật sang một image không tồn tại `nginx:non-existent-tag`:
   ```bash
   kubectl set image deployment/web-app nginx=nginx:non-existent-tag
   kubectl get pods -w
   ```
   *Quan sát: Vì `maxUnavailable: 0`, K8s chỉ tạo 1 Pod mới thử nghiệm và Pod này bị lỗi `ImagePullBackOff` hoặc `ErrImagePull`. 4 Pod cũ VẪN HOẠT ĐỘNG BÌNH THƯỜNG đảm bảo không có downtime!*

7. Kiểm tra lịch sử cập nhật:
   ```bash
   kubectl rollout history deployment/web-app
   ```

8. Thực hiện Rollback khẩn cấp:
   ```bash
   kubectl rollout undo deployment/web-app
   kubectl rollout status deployment/web-app
   ```
   *Quan sát: Pod lỗi bị xoá ngay lập tức, hệ thống ổn định trở lại ở phiên bản `nginx:1.25-alpine`.*

---

## Lab 2.2 — Chuyển đổi Deployment sang DaemonSet

**🎯 Mục tiêu:** Thực hành kỹ thuật phòng thi tạo DaemonSet từ lệnh imperative của Deployment.
**⏱️ ~20 phút**

### Các bước thực hiện:

1. Sinh file manifest mẫu từ Deployment:
   ```bash
   kubectl create deployment node-monitor --image=busybox:1.28 $do > daemonset.yaml -- sh -c "while true; do echo Monitoring node; sleep 30; done"
   ```

2. Dùng `vim daemonset.yaml` hoặc lệnh `sed` để sửa đổi:
   - Đổi `kind: Deployment` thành `kind: DaemonSet`
   - Xoá trường `replicas: 1`
   - Xoá trường `strategy: ...` (nếu có)
   - Giữ nguyên phần `selector` và `template`

   Nội dung file sau khi chỉnh sửa:
   ```yaml
   apiVersion: apps/v1
   kind: DaemonSet
   metadata:
     name: node-monitor
     labels:
       app: node-monitor
   spec:
     selector:
       matchLabels:
         app: node-monitor
     template:
       metadata:
         labels:
           app: node-monitor
       spec:
         containers:
         - name: busybox
           image: busybox:1.28
           command: ["sh", "-c", "while true; do echo Monitoring node; sleep 30; done"]
   ```

3. Áp dụng manifest:
   ```bash
   kubectl apply -f daemonset.yaml
   ```

4. Kiểm tra sự phân bổ Pod:
   ```bash
   kubectl get daemonset node-monitor
   kubectl get pods -o wide -l app=node-monitor
   ```
   *Quan sát: Số lượng Pods được tạo ra sẽ đúng bằng số lượng Worker Nodes trong cụm của bạn (mỗi Node chạy đúng 1 Pod).*

---

## Lab 2.3 — Cấu hình Job và CronJob với `concurrencyPolicy`

**🎯 Mục tiêu:** Cấu hình Job chạy nhiều Pod đồng thời và CronJob chặn việc chạy chồng lấn tác vụ.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Tạo một Job hoàn thành 5 lần với 2 Pod chạy song song:
   ```bash
   cat << 'EOF' > batch-job.yaml
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: data-migrator
   spec:
     completions: 5
     parallelism: 2
     backoffLimit: 3
     template:
       spec:
         restartPolicy: OnFailure
         containers:
         - name: worker
           image: busybox:1.28
           command: ["sh", "-c", "echo 'Batch processing item'; sleep 4; exit 0"]
   EOF

   kubectl apply -f batch-job.yaml
   ```

2. Quan sát tiến trình chạy của Job:
   ```bash
   kubectl get job data-migrator -w
   ```
   *Quan sát: Luôn có 2 Pod chạy đồng thời cho tới khi tổng số completions đạt 5/5.*

3. Tạo CronJob với `concurrencyPolicy: Forbid`:
   ```bash
   cat << 'EOF' > heavy-cron.yaml
   apiVersion: batch/v1
   kind: CronJob
   metadata:
     name: sync-task
   spec:
     schedule: "*/1 * * * *" # Chạy mỗi phút
     concurrencyPolicy: Forbid # Không cho phép chạy chồng lấn
     jobTemplate:
       spec:
         template:
           spec:
             restartPolicy: Never
             containers:
             - name: runner
               image: busybox:1.28
               command: ["sh", "-c", "echo 'Job started...'; sleep 90; echo 'Job finished'"]
   EOF

   kubectl apply -f heavy-cron.yaml
   ```

4. Theo dõi trong 3 phút:
   ```bash
   kubectl get cronjob sync-task
   kubectl get jobs -w
   ```
   *Quan sát: Mặc dù lịch là 1 phút/lần, nhưng vì tác vụ mất 90 giây để hoàn thành, lần chạy ở phút thứ 2 sẽ bị bỏ qua (Forbid). Chỉ sau khi Job đầu tiên chạy xong, Job ở phút thứ 3 mới được phép kích hoạt.*

---

## 🧹 Dọn dẹp:
```bash
kubectl delete deployment web-app
kubectl delete daemonset node-monitor
kubectl delete job data-migrator
kubectl delete cronjob sync-task
```
