# 🟩 Tuần 4 — Configuration, Probes, SecurityContext, PSS & Kustomize/Helm

> **Domain:** Workloads & Scheduling (15%) + Cluster Architecture (25%) · **Thời lượng:** ~13h (5 buổi) · **Vị trí:** Tuần 4/10
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
- 🆕 Sử dụng **Kustomize** (`kubectl apply -k`, base/overlays, patches, generators) và **Helm** (repo, chart, release, values, upgrade/rollback) để **cài đặt và cấu hình cluster components** — competency bắt buộc theo curriculum CKA từ 02/2025.

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

### 🧩 Buổi C+ — Kustomize & Helm: Đóng gói và cài đặt Cluster Components (~2h)

> 🆕 **Bổ sung theo curriculum CKA cập nhật 18/02/2025.** CNCF đã đưa hẳn một competency vào Domain *Cluster Architecture, Installation & Configuration (25%)*:
> **"Use Helm and Kustomize to install cluster components"**. Đây là nội dung **chắc chắn có thể ra thi**, và `helm.sh/docs` cũng đã được thêm vào danh sách tài liệu được mở trong phòng thi.

#### 1. Kustomize — "Overlay" không cần template (đã tích hợp sẵn trong `kubectl`)

Kustomize **không dùng template, không có biến `{{ }}`**. Nó lấy YAML thuần rồi *đắp chồng* các thay đổi lên. Điểm mạnh: file base vẫn là YAML hợp lệ, apply thẳng được.

Cấu trúc chuẩn base + overlays:

```text
app/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   └── service.yaml
└── overlays/
    ├── staging/
    │   └── kustomization.yaml
    └── production/
        ├── kustomization.yaml
        └── replica-patch.yaml
```

`base/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
```

`overlays/production/kustomization.yaml`:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: production           # Ép toàn bộ resource vào namespace này
namePrefix: prod-               # prod-web-app
labels:                         # Thay cho commonLabels đã deprecated
  - pairs:
      env: production
    includeSelectors: true
resources:
  - ../../base
images:                         # Đổi image tag mà KHÔNG cần sửa file base
  - name: nginx
    newTag: 1.27-alpine
replicas:                       # Đổi số replicas không cần viết patch
  - name: web-app
    count: 5
patches:                        # Strategic merge patch cho thay đổi phức tạp
  - path: replica-patch.yaml
configMapGenerator:             # Sinh ConfigMap kèm hash-suffix -> tự rollout khi đổi config
  - name: app-settings
    literals:
      - LOG_LEVEL=warn
```

Bộ lệnh phải thuộc:
```bash
# 1. XEM TRƯỚC kết quả render (KHÔNG apply) — luôn chạy bước này trước
kubectl kustomize overlays/production/

# 2. Apply thẳng thư mục kustomize
kubectl apply -k overlays/production/

# 3. Xoá những gì kustomization đã tạo
kubectl delete -k overlays/production/

# 4. Render ra file để nộp bài / soi diff
kubectl kustomize overlays/production/ > rendered.yaml
```

> ⚠️ **Bẫy 1:** `configMapGenerator` mặc định gắn **hash-suffix** vào tên (`app-settings-9f8h2k5t7c`). Đây là tính năng (đổi config → tên đổi → Deployment tự rolling restart), nhưng nếu đề bài yêu cầu ConfigMap tên **chính xác** `app-settings` thì phải tắt:
> ```yaml
> generatorOptions:
>   disableNameSuffixHash: true
> ```
>
> ⚠️ **Bẫy 2:** `commonLabels` đã **deprecated**, thay bằng khối `labels:` với `includeSelectors`. Dùng `commonLabels` vẫn chạy nhưng sẽ in cảnh báo.
>
> ⚠️ **Bẫy 3:** `namePrefix`/`nameSuffix` đổi tên resource → mọi tham chiếu chéo (Service selector, `claimName`, `configMapRef`) đều được Kustomize tự sửa theo, nhưng **chuỗi tên nằm trong `args`/`env` value thì KHÔNG** — phải tự patch.

#### 2. Helm — Package manager cho Kubernetes

| Khái niệm | Nghĩa |
|---|---|
| **Chart** | Gói phần mềm (thư mục chứa `Chart.yaml`, `values.yaml`, `templates/`, `charts/`) |
| **Release** | Một lần cài đặt chart vào cluster, có **tên** và **số revision** |
| **Repository** | Kho chứa chart đã đóng gói (`.tgz`) + `index.yaml` |
| **Values** | Tham số cấu hình, override chart mặc định bằng `--set` hoặc `-f` |

Bộ lệnh phải thuộc cho phòng thi:
```bash
# 1. Thêm repo và cập nhật index
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm repo list

# 2. Tìm chart
helm search repo nginx
helm search repo bitnami/nginx --versions      # Liệt kê mọi version của chart

# 3. XEM values mặc định TRƯỚC KHI cài (cực hay ra thi)
helm show values bitnami/nginx
helm show values bitnami/nginx > values.yaml
helm show chart bitnami/nginx                  # Metadata: version, appVersion

# 4. Render template ra YAML mà KHÔNG cài (dry-run offline)
helm template my-release bitnami/nginx --set replicaCount=3

# 5. Cài đặt
helm install my-nginx bitnami/nginx \
  --namespace web --create-namespace \
  --set replicaCount=3 \
  --set service.type=NodePort
