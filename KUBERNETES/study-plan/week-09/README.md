# 🛠️ Tuần 9 — Cluster Maintenance, Kubeadm Upgrade, etcd DR, HA Control Plane & CRD/Operators

> **Domain:** Cluster Architecture, Installation & Configuration (25%) · **Thời lượng:** ~14.5h (6 buổi) · **Vị trí:** Tuần 9/10
>
> **Điều hướng:** [⬅️ Tuần 8](../week-08/README.md) · [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [Tuần 10 ➡️](../week-10/README.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Làm chủ quy trình bảo trì Node: Phân biệt sự khác nhau giữa **`kubectl cordon`** (chặn xếp Pod mới) và **`kubectl drain`** (di dời Pod đang chạy một cách an toàn), cùng các cờ bắt buộc: `--ignore-daemonsets`, `--delete-emptydir-data`, `--force`.
- Thực hiện chuẩn xác quy trình **Nâng cấp Cluster bằng Kubeadm (Kubeadm Cluster Upgrade)** từ phiên bản `v1.34.x` lên `v1.35.x` theo đúng trình tự nghiêm ngặt (Control Plane trước, Worker Nodes sau; không được nhảy cóc minor version).
- Thành thạo 100% kịch bản **Backup & Restore etcd Database** bằng `etcdctl`:
  - Lưu file snapshot `.db` với các file chứng chỉ CA, cert, key chuẩn xác.
  - Khôi phục snapshot vào thư mục mới `--data-dir=/var/lib/etcd-restored`.
  - Cấu hình lại file Static Pod `/etc/kubernetes/manifests/etcd.yaml` để áp dụng dữ liệu đã khôi phục.
- Kiểm tra hạn sử dụng chứng chỉ của cụm bằng `kubeadm certs check-expiration` và gia hạn bằng `kubeadm certs renew`.

---

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Node Maintenance: Cordon, Drain & Uncordon (~3h)

Khi cần khởi động lại hoặc nâng cấp hệ điều hành của một Worker Node, tuyệt đối không được tắt node đột ngột! Phải thực hiện quy trình 3 bước:

```text
[ Node Active ]
      |
      v  kubectl cordon <node>
[ SchedulingDisabled ]  (Pod cũ vẫn chạy, Pod mới không được xếp vào)
      |
      v  kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
[ Node Drained ]        (Tất cả Pod di chuyển sang Node khác, trừ DaemonSet)
      |
      * (Thực hiện bảo trì phần cứng / reboot node / upgrade kernel) *
      |
      v  kubectl uncordon <node>
[ Node Active ]         (Node mở cửa trở lại nhận Pod mới)
```

#### Các cờ bắt buộc khi chạy `kubectl drain` trong phòng thi CKA:
1. `--ignore-daemonsets`: DaemonSet được quản lý để chạy trên mọi node. Nếu không có cờ này, lệnh `drain` sẽ từ chối chạy vì không thể đuổi DaemonSet!
2. `--delete-emptydir-data`: Nếu Pod có gắn volume `emptyDir`, việc đuổi Pod sẽ làm mất dữ liệu tạm thời đó. Cờ này xác nhận bạn đồng ý cho xoá dữ liệu `emptyDir`.
3. `--force`: Bắt buộc đuổi cả các Pod độc lập (Bare Pods) không được quản lý bởi ReplicaSet/Deployment.

---

### 🅱️ Buổi B — Kubeadm Cluster Upgrade Quy trình chuẩn (~3.5h)

> ⚠️ **Quy tắc vàng:** Chỉ nâng cấp từng minor version (ví dụ: `1.34 -> 1.35`). Tuyệt đối không được nhảy từ `1.33 -> 1.35`!

#### Bước 1: Nâng cấp Control Plane Node đầu tiên
```bash
# 1. Drain node control-plane
kubectl drain controlplane --ignore-daemonsets

# 2. Cập nhật apt repo và nâng cấp công cụ kubeadm
apt-mark unhold kubeadm
apt-get update && apt-get install -y kubeadm=1.35.0-1.1
apt-mark hold kubeadm

# 3. Kiểm tra kế hoạch nâng cấp
kubeadm upgrade plan

# 4. Áp dụng nâng cấp cho Control Plane
sudo kubeadm upgrade apply v1.35.0

# 5. Nâng cấp kubelet và kubectl trên node
apt-mark unhold kubelet kubectl
apt-get update && apt-get install -y kubelet=1.35.0-1.1 kubectl=1.35.0-1.1
apt-mark hold kubelet kubectl

# 6. Restart dịch vụ kubelet và uncordon node
sudo systemctl daemon-reload
sudo systemctl restart kubelet
kubectl uncordon controlplane
```

#### Bước 2: Nâng cấp lần lượt từng Worker Node
```bash
# 1. Trên máy quản trị (Control Plane): Drain worker node
kubectl drain node01 --ignore-daemonsets --delete-emptydir-data

# 2. SSH sang node01 và nâng cấp kubeadm:
apt-mark unhold kubeadm
apt-get update && apt-get install -y kubeadm=1.35.0-1.1
apt-mark hold kubeadm

# 3. Nâng cấp cấu hình node worker (KHÁC VỚI CONTROL PLANE):
sudo kubeadm upgrade node

# 4. Nâng cấp kubelet & kubectl:
apt-mark unhold kubelet kubectl
apt-get update && apt-get install -y kubelet=1.35.0-1.1 kubectl=1.35.0-1.1
apt-mark hold kubelet kubectl

# 5. Restart kubelet:
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# 6. Quay lại máy quản trị: Uncordon node
kubectl uncordon node01
```

---

### 🅲 Buổi C — etcd Backup & Disaster Recovery (~2.5h)

```text
1. SNAPSHOT BACKUP (Đọc trạng thái hiện tại lưu ra file)
   [ etcd DB: 2379 ] ---- etcdctl snapshot save ----> [ /opt/etcd-backup.db ]

2. RESTORE DISASTER (Khôi phục dữ liệu vào thư mục mới)
   [ /opt/etcd-backup.db ] ---- etcdctl snapshot restore ----> [ /var/lib/etcd-restored ]
                                                                        ^
3. REPOINT MANIFEST                                                     |
   Sửa /etc/kubernetes/manifests/etcd.yaml: trỏ hostPath vào ------------+
```

#### Cú pháp lệnh Backup 100% có trong đề CKA:
```bash
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /opt/snapshot-pre-upgrade.db
```

#### Cú pháp lệnh Restore:
```bash
ETCDCTL_API=3 etcdctl snapshot restore /opt/snapshot-pre-upgrade.db \
  --data-dir=/var/lib/etcd-restored
```
Sau đó mở `/etc/kubernetes/manifests/etcd.yaml`, tìm đoạn:
```yaml
  volumes:
  - hostPath:
      path: /var/lib/etcd-restored # <-- ĐỔI THÀNH THƯ MỤC MỚI
      type: DirectoryOrCreate
    name: etcd-data
```
Kubelet sẽ tự động phát hiện file YAML thay đổi và khởi động lại Pod `etcd` với dữ liệu vừa khôi phục.

---

### 🏛️ Buổi C+ — Highly-Available Control Plane (~2h)

> 🆕 **Bổ sung theo curriculum CKA cập nhật 18/02/2025** — competency *"Implement and configure a highly-available control plane"*, Domain *Cluster Architecture (25%)*.

#### 1. Hai kiểu tô-pô HA mà kubeadm hỗ trợ

| | **Stacked etcd** | **External etcd** |
|---|---|---|
| Vị trí etcd | Chạy **ngay trên** mỗi control plane node (static pod) | Cụm etcd **riêng biệt**, tách khỏi control plane |
| Số máy tối thiểu | 3 (3 CP node) | 6 (3 CP + 3 etcd) |
| Mất 1 node thì mất gì | Mất **cả** 1 CP **và** 1 thành viên etcd | Chỉ mất 1 CP, etcd không suy suyển |
| Độ phức tạp | Thấp — `kubeadm` lo hết | Cao — phải tự dựng và cấp cert cho cụm etcd |
| Mặc định của kubeadm | ✅ Có | Phải khai báo `external` trong cấu hình |

> 🧠 **Ghi nhớ:** `kubeadm` mặc định dựng **stacked etcd**. Đề bài nhắc tới "dedicated etcd cluster" / "external etcd endpoints" là đang nói tới tô-pô thứ hai.

#### 2. Quorum — con số sống còn

Cụm etcd dùng thuật toán đồng thuận **Raft**, cần **quá bán** thành viên còn sống mới ghi được:

```text
quorum = (N / 2) + 1        (làm tròn xuống ở phép chia)
```

| Số etcd member | Quorum cần | Chịu được mất | Nhận xét |
|---|---|---|---|
| **1** | 1 | **0** | Không HA |
| **2** | 2 | **0** | ❌ **Tệ hơn 1 node** — mất 1 là mất luôn quorum |
| **3** | 2 | **1** | ✅ Lựa chọn chuẩn cho production |
| **4** | 3 | **1** | ❌ Tốn thêm máy mà không tăng khả năng chịu lỗi |
| **5** | 3 | **2** | ✅ Dùng cho cụm lớn |

> ⚠️ **Vì sao luôn là số LẺ:** từ 3 lên 4 member, khả năng chịu lỗi **vẫn là 1**, nhưng xác suất có một node hỏng lại **cao hơn**. Số chẵn chỉ làm mọi thứ tệ đi.
>
> ⚠️ **Mất quorum thì sao:** etcd chuyển sang **read-only**, API server không ghi được gì. Pod đang chạy vẫn chạy, nhưng mọi thao tác tạo/sửa/xoá đều treo. Cách chữa: khôi phục đủ member, hoặc restore từ snapshot với `--force-new-cluster`.

#### 3. Dựng control plane HA bằng kubeadm

```bash
# --- Bước 1: Trên control plane node ĐẦU TIÊN ---
# --control-plane-endpoint TRỎ VÀO LOAD BALANCER, không phải IP của node
sudo kubeadm init \
  --control-plane-endpoint "k8s-api.example.com:6443" \
  --upload-certs \
  --pod-network-cidr=192.168.0.0/16

# --- Bước 2: Join các control plane node BỔ SUNG ---
# Lệnh này do bước 1 in ra; chú ý có THÊM --control-plane và --certificate-key
sudo kubeadm join k8s-api.example.com:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash> \
  --control-plane \
  --certificate-key <key>

# --- Bước 3: Join worker node (KHÔNG có --control-plane) ---
sudo kubeadm join k8s-api.example.com:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

Khi token/cert key đã hết hạn (mặc định 2 giờ với `--certificate-key`, 24 giờ với token):
```bash
# Sinh lại lệnh join cho worker
kubeadm token create --print-join-command

# Nạp lại certificate vào Secret và in ra certificate-key mới (cho CP node)
sudo kubeadm init phase upload-certs --upload-certs
```

> ⚠️ **`--control-plane-endpoint` là thứ KHÔNG SỬA ĐƯỢC về sau.** Nếu `kubeadm init` ban đầu trỏ thẳng vào IP một node, bạn **không thể** chuyển cụm đó sang HA mà không dựng lại. Luôn trỏ vào DNS/VIP của load balancer ngay từ đầu, kể cả khi mới có 1 CP node.

#### 4. Load balancer đứng trước API server

Cả 3 `kube-apiserver` đều **stateless** và active-active. Điều kiện: một L4 LB (HAProxy + keepalived VIP, hoặc NLB của cloud) phân phối TCP `:6443` tới cả ba.

```text
                 ┌──────────────────────────┐
  kubectl ─────► │  LB  k8s-api:6443 (VIP)  │
  kubelet  ────► └───┬──────────┬───────────┘
                     │          │          │
                 ┌───▼───┐  ┌───▼───┐  ┌───▼───┐
                 │ cp-1  │  │ cp-2  │  │ cp-3  │   apiserver (active-active)
                 │ etcd  │◄─┤ etcd  │─►│ etcd  │   Raft, quorum = 2/3
                 └───────┘  └───────┘  └───────┘
```

Lưu ý về tính chất từng thành phần khi chạy nhiều bản:
- **`kube-apiserver`**: **active-active** — cả 3 cùng phục vụ.
- **`kube-controller-manager`** và **`kube-scheduler`**: **active-passive** qua **leader election** (Lease object trong `kube-system`). Chỉ 1 bản làm việc thật, 2 bản còn lại chờ.

```bash
# Ai đang là leader?
kubectl get lease -n kube-system kube-scheduler kube-controller-manager
kubectl get lease -n kube-system kube-scheduler -o jsonpath='{.spec.holderIdentity}{"\n"}'

# Sức khoẻ cụm etcd
kubectl get pods -n kube-system -l component=etcd -o wide
sudo ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  --write-out=table member list

sudo etcdctl ... --write-out=table endpoint status --cluster   # Cột IS LEADER
sudo etcdctl ... endpoint health --cluster
```

---

### 🧬 Buổi C++ — CustomResourceDefinitions (CRD) & Operators (~1.5h)

> 🆕 **Bổ sung theo curriculum CKA cập nhật 18/02/2025** — competency *"Understand CRDs, install and configure operators"*, Domain *Cluster Architecture (25%)*.

#### 1. CRD — dạy cho API server một loại tài nguyên mới

CRD **mở rộng chính API của Kubernetes**: sau khi đăng ký, kind mới hoạt động y hệt Pod hay Deployment — `kubectl get`, RBAC, `kubectl explain`, watch, etcd storage, tất cả đều dùng được.

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.ops.example.com        # BẮT BUỘC đúng dạng <plural>.<group>
spec:
  group: ops.example.com
  scope: Namespaced                     # hoặc Cluster
  names:
    plural: backups
    singular: backup
    kind: Backup
    shortNames: [bk]
  versions:
    - name: v1
      served: true                      # API có phục vụ version này không
      storage: true                     # CHỈ MỘT version được đặt storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required: [schedule]
              properties:
                schedule:
                  type: string
                retention:
                  type: integer
                  minimum: 1
      additionalPrinterColumns:         # Thêm cột cho `kubectl get`
        - name: Schedule
          type: string
          jsonPath: .spec.schedule
```

```bash
kubectl apply -f backup-crd.yaml

kubectl get crd
kubectl get crd backups.ops.example.com
kubectl api-resources | grep backups          # Xác nhận kind mới đã xuất hiện
kubectl explain backup.spec                   # Schema hoạt động ngay
kubectl get backups -A
kubectl get bk                                # shortName cũng chạy
```

> ⚠️ **Bẫy 1:** `metadata.name` của CRD **phải** là `<spec.names.plural>.<spec.group>`. Sai một ký tự là API server từ chối ngay.
> ⚠️ **Bẫy 2:** Chỉ **đúng một** version được `storage: true`.
> ⚠️ **Bẫy 3:** Xoá CRD sẽ **xoá sạch mọi custom object** thuộc loại đó. Không có cách hoàn tác.
> ⚠️ **Bẫy 4:** CRD chỉ tạo ra **nơi lưu trữ**. Không có controller nào đọc nó thì object bạn tạo chỉ nằm im trong etcd — không có gì xảy ra cả.

#### 2. Operator = CRD + Controller

**Operator** là mẫu thiết kế đóng gói *tri thức vận hành* của con người thành phần mềm:

```text
Operator  =  CRD (định nghĩa "cái gì")  +  Controller (vòng lặp thực thi "làm thế nào")
```

Controller chạy vòng lặp bất tận: **observe** trạng thái thực tế → **diff** với `spec` mong muốn → **act** để thu hẹp khoảng cách → cập nhật `status`. Đây chính xác là cơ chế của các controller có sẵn (Deployment, ReplicaSet), chỉ khác là do bên thứ ba viết.

Cài operator — hầu hết dùng Helm hoặc một manifest bundle:
```bash
# Cách 1: Helm (phổ biến nhất)
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set crds.enabled=true

# Cách 2: Manifest bundle
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
```

Xác minh sau khi cài:
```bash
kubectl get crds | grep cert-manager          # CRD đã đăng ký chưa?
kubectl get pods -n cert-manager              # Controller có Running không?
kubectl get clusterissuers                    # Custom resource dùng được chưa?
kubectl api-resources --api-group=cert-manager.io
```

Chuỗi truy vết khi custom resource "không có gì xảy ra":
```bash
kubectl get <customresource> <name> -o yaml   # Trường .status nói gì?
kubectl describe <customresource> <name>      # Đọc Events
kubectl logs -n <operator-ns> deploy/<operator-controller>   # Log của controller
kubectl get crd <name> -o jsonpath='{.spec.versions[*].name}{"\n"}'
```

> 🧠 **Mẹo ghi nhớ:** **CRD = danh từ** (định nghĩa kiểu dữ liệu mới). **Controller/Operator = động từ** (biến khai báo thành hiện thực). Object tạo ra mà "không có gì xảy ra" → gần như chắc chắn **controller không chạy**, chứ không phải CRD sai.

---

### 🅳 Buổi D — Practice & Review (~2h)

- Thực hành trọn vẹn bài lab trong [labs.md](labs.md): Cordon/Drain node, mô phỏng thảm hoạ xoá mất namespace quan trọng và khôi phục thành công bằng etcd snapshot.

---

## 🚪 Cổng tự kiểm tra Tuần 9 (Self-check Gate)

1. [ ] Lệnh nâng cấp trên Worker Node dùng `kubeadm upgrade apply` hay `kubeadm upgrade node`? *(Đáp án: Worker Node dùng `kubeadm upgrade node`; chỉ Control Plane mới dùng `kubeadm upgrade apply`).*
2. [ ] Khi restore etcd snapshot bằng `etcdctl`, tại sao bắt buộc phải chỉ định `--data-dir` sang một thư mục mới? *(Đáp án: Để tránh ghi đè hoặc xung đột lock file với cơ sở dữ liệu etcd đang chạy).*
3. [ ] Nếu chạy `kubectl drain` mà bị báo lỗi do có Pod không thuộc controller nào quản lý, bạn cần thêm cờ gì? *(Đáp án: Thêm cờ `--force`).*
4. [ ] Cụm etcd 4 member chịu được mất mấy node? So với 3 member thì hơn kém thế nào? *(Đáp án: **Cả hai đều chỉ chịu được mất 1**. Quorum của 4 là 3, của 3 là 2. Thêm node thứ 4 không tăng khả năng chịu lỗi mà còn tăng xác suất hỏng hóc — vì vậy etcd luôn dùng số **lẻ**).*
5. [ ] Vì sao `kubeadm init` phải dùng `--control-plane-endpoint` ngay từ lần đầu dù mới có 1 node? *(Đáp án: Endpoint này được nhúng vào chứng chỉ và kubeconfig của toàn cụm, **không sửa được về sau**. Không có nó thì không thể mở rộng lên HA mà không dựng lại cụm).*
6. [ ] Trong cụm HA, thành phần nào chạy active-active, thành phần nào active-passive? *(Đáp án: `kube-apiserver` **active-active** (stateless, cả 3 cùng phục vụ sau LB). `kube-controller-manager` và `kube-scheduler` **active-passive** qua leader election — xem bằng `kubectl get lease -n kube-system`).*
7. [ ] `metadata.name` của một CRD phải tuân theo quy tắc nào? *(Đáp án: Chính xác `<spec.names.plural>.<spec.group>`, ví dụ `backups.ops.example.com`. Sai là API server từ chối).*
8. [ ] Bạn apply CRD thành công và tạo được custom object, nhưng không có gì xảy ra trong cluster. Nguyên nhân? *(Đáp án: CRD chỉ tạo ra **chỗ lưu trữ** trong API/etcd. Cần một **controller/operator** đọc object đó và hành động. Kiểm tra pod controller có Running và đọc log của nó).*
