# 🟦 Tuần 1 — Kiến trúc Kubernetes & Control Plane + Lab Multi-node + `kubectl` Imperative Pro

> **Domain:** Cluster Architecture, Installation & Configuration (25%) · **Thời lượng:** ~12.5h (5 buổi) · **Vị trí:** Tuần 1/10
>
> **Điều hướng:** [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [Tuần 2 ➡️](../week-02/README.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Phân tích chi tiết và vẽ lại được **luồng dữ liệu của một API Request** trong Kubernetes từ lúc người dùng gõ `kubectl run` đến khi container thực sự chạy trên Worker Node.
- Giải thích được vai trò và cơ chế mTLS của **4 thành phần Control Plane** (`kube-apiserver`, `etcd`, `kube-controller-manager`, `kube-scheduler`) và **2 thành phần Worker Node** (`kubelet`, `kube-proxy`).
- Tự tay dựng được một **cụm Kubernetes Multi-node local (1 Control Plane + 2 Workers)** bằng `Kind` hoặc `Minikube` trên máy tính cá nhân.
- Thuần thục **kỹ năng phòng thi CKA**: Thiết lập alias `k=kubectl`, Bash Autocompletion, biến export `$do` và `$now`, tối ưu `.vimrc` cho việc thụt lề YAML 2-space.
- Tạo được Pod, Multi-container Pod (gồm Init Container và Native Sidecar K8s 1.28+) bằng lệnh **Imperative trong vòng 5 giây** với `--dry-run=client -o yaml`.
- Nắm vững **Pod Lifecycle & Phases** (`Pending`, `Running`, `Succeeded`, `Failed`, `Unknown`) và các nguyên nhân gây ra từng trạng thái.

---

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Lý thuyết kiến trúc (~3h)

#### 1. Bức tranh toàn cảnh kiến trúc Kubernetes (Architecture Deep-dive)

Kubernetes tuân theo mô hình **Master-Worker (Control Plane - Data Plane)**:

```text
+-----------------------------------------------------------------------+
|                             CONTROL PLANE                             |
|                                                                       |
|  +--------------------+        +-------------------+                  |
|  |   kube-scheduler   |<------>|  kube-apiserver   |<---- kubectl     |
|  +--------------------+        +-------------------+                  |
|                                     ^         ^                       |
|  +--------------------+             |         |                       |
|  | kube-controller-   |<------------+         v                       |
|  |      manager       |              +-----------------+              |
|  +--------------------+              |      etcd       |              |
|                                      +-----------------+              |
+-----------------------------------------------------------------------+
                                      |
                     mTLS (giao tiếp mã hoá 2 chiều qua PKI)
                                      |
+-------------------------------------+---------------------------------+
| WORKER NODE 1                       | WORKER NODE 2                   |
|  +---------------+  +------------+  |  +---------------+  +------------+
|  |    kubelet    |  | kube-proxy |  |  |    kubelet    |  | kube-proxy |
|  +---------------+  +------------+  |  +---------------+  +------------+
|         |                           |         |                       |
|         v (CRI - unix socket)       |         v (CRI)                 |
|  +---------------+                  |  +---------------+              |
|  |  containerd   |                  |  |  containerd   |              |
|  +---------------+                  |  +---------------+              |
|         |                           |         |                       |
|         v                           |         v                       |
|  [ Pod A ]  [ Pod B ]               |  [ Pod C ]  [ Pod D ]           |
+-------------------------------------+---------------------------------+
```

- **`kube-apiserver` (Cổng giao tiếp duy nhất):**
  - Mọi thao tác từ `kubectl`, từ các controller nội bộ, hay từ `kubelet` đều phải đi qua API Server qua cổng HTTPS 6443.
  - Các thành phần khác **không bao giờ nói chuyện trực tiếp với nhau** (Scheduler không gọi Kubelet; Controller-manager không ghi trực tiếp vào etcd).
  - Nhiệm vụ: Xác thực danh tính (Authentication) -> Kiểm tra quyền hạn (Authorization via RBAC) -> Kích hoạt Admission Controllers -> Đọc/Ghi dữ liệu vào etcd.
- **`etcd` (Trái tim lưu trữ trạng thái):**
  - Cơ sở dữ liệu phân tán dạng Key-Value lưu toàn bộ trạng thái mong muốn (Desired State) và thực tế của cụm.
  - Dùng thuật toán đồng thuận Raft. Chỉ API Server có quyền đọc/ghi vào etcd.
- **`kube-scheduler` (Người phân công công việc):**
  - Lắng nghe sự kiện từ API Server để tìm các Pod mới tạo có trường `nodeName` rỗng.
  - Chạy 2 thuật toán:
    1. **Filtering (Predicates):** Lọc bỏ các Node không đủ điều kiện (hết RAM/CPU, dính Taint mà Pod không có Toleration, sai NodeSelector).
    2. **Scoring (Priorities):** Chấm điểm các Node còn lại dựa trên độ phân tán (PodAntiAffinity), độ cân bằng tài nguyên, và chọn Node có điểm cao nhất.
    3. Gửi lệnh Bind (gán `nodeName`) về API Server.
- **`kube-controller-manager` (Vòng lặp tự phục hồi):**
  - Tập hợp hàng loạt Controller nhỏ chạy trong 1 tiến trình: Node Lifecycle Controller, ReplicaSet Controller, EndpointSlice Controller, ServiceAccount Controller...
  - Nguyên lý hoạt động: So sánh liên tục `Desired State` (trong etcd) và `Current State` (thực tế). Nếu lệch (ví dụ 1 Pod bị chết) -> yêu cầu API server tạo Pod mới để bù lại.
- **`kubelet` (Đội trưởng trên Worker Node):**
  - Chạy dưới dạng Systemd service trên hệ điều hành của Node.
  - Nhận PodSpec từ API Server, gọi Container Runtime (`containerd`) qua giao thức **CRI** (Container Runtime Interface) để pull image và start container.
  - Kiểm tra Liveness/Readiness Probes, báo cáo metrics và trạng thái Node về API Server.
- **`kube-proxy` (Cảnh sát giao thông mạng):**
  - Chạy trên từng Node, theo dõi các Service và Endpoints.
  - Cập nhật bảng `iptables` hoặc `IPVS` của Linux Kernel để định tuyến gói tin gửi tới ClusterIP sang các Pod IP thực tế.

#### 2. Vòng đời của một câu lệnh: `kubectl run nginx --image=nginx`

1. **Client:** `kubectl` đọc kubeconfig (`~/.kube/config`), lấy token/client-cert và gửi HTTP POST request `api/v1/namespaces/default/pods` lên `kube-apiserver`.
2. **API Server:**
   - Authenticate client -> Authorize xem có quyền tạo Pod không -> Chạy Mutating/Validating Admission Controllers.
   - Ghi Pod metadata vào `etcd` với trạng thái `Pending` (`nodeName` đang để trống). Trả về response 201 Created cho client.
3. **Scheduler:** Vòng lặp watch của Scheduler phát hiện Pod chưa có `nodeName`. Scheduler chạy thuật toán lọc và chấm điểm, chọn ra `node-01`. Scheduler gửi request `Binding` gán `nodeName: node-01` về API Server.
4. **API Server:** Cập nhật `nodeName: node-01` vào `etcd`.
5. **Kubelet trên node-01:** Vòng lặp watch của Kubelet thấy có Pod được gán cho chính nó. Kubelet gọi `containerd` qua CRI socket để tải image `nginx` và khởi chạy container. Đồng thời Kubelet gọi CNI plugin để cấp phát IP nội bộ cho Pod.
6. **Kubelet:** Cập nhật trạng thái Pod `Running` và Pod IP về API Server để ghi vào `etcd`.

---

### 🅱️ Buổi B — Hands-on Cấu hình Môi trường & Imperative CLI (~3.5h)

> 🧪 **Thực hành chi tiết từng bước:** Xem file [labs.md](labs.md).

**Nội dung cốt lõi cần đạt được trong buổi này:**
1. Cài đặt Docker, Kubectl và Kind trên máy.
2. Dựng cụm 3 node bằng Kind với file manifest `kind-3nodes.yaml`.
3. Cấu hình `.bashrc` / `.zshrc`:
   ```bash
   alias k=kubectl
   complete -o default -F __start_kubectl k
   export do="--dry-run=client -o yaml"
   export now="--force --grace-period=0"
   ```
4. Cấu hình `.vimrc`:
   ```vim
   set tabstop=2
   set shiftwidth=2
   set expandtab
   set number
   set paste
   ```
5. Luyện tốc độ sinh YAML không cần tra cứu:
   - Tạo Pod Nginx: `k run nginx --image=nginx $do > pod.yaml`
   - Tạo Pod Nginx có gán port 80 và biến môi trường: `k run nginx --image=nginx --port=80 --env="ENV=prod" $do > pod.yaml`
   - Tạo Deployment: `k create deploy web-dep --image=nginx --replicas=3 $do > dep.yaml`
   - Expose Deployment: `k expose deploy web-dep --port=80 --target-port=80 --type=ClusterIP $do > svc.yaml`

---

### 🅲 Buổi C — Pod Lifecycle, Init Containers & Native Sidecars (~2.5h)

#### 1. Các trạng thái (Phases) của Pod
- **`Pending`**: Pod đã được API server chấp nhận và lưu vào etcd, nhưng chưa chạy được (có thể đang chờ Scheduler xếp Node, hoặc Node đang kéo Image).
- **`Running`**: Pod đã được gán vào Node và ít nhất 1 container đã được khởi chạy thành công hoặc đang chạy/restart.
- **`Succeeded`**: Tất cả container trong Pod đã kết thúc thành công (Exit Code 0) và sẽ không restart lại (thường gặp trong `Job`).
- **`Failed`**: Tất cả container đã kết thúc, và có ít nhất 1 container kết thúc thất bại (Exit Code khác 0).
- **`CrashLoopBackOff`**: Container khởi động thất bại hoặc bị crash ngay sau khi start, Kubelet cố gắng restart lại nhưng áp dụng thuật toán exponential backoff delay (10s, 20s, 40s... tối đa 5 phút).

#### 2. Init Containers vs Native Sidecars (K8s 1.28+ / 1.29+ GA)
- **`initContainers` truyền thống:**
  - Chạy theo thứ tự tuần tự (Sequential).
  - Phải kết thúc thành công (`Exit Code 0`) thì container chính (`containers[]`) mới bắt đầu được khởi động.
  - Nếu init container thất bại -> Pod bị restart liên tục trừ khi `restartPolicy: Never`.
  - Ứng dụng: Chờ cơ sở dữ liệu sẵn sàng (ping DB), tải dữ liệu ban đầu, cấp quyền cho thư mục.
- **`Native Sidecar Containers` (Tính năng hiện đại):**
  - Khai báo trong danh sách `initContainers[]` NHƯNG có thêm cờ: **`restartPolicy: Always`**.
  - **Hành vi:** Kubelet khởi động sidecar này trước, chờ đến khi nó đạt trạng thái `Ready`, sau đó NGAY LẬP TỨC khởi động container chính mà KHÔNG CHỜ sidecar kết thúc!
  - Sidecar chạy song song suốt vòng đời của Pod.
  - Khi container chính chạy xong (trong K8s Job), Kubelet sẽ **tự động gửi tín hiệu SIGTERM để tắt sidecar**, giải quyết triệt để vấn đề Pod Job bị treo không bao giờ Succeeded vì sidecar logging/proxy.

Ví dụ Manifest chuẩn:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-native-sidecar
spec:
  initContainers:
  - name: log-shipper-sidecar
    image: busybox:1.28
    restartPolicy: Always # <-- BIẾN CONTAINER NÀY THÀNH NATIVE SIDECAR
    command: ['sh', '-c', 'tail -F /var/log/app.log']
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log
  containers:
  - name: main-app
    image: busybox:1.28
    command: ['sh', '-c', 'for i in $(seq 1 10); do echo "Log $i" >> /var/log/app.log; sleep 1; done']
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log
  volumes:
  - name: shared-logs
    emptyDir: {}
```

---

### 🔌 Buổi C+ — Extension Interfaces: CRI, CNI, CSI & Device Plugins (~1.5h)

> 🆕 **Bổ sung theo curriculum CKA cập nhật 18/02/2025** — competency *"Understand extension interfaces (CNI, CSI, CRI, etc.)"* nằm trong Domain *Cluster Architecture (25%)*.

Kubernetes cố tình **không** tự cài cắm runtime, mạng hay storage. Nó định nghĩa **hợp đồng (interface)** rồi để nhà cung cấp bên ngoài cắm vào. Hiểu được "ai cắm vào đâu" chính là chìa khoá troubleshooting: khi Pod không lên được, câu hỏi đầu tiên luôn là *hỏng ở interface nào?*

| Interface | Ai gọi nó? | Cắm vào để làm gì | Triệu chứng khi hỏng |
|---|---|---|---|
| **CRI** (Container Runtime Interface) | `kubelet` | Tạo/xoá/chạy container (`containerd`, `CRI-O`) | Node `NotReady`, Pod kẹt `ContainerCreating`, `kubelet` log báo lỗi gọi runtime |
| **CNI** (Container Network Interface) | `kubelet` (qua runtime) | Cấp IP cho Pod, đấu veth vào bridge/overlay (`Calico`, `Cilium`, `Flannel`) | Pod kẹt `ContainerCreating` với event `failed to setup network`, node `NotReady` kèm `cni plugin not initialized` |
| **CSI** (Container Storage Interface) | `kube-controller-manager` + `kubelet` | Provision / attach / mount volume (`ebs.csi.aws.com`, `nfs.csi.k8s.io`) | PVC kẹt `Pending`, Pod kẹt `ContainerCreating` với lỗi `FailedAttachVolume` / `FailedMount` |
| **Device Plugin** | `kubelet` | Expose tài nguyên phần cứng đặc biệt (GPU, FPGA, hugepages) | Pod `Pending` vì `Insufficient nvidia.com/gpu` |
| **CCM** (Cloud Controller Manager) | Control plane | Tích hợp LoadBalancer / Node / Route của cloud | Service `LoadBalancer` kẹt `<pending>` mãi |

#### 1. CRI — nơi kubelet nói chuyện với runtime

```bash
# Runtime nào đang chạy, version bao nhiêu?
kubectl get nodes -o wide          # Cột CONTAINER-RUNTIME
crictl version
crictl info | head -20

# Socket mặc định
#   containerd : unix:///run/containerd/containerd.sock
#   CRI-O      : unix:///var/run/crio/crio.sock

# Cấu hình endpoint cho crictl (tránh cảnh báo deprecated mỗi lần gõ)
cat << 'EOF' > /etc/crictl.yaml
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
EOF
```

> ⚠️ **Bẫy kinh điển:** Kubelet và containerd phải **cùng** cgroup driver (`systemd`). Lệch nhau → kubelet không khởi động được.
> Kubelet: `/var/lib/kubelet/config.yaml` → `cgroupDriver: systemd`
> containerd: `/etc/containerd/config.toml` → `SystemdCgroup = true`

#### 2. CNI — nơi Pod nhận IP

```bash
# Danh sách cấu hình CNI mà kubelet sẽ đọc (file có thứ tự alphabet nhỏ nhất thắng)
ls -l /etc/cni/net.d/

# Các binary plugin thực thi
ls -l /opt/cni/bin/

# Pod của CNI (thường chạy dạng DaemonSet trên mọi node)
kubectl get pods -n kube-system -o wide | grep -Ei 'calico|cilium|flannel|weave'
```

Luồng cấp IP cho một Pod: `kubelet` → runtime (CRI) → gọi **CNI plugin** với `ADD` → plugin tạo veth pair, gắn vào bridge/overlay, xin IP từ **IPAM** → trả IP về → `kubelet` ghi `podIP` vào status.

> 🧠 **Ghi nhớ để troubleshoot:** Node `NotReady` mà log kubelet báo `Network plugin returns error: cni plugin not initialized` → **CNI chưa cài hoặc DaemonSet CNI đang chết**, không phải lỗi kubelet.
>
> ⚠️ **NetworkPolicy chỉ có tác dụng khi CNI hỗ trợ.** Calico/Cilium có; **Flannel thuần thì KHÔNG** — bạn apply NetworkPolicy, API server nhận, nhưng không có gì thực thi cả. Đây là bẫy đề rất hay gặp.

#### 3. CSI — nơi volume được cấp phát và gắn vào

Mỗi CSI driver triển khai 2 thành phần:
- **Controller plugin** (Deployment/StatefulSet trên control plane): `CreateVolume`, `DeleteVolume`, `ControllerPublishVolume` (attach).
- **Node plugin** (DaemonSet trên mọi node): `NodeStageVolume`, `NodePublishVolume` (mount vào Pod).

```bash
# Driver nào đã đăng ký với cluster?
kubectl get csidrivers
kubectl get csinodes
kubectl get storageclass           # Cột PROVISIONER chính là tên CSI driver

# Chuỗi truy vết khi PVC treo
kubectl describe pvc <pvc>         # Xem Events: có provisioner nhận không?
kubectl get volumeattachments
kubectl get pods -n kube-system | grep csi
```

> 🧠 **Ghi nhớ:** `StorageClass.provisioner` = **tên CSI driver**. PVC `Pending` mãi mà `describe` không thấy event nào từ provisioner → driver chưa cài, hoặc `storageClassName` gõ sai.

---

### 🅳 Buổi D — Practice Questions & Cổng tự kiểm tra (~2h)

- Hoàn thành bộ 20 câu hỏi luyện tập trong file [questions.md](questions.md).
- Tự làm bài không nhìn đáp án trong 40 phút.
- Đối chiếu với [answers.md](answers.md), ghi nhận lại các câu sai vào sổ tay học tập cá nhân.

---

## 🚪 Cổng tự kiểm tra Tuần 1 (Self-check Gate)

> ⚠️ **KHÔNG chuyển sang Tuần 2 nếu chưa trả lời trôi chảy các câu hỏi dưới đây:**

1. [ ] Nếu `etcd` bị sập, các Pod hiện tại trên Worker Node có tiếp tục chạy và phục vụ traffic không? Tại sao? *(Đáp án: Có. Các Pod vẫn chạy bình thường trên containerd và kube-proxy vẫn giữ iptables rules. Tuy nhiên không thể tạo mới, cập nhật, hoặc tự phục hồi nếu Pod bị chết).*
2. [ ] Thành phần nào trong cụm K8s giao tiếp trực tiếp với Container Runtime qua CRI? *(Đáp án: Duy nhất `kubelet`).*
3. [ ] Viết câu lệnh tạo Pod `redis` thuộc namespace `cache`, image `redis:alpine`, gán nhãn `tier=db` và xuất ra file `redis.yaml` mà không thực sự tạo Pod?
   *(Đáp án: `kubectl run redis --image=redis:alpine --namespace=cache --labels="tier=db" --dry-run=client -o yaml > redis.yaml`)*.
4. [ ] Khác biệt giữa Static Pod và Pod thông thường là gì? Static Pod do thành phần nào quản lý? *(Đáp án: Static Pod do Kubelet trên node đọc trực tiếp từ thư mục manifest địa phương `/etc/kubernetes/manifests/`, không qua API Server. Scheduler không thể lập lịch cho Static Pod).*
5. [ ] Native Sidecar container trong K8s 1.29+ được cấu hình như thế nào để phân biệt với Init Container thông thường? *(Đáp án: Khai báo trong `initContainers[]` kèm trường `restartPolicy: Always`).*
6. [ ] Kể tên 3 extension interface chính của Kubernetes và thành phần nào gọi chúng? *(Đáp án: **CRI** — kubelet gọi runtime (containerd/CRI-O); **CNI** — kubelet/runtime gọi plugin mạng để cấp IP cho Pod; **CSI** — controller-manager + kubelet gọi driver storage để provision/attach/mount volume).*
7. [ ] Pod kẹt ở `ContainerCreating` kèm event `failed to setup network for sandbox` — hỏng ở interface nào? *(Đáp án: **CNI**. Kiểm tra `/etc/cni/net.d/`, `/opt/cni/bin/`, và DaemonSet CNI trong `kube-system`).*
8. [ ] Vì sao apply NetworkPolicy trên cụm dùng Flannel thuần lại không có tác dụng gì? *(Đáp án: NetworkPolicy chỉ là **object khai báo**; việc thực thi do CNI plugin đảm nhiệm. Flannel thuần không implement NetworkPolicy — cần Calico hoặc Cilium).*

---

## ✅ Checklist Tuần 1

- [ ] Hiểu rõ vai trò của 4 thành phần Control Plane và 2 thành phần Worker Node.
- [ ] Dựng thành công cluster 3 nodes bằng Kind trên máy cá nhân.
- [ ] Cấu hình xong `.vimrc` và các alias `k`, `$do`, `$now` trên shell.
- [ ] Tự tay tạo được 5 Pod khác nhau bằng lệnh imperative dưới 30 giây.
- [ ] Viết thành công một Pod có chứa Init Container và một Pod có Native Sidecar container.
- [ ] Hoàn thành 100% bài lab trong [labs.md](labs.md).
- [ ] Làm bài test [questions.md](questions.md) đạt kết quả ≥ 85%.
