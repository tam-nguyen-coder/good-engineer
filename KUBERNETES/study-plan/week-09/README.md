# 🛠️ Tuần 9 — Cluster Maintenance, Kubeadm Upgrade & etcd Disaster Recovery

> **Domain:** Cluster Architecture, Installation & Configuration (25%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 9/10
>
> **Điều hướng:** [⬅️ Tuần 8](../week-08/README.md) · [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [Tuần 10 ➡️](../week-10/README.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Làm chủ quy trình bảo trì Node: Phân biệt sự khác nhau giữa **`kubectl cordon`** (chặn xếp Pod mới) và **`kubectl drain`** (di dời Pod đang chạy một cách an toàn), cùng các cờ bắt buộc: `--ignore-daemonsets`, `--delete-emptydir-data`, `--force`.
- Thực hiện chuẩn xác quy trình **Nâng cấp Cluster bằng Kubeadm (Kubeadm Cluster Upgrade)** từ phiên bản `v1.30.x` lên `v1.31.x` theo đúng trình tự nghiêm ngặt (Control Plane trước, Worker Nodes sau; không được nhảy cóc minor version).
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

> ⚠️ **Quy tắc vàng:** Chỉ nâng cấp từng minor version (ví dụ: `1.30 -> 1.31`). Tuyệt đối không được nhảy từ `1.29 -> 1.31`!

#### Bước 1: Nâng cấp Control Plane Node đầu tiên
```bash
# 1. Drain node control-plane
kubectl drain controlplane --ignore-daemonsets

# 2. Cập nhật apt repo và nâng cấp công cụ kubeadm
apt-mark unhold kubeadm
apt-get update && apt-get install -y kubeadm=1.31.0-1.1
apt-mark hold kubeadm

# 3. Kiểm tra kế hoạch nâng cấp
kubeadm upgrade plan

# 4. Áp dụng nâng cấp cho Control Plane
sudo kubeadm upgrade apply v1.31.0

# 5. Nâng cấp kubelet và kubectl trên node
apt-mark unhold kubelet kubectl
apt-get update && apt-get install -y kubelet=1.31.0-1.1 kubectl=1.31.0-1.1
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
apt-get update && apt-get install -y kubeadm=1.31.0-1.1
apt-mark hold kubeadm

# 3. Nâng cấp cấu hình node worker (KHÁC VỚI CONTROL PLANE):
sudo kubeadm upgrade node

# 4. Nâng cấp kubelet & kubectl:
apt-mark unhold kubelet kubectl
apt-get update && apt-get install -y kubelet=1.31.0-1.1 kubectl=1.31.0-1.1
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

### 🅳 Buổi D — Practice & Review (~2h)

- Thực hành trọn vẹn bài lab trong [labs.md](labs.md): Cordon/Drain node, mô phỏng thảm hoạ xoá mất namespace quan trọng và khôi phục thành công bằng etcd snapshot.

---

## 🚪 Cổng tự kiểm tra Tuần 9 (Self-check Gate)

1. [ ] Lệnh nâng cấp trên Worker Node dùng `kubeadm upgrade apply` hay `kubeadm upgrade node`? *(Đáp án: Worker Node dùng `kubeadm upgrade node`; chỉ Control Plane mới dùng `kubeadm upgrade apply`).*
2. [ ] Khi restore etcd snapshot bằng `etcdctl`, tại sao bắt buộc phải chỉ định `--data-dir` sang một thư mục mới? *(Đáp án: Để tránh ghi đè hoặc xung đột lock file với cơ sở dữ liệu etcd đang chạy).*
3. [ ] Nếu chạy `kubectl drain` mà bị báo lỗi do có Pod không thuộc controller nào quản lý, bạn cần thêm cờ gì? *(Đáp án: Thêm cờ `--force`).*