# Hoặc dùng file values:
helm install my-nginx bitnami/nginx -n web -f values.yaml

# 6. Liệt kê release
helm list                 # Chỉ namespace hiện tại
helm list -A              # TOÀN BỘ namespace  <-- hay bị quên
helm list -n web

# 7. Nâng cấp & hoàn tác
helm upgrade my-nginx bitnami/nginx -n web --set replicaCount=5
helm upgrade --install my-nginx bitnami/nginx -n web   # Cài nếu chưa có, nâng cấp nếu đã có
helm history my-nginx -n web
helm rollback my-nginx 1 -n web

# 8. Kiểm tra cấu hình một release đang chạy
helm get values my-nginx -n web            # Chỉ những value đã override
helm get values my-nginx -n web -a         # TẤT CẢ values (kể cả mặc định)
helm get manifest my-nginx -n web          # YAML thực tế đã apply

# 9. Gỡ bỏ
helm uninstall my-nginx -n web
```

> ⚠️ **Bẫy 4:** `helm list` **chỉ hiện release trong namespace hiện tại**. Đề bài hỏi "có bao nhiêu release trong cluster" mà bạn quên `-A` là mất điểm ngay.
>
> ⚠️ **Bẫy 5:** `--set` với giá trị có dấu chấm hoặc dấu phẩy phải escape: `--set 'ingress.hosts[0].host=app.example.com'`, `--set "nodeSelector.kubernetes\.io/os=linux"`.
>
> ⚠️ **Bẫy 6:** Đề yêu cầu "cài chart nhưng **chưa** được apply vào cluster, chỉ xuất YAML" → dùng `helm template`, **không** dùng `helm install --dry-run` (dry-run vẫn cần kết nối API server và validate).

#### 3. Chọn cái nào? Bảng phản xạ

| Tình huống trong đề bài | Công cụ |
|---|---|
| "Install this chart / add this repo / upgrade the release" | **Helm** |
| "Set the replica count to N for the `production` overlay" | **Kustomize** |
| "Render the manifests without applying them" | `helm template` hoặc `kubectl kustomize` |
| "Roll back the component to the previous revision" | `helm rollback` (Kustomize không có khái niệm revision) |
| "Patch an existing manifest per environment without duplicating YAML" | **Kustomize** |
| "Install a cluster component (ingress controller, CNI, metrics-server)" | Thường là **Helm** |

> 🧠 **Mẹo ghi nhớ:** **Helm = `apt install`** (package manager, có version, rollback được).
> **Kustomize = `patch`** (đắp vá YAML sẵn có theo từng môi trường, đã nằm sẵn trong `kubectl -k`).

---

### 🅳 Buổi D — Practice & Review (~2h)

- Tự tay hoàn thành bài lab trong [labs.md](labs.md): Viết Pod có đủ 3 Probes, cấu hình Secret nhúng vào Volume, test PSA `restricted`, và dựng bộ **Kustomize base/overlays + cài một chart bằng Helm**.

---

## 🚪 Cổng tự kiểm tra Tuần 4 (Self-check Gate)

1. [ ] Nếu `ReadinessProbe` thất bại thì Kubelet có restart container không? *(Đáp án: KHÔNG. Nó chỉ tạm thời gỡ Pod IP khỏi danh sách Endpoints của Service để không nhận traffic nữa).*
2. [ ] StartupProbe sinh ra để giải quyết bài toán gì? *(Đáp án: Dành cho các ứng dụng khởi động chậm (như Java/Spring Boot mất vài phút load context). StartupProbe vô hiệu hoá Liveness/Readiness probe cho đến khi app khởi động xong, tránh bị Liveness probe kill oan).*
3. [ ] Khi nào một file mounted từ ConfigMap vào container tự động cập nhật nội dung? *(Đáp án: Khi ConfigMap được mount dưới dạng Volume, kubelet sẽ định kỳ sync nội dung mới vào file).*
4. [ ] Cờ `readOnlyRootFilesystem: true` có tác dụng gì? *(Đáp án: Khoá toàn bộ hệ thống file gốc của container thành chỉ đọc, chống mã độc ghi file hoặc sửa đổi binary).*
5. [ ] Kustomize và Helm khác nhau ở điểm cốt lõi nào? *(Đáp án: Helm dùng **template engine** (`{{ .Values.x }}`) + quản lý **release có version/rollback**; Kustomize **không có template**, chỉ đắp overlay/patch lên YAML thuần và đã tích hợp sẵn trong `kubectl -k`).*
6. [ ] Làm sao xem toàn bộ values (kể cả mặc định) của một release đang chạy? *(Đáp án: `helm get values <release> -n <ns> -a`. Bỏ cờ `-a` thì chỉ thấy phần bạn override).*
7. [ ] Vì sao `configMapGenerator` lại thêm hậu tố băm vào tên ConfigMap, và tắt nó thế nào? *(Đáp án: Hash thay đổi khi nội dung đổi → tên ConfigMap đổi → Deployment tham chiếu tới nó tự động rolling restart. Tắt bằng `generatorOptions.disableNameSuffixHash: true`).*
8. [ ] Đề yêu cầu xuất manifest của một chart ra file mà tuyệt đối không được chạm vào cluster — dùng lệnh gì? *(Đáp án: `helm template <name> <chart> [-f values.yaml] > out.yaml`. Không dùng `helm install --dry-run` vì nó vẫn gọi API server).*
