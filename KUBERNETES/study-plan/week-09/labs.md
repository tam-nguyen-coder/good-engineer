# 🧪 Hands-on Labs — Tuần 9: Cluster Maintenance & etcd Disaster Recovery

> Thực hành bảo trì node (Cordon/Drain/Uncordon) và khôi phục sự cố với etcd snapshot.
> Về [plan tuần 9](README.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

---

## Lab 9.1 — Thực hành Cordon, Drain và Uncordon Worker Node

**🎯 Mục tiêu:** Thực hiện bảo trì di dời an toàn toàn bộ Pod khỏi Worker Node và đưa Node quay trở lại hoạt động.
**⏱️ ~20 phút**

### Các bước thực hiện:

1. Tạo một Deployment gồm 4 replicas phân bổ trên các node:
   ```bash
   kubectl create deployment test-drain --image=nginx:alpine --replicas=4
   kubectl get pods -o wide -l app=test-drain
   ```

2. Thử nghiệm **`cordon`**:
   ```bash
   kubectl cordon cka-cluster-worker
   kubectl get nodes
   ```
   *Quan sát cột STATUS của node: hiển thị `Ready,SchedulingDisabled`.*
   Scale deployment lên 6 replicas:
   ```bash
   kubectl scale deployment test-drain --replicas=6
   kubectl get pods -o wide -l app=test-drain
   ```
   *Quan sát: 2 Pod mới được tạo ra KHÔNG BAO GIỜ rơi vào `cka-cluster-worker` mà chuyển hết sang `worker2`.*

3. Thử nghiệm **`drain`**:
   Di dời toàn bộ Pod khỏi `cka-cluster-worker`:
   ```bash
   kubectl drain cka-cluster-worker --ignore-daemonsets --delete-emptydir-data --force
   ```
   *Quan sát: Lệnh sẽ lần lượt evict các Pod đang chạy trên node này.*
   Kiểm tra lại danh sách Pod:
   ```bash
   kubectl get pods -o wide -l app=test-drain
   ```
   *Quan sát: Không còn bất kỳ Pod nào của `test-drain` chạy trên `cka-cluster-worker`.*

4. Mở cửa Node quay lại hoạt động (**`uncordon`**):
   ```bash
   kubectl uncordon cka-cluster-worker
   kubectl get nodes
   ```
   *Quan sát: Trạng thái trở về `Ready` bình thường.*

---

## Lab 9.2 — Kịch bản Disaster Recovery: Phục hồi etcd Snapshot

**🎯 Mục tiêu:** Mô phỏng tình huống thảm hoạ: Lưu snapshot etcd, vô tình xoá mất Namespace quan trọng, sau đó khôi phục lại cụm về thời điểm trước khi bị xoá.
**⏱️ ~30 phút**

### Các bước thực hiện:

1. Tạo dữ liệu quan trọng cần bảo vệ:
   ```bash
   kubectl create ns mission-critical
   kubectl create deployment secret-api --image=nginx:alpine --replicas=3 -n mission-critical
   kubectl get pods -n mission-critical
   ```

2. SSH vào container Control Plane của Kind:
   ```bash
   docker exec -it cka-cluster-control-plane bash
   ```

3. Cài đặt tiện ích `etcdctl` (nếu chưa có sẵn):
   ```bash
   apt-get update && apt-get install -y etcd-client
   ```

4. **Tạo file Snapshot Backup:**
   ```bash
   ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
     --cacert=/etc/kubernetes/pki/etcd/ca.crt \
     --cert=/etc/kubernetes/pki/etcd/server.crt \
     --key=/etc/kubernetes/pki/etcd/server.key \
     snapshot save /tmp/backup-state.db
   ```

5. Kiểm tra tính hợp lệ của Snapshot:
   ```bash
   ETCDCTL_API=3 etcdctl --write-out=table snapshot status /tmp/backup-state.db
   ```

6. **Mô phỏng thảm hoạ:** Thoát ra máy host và xoá sạch namespace `mission-critical`:
   ```bash
   exit
   kubectl delete ns mission-critical
   kubectl get ns mission-critical
   ```
   *(Namespace đã biến mất hoàn toàn!)*

7. **Tiến hành khôi phục (Disaster Recovery):**
   Quay lại Control Plane container:
   ```bash
   docker exec -it cka-cluster-control-plane bash
   ```

8. Restore dữ liệu từ file snapshot vào thư mục mới `/var/lib/etcd-from-backup`:
   ```bash
   ETCDCTL_API=3 etcdctl snapshot restore /tmp/backup-state.db \
     --data-dir=/var/lib/etcd-from-backup
   ```

9. Cập nhật file cấu hình Static Pod `/etc/kubernetes/manifests/etcd.yaml`:
   Dùng `vim /etc/kubernetes/manifests/etcd.yaml`:
   Tìm phần volumes `etcd-data` và đổi đường dẫn `hostPath`:
   ```yaml
     volumes:
     - hostPath:
         path: /var/lib/etcd-from-backup # <-- Trỏ vào thư mục vừa restore
         type: DirectoryOrCreate
       name: etcd-data
   ```

10. Lưu file và đợi 30–60 giây để Kubelet tự động restart pod etcd.
    Kiểm tra trạng thái từ máy host:
    ```bash
    exit
    kubectl get ns mission-critical
    kubectl get pods -n mission-critical
    ```
    *KẾT QUẢ KỲ DIỆU: Namespace `mission-critical` và 3 Pod `secret-api` đã được hồi sinh hoàn toàn!*

---

## 🧹 Dọn dẹp:
```bash
kubectl delete deployment test-drain
kubectl delete ns mission-critical
```
