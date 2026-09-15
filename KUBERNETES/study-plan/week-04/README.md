# 🟩 Tuần 4 — Configuration, Probes, SecurityContext & Pod Security Standards

> **Domain:** Workloads & Scheduling (15%) & Security (25%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 4/10
>
> **Điều hướng:** [⬅️ Tuần 3](../week-03/README.md) · [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [Tuần 5 ➡️](../week-05/README.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Làm chủ việc cấu hình ứng dụng động qua **`ConfigMap`** và **`Secret`** (dưới dạng Environment Variables, `envFrom`, và Volume Mounts).
- Phân biệt rõ ràng giữa 3 loại Health Check Probes:
  - **`StartupProbe`**: Chờ ứng dụng khởi động chậm, bảo vệ không bị kill oan.
  - **`LivenessProbe`**: Phát hiện tiến trình bị deadlock/treo để **RESTART container**.
  - **`ReadinessProbe`**: Kiểm tra container đã sẵn sàng nhận request chưa để **THÊM/GỠ Pod khỏi Service Endpoints** (KHÔNG restart container).
- Cấu hình **`SecurityContext`** ở cả 2 cấp độ: Pod-level và Container-level (`runAsUser`, `runAsNonRoot`, `readOnlyRootFilesystem`, Linux `capabilities: [add/drop]`, `allowPrivilegeEscalation: false`).
- Nắm vững chuẩn bảo mật hiện đại **Pod Security Standards (PSS)** và **Pod Security Admission (PSA)** với 3 profile: `privileged`, `baseline`, `restricted` (thay thế PodSecurityPolicy cũ).

---

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — ConfigMap & Secret Management (~3h)

#### 1. Các phương pháp tạo ConfigMap & Secret nhanh bằng CLI
```bash
# 1. Tạo ConfigMap từ biến literal
kubectl create configmap app-config --from-literal=APP_ENV=prod --from-literal=MAX_CONNECTIONS=100

# 2. Tạo ConfigMap từ file cấu hình có sẵn
kubectl create configmap nginx-cfg --from-file=/etc/nginx/nginx.conf

# 3. Tạo Secret thông thường (Opaque)
kubectl create secret generic db-secret --from-literal=DB_PASS=SuperSecret123!

# 4. Tạo TLS Secret cho Ingress (chứa cert và key)
kubectl create secret tls my-tls-cert --cert=tls.crt --key=tls.key

# 5. Tạo Docker Registry Secret để kéo image từ private repo
kubectl create secret docker-registry my-registry-key \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=myuser \
  --docker-password=mypass \
  --docker-email=user@example.com
```

#### 2. Cách Inject vào Pod: Biến môi trường vs Volume Mount
- **`envFrom`**: Nhúng toàn bộ các key-value trong ConfigMap/Secret thành biến môi trường trong 1 dòng.
- **`valueFrom.configMapKeyRef`**: Nhúng chọn lọc 1 key cụ thể.
- **`Volume Mount`**: Mount toàn bộ key thành các file nằm trong thư mục (mỗi key là tên file, value là nội dung file). **Ưu điểm lớn:** Khi sửa ConfigMap, các file trong volume sẽ **tự động cập nhật nội dung** sau vài giây mà không cần restart Pod (trong khi biến môi trường đòi hỏi phải restart Pod mới nhận giá trị mới).

---

### 🅱️ Buổi B — Health Probes: Liveness, Readiness & Startup (~3.5h)

```text
               +------------------------------------+
               |           Container Start          |
               +------------------------------------+
                                 |
                                 v
               +------------------------------------+
               |            StartupProbe            |
               |  (Kiểm tra xem app đã lên chưa?)   |
               +------------------------------------+
                   /                            \
              [Fail > Thres]                [Success]
                  /                                \
                 v                                  v
         KILLED & RESTARTED             +-----------------------+
                                        |  Bắt đầu chạy song    |
                                        |   song 2 Probes sau:  |
                                        +-----------------------+
                                           /                 \
                                          /                   \
                                         v                     v
                             +--------------------+   +--------------------+
                             |   LivenessProbe    |   |   ReadinessProbe   |
                             | (App còn sống ko?) |   | (App nhận tải ko?) |
                             +--------------------+   +--------------------+
                                       |                        |
                                    [Fail]                   [Fail]
                                       |                        |
                                       v                        v
                                 RESTART CONTAINER       REMOVE POD FROM
                                                         SERVICE ENDPOINTS
```

- **3 cơ chế kiểm tra (Probe Mechanisms):**
  1. `httpGet`: Gửi HTTP GET request tới path (ví dụ: `/healthz` cổng 8080). Thành công khi HTTP Code nằm trong khoảng `200–399`.
  2. `tcpSocket`: Kiểm tra xem cổng TCP có đang mở và kết nối được không (ví dụ kiểm tra cổng DB 5432).
  3. `exec`: Chạy một câu lệnh Linux bên trong container (ví dụ: `cat /tmp/healthy`). Thành công khi Exit Code bằng `0`.

---

### 🅲 Buổi C — SecurityContext & Pod Security Standards (PSA) (~2.5h)

#### 1. SecurityContext Best Practices
Chạy container với quyền root (`UID 0`) là lỗ hổng bảo mật nghiêm trọng. K8s cung cấp `securityContext` để hạn chế tối đa đặc quyền:
```yaml
spec:
  securityContext: # Pod-level (áp dụng cho toàn bộ container)
    runAsNonRoot: true
    runAsUser: 10001
    fsGroup: 2000
  containers:
  - name: secure-app
    image: nginx:alpine
    securityContext: # Container-level (ghi đè hoặc bổ sung đặc quyền riêng)
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
        add: ["NET_BIND_SERVICE"]
```

#### 2. Pod Security Admission (PSA)
Áp dụng bảo mật thông qua nhãn (labels) trên Namespace với 3 chế độ (`enforce`, `audit`, `warn`):
```bash
# Bắt buộc namespace 'production' phải tuân thủ chuẩn Restricted:
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest
```
Nếu một Pod cố tình chạy dưới quyền root hoặc yêu cầu `privileged: true`, API server sẽ từ chối tạo Pod ngay tại cửa!

---

### 🅳 Buổi D — Practice & Review (~2h)

- Tự tay hoàn thành bài lab trong [labs.md](labs.md): Viết Pod có đủ 3 Probes, cấu hình Secret nhúng vào Volume, và test PSA `restricted`.

---

## 🚪 Cổng tự kiểm tra Tuần 4 (Self-check Gate)

1. [ ] Nếu `ReadinessProbe` thất bại thì Kubelet có restart container không? *(Đáp án: KHÔNG. Nó chỉ tạm thời gỡ Pod IP khỏi danh sách Endpoints của Service để không nhận traffic nữa).*
2. [ ] StartupProbe sinh ra để giải quyết bài toán gì? *(Đáp án: Dành cho các ứng dụng khởi động chậm (như Java/Spring Boot mất vài phút load context). StartupProbe vô hiệu hoá Liveness/Readiness probe cho đến khi app khởi động xong, tránh bị Liveness probe kill oan).*
3. [ ] Khi nào một file mounted từ ConfigMap vào container tự động cập nhật nội dung? *(Đáp án: Khi ConfigMap được mount dưới dạng Volume, kubelet sẽ định kỳ sync nội dung mới vào file).*
4. [ ] Cờ `readOnlyRootFilesystem: true` có tác dụng gì? *(Đáp án: Khoá toàn bộ hệ thống file gốc của container thành chỉ đọc, chống mã độc ghi file hoặc sửa đổi binary).*
