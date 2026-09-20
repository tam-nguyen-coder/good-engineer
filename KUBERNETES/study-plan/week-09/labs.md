# 🧪 Hands-on Labs — Tuần 9: Cluster Maintenance & etcd Disaster Recovery

> Thực hành bảo trì node (Cordon/Drain/Uncordon), khôi phục sự cố với etcd snapshot, kiểm tra sức khoẻ **HA control plane**, và đăng ký **CRD + cài Operator**.
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

## Lab 9.3 — Khám nghiệm HA Control Plane: quorum, leader election & etcd member

**🎯 Mục tiêu:** Đọc được sức khoẻ của một control plane nhiều node — ai đang là etcd leader, ai đang giữ lease của scheduler/controller-manager, quorum còn bao nhiêu.
**⏱️ ~25 phút**

> 💡 Cụm Kind 1 control plane vẫn làm được **toàn bộ** lab này (một etcd member, một lease holder). Muốn thấy đúng chất HA, dựng Kind 3 control plane:
> ```bash
> cat << 'EOF' > kind-ha.yaml
> kind: Cluster
> apiVersion: kind.x-k8s.io/v1alpha4
> nodes:
>   - role: control-plane
>   - role: control-plane
>   - role: control-plane
>   - role: worker
> EOF
> kind create cluster --name cka-ha --config kind-ha.yaml
> ```

### Các bước thực hiện:

1. Nhìn tổng thể control plane:
   ```bash
   kubectl get nodes -l node-role.kubernetes.io/control-plane
   kubectl get pods -n kube-system -o wide \
     -l 'tier=control-plane' --show-labels | head -20
   kubectl get pods -n kube-system -l component=etcd -o wide
   ```

2. **Leader election** — ai đang thực sự làm việc:
   ```bash
   kubectl get lease -n kube-system kube-scheduler kube-controller-manager

   kubectl get lease -n kube-system kube-scheduler \
     -o jsonpath='{.spec.holderIdentity}{"\n"}'
   kubectl get lease -n kube-system kube-controller-manager \
     -o jsonpath='{.spec.holderIdentity}{"\n"}'
   ```
   > Chú ý hai lease **có thể do hai node khác nhau** nắm giữ — chúng bầu cử độc lập.

3. Kiểm tra cụm etcd từ bên trong static pod:
   ```bash
   CP=$(kubectl get pods -n kube-system -l component=etcd \
        -o jsonpath='{.items[0].metadata.name}')

   kubectl -n kube-system exec "$CP" -- sh -c '
     etcdctl --endpoints=https://127.0.0.1:2379 \
       --cacert=/etc/kubernetes/pki/etcd/ca.crt \
       --cert=/etc/kubernetes/pki/etcd/server.crt \
       --key=/etc/kubernetes/pki/etcd/server.key \
       --write-out=table member list'

   kubectl -n kube-system exec "$CP" -- sh -c '
     etcdctl --endpoints=https://127.0.0.1:2379 \
       --cacert=/etc/kubernetes/pki/etcd/ca.crt \
       --cert=/etc/kubernetes/pki/etcd/server.crt \
       --key=/etc/kubernetes/pki/etcd/server.key \
       --write-out=table endpoint status --cluster'
   ```
   Cột **`IS LEADER`** chỉ ra đúng một member đang là Raft leader.

4. Tính quorum bằng tay và đối chiếu:
   ```bash
   N=$(kubectl get pods -n kube-system -l component=etcd --no-headers | wc -l)
   echo "members=$N  quorum=$(( N/2 + 1 ))  chịu được mất=$(( N - (N/2 + 1) ))"
   ```

5. Quan sát thứ được nhúng vào chứng chỉ (lý do endpoint không đổi được):
   ```bash
   kubectl get cm kubeadm-config -n kube-system -o yaml | grep -i controlPlaneEndpoint

   # SAN thực tế trong cert của API server
   kubectl -n kube-system get pod -l component=kube-apiserver \
     -o jsonpath='{.items[0].spec.containers[0].command}' | tr ',' '\n' | grep -i 'advertise\|cert'
   ```

6. Sinh lại lệnh join khi token hết hạn (hay ra thi):
   ```bash
   # Worker
   kubeadm token create --print-join-command

   # Control plane bổ sung: cần thêm certificate-key mới
   sudo kubeadm init phase upload-certs --upload-certs
   ```

### ✅ Kết quả mong đợi:
- `member list` liệt kê đủ số etcd member; `endpoint status --cluster` chỉ ra **đúng một** `IS LEADER = true`.
- Hai Lease `kube-scheduler` và `kube-controller-manager` đều có `holderIdentity` hợp lệ.
- Phép tính quorum khớp bảng: 1→0, 3→1, 5→2.

---

## Lab 9.4 — CRD & Operator: đăng ký kind mới, rồi chứng minh CRD không tự làm gì

**🎯 Mục tiêu:** Tự tay viết một CRD, tạo custom object, **chứng kiến việc không có gì xảy ra**, sau đó cài một operator thật để thấy khác biệt.
**⏱️ ~30 phút**

### Phần A — Viết CRD từ đầu

1. Tạo CRD:
   ```bash
   cat << 'EOF' > backup-crd.yaml
   apiVersion: apiextensions.k8s.io/v1
   kind: CustomResourceDefinition
   metadata:
     name: backups.ops.example.com      # PHẢI là <plural>.<group>
   spec:
     group: ops.example.com
     scope: Namespaced
     names:
       plural: backups
       singular: backup
       kind: Backup
       shortNames: [bk]
     versions:
       - name: v1
         served: true
         storage: true
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
         additionalPrinterColumns:
           - name: Schedule
             type: string
             jsonPath: .spec.schedule
           - name: Retention
             type: integer
             jsonPath: .spec.retention
   EOF

   kubectl apply -f backup-crd.yaml
   ```

2. Xác nhận API server đã học được kind mới:
   ```bash
   kubectl get crd backups.ops.example.com
   kubectl api-resources | grep backups
   kubectl explain backup.spec
   kubectl explain backup.spec.retention
   ```

3. Tạo custom object và thử nghiệm validation:
   ```bash
   cat << 'EOF' | kubectl apply -f -
   apiVersion: ops.example.com/v1
   kind: Backup
   metadata:
     name: nightly-db
   spec:
     schedule: "0 2 * * *"
     retention: 7
   EOF

   kubectl get backups
   kubectl get bk                       # shortName
   kubectl describe backup nightly-db
   ```

4. **Chứng minh schema đang thực sự được enforce** — hai lệnh dưới đây PHẢI thất bại:
   ```bash
   # Thiếu trường bắt buộc 'schedule'
   kubectl apply -f - << 'EOF'
   apiVersion: ops.example.com/v1
   kind: Backup
   metadata: { name: bad-1 }
   spec: { retention: 3 }
   EOF

   # Vi phạm minimum: 1
   kubectl apply -f - << 'EOF'
   apiVersion: ops.example.com/v1
   kind: Backup
   metadata: { name: bad-2 }
   spec: { schedule: "@daily", retention: 0 }
   EOF
   ```

5. **Bài học cốt lõi** — object tồn tại, nhưng tuyệt đối không có gì xảy ra:
   ```bash
   kubectl get backups nightly-db -o yaml | grep -A5 'status' || echo "KHÔNG có .status"
   kubectl get pods,jobs,cronjobs -A | grep -i backup || echo "KHÔNG có workload nào được tạo"
   ```
   > 🔑 Đây chính là điều CRD làm và **không** làm. Nó cho bạn chỗ lưu và validation. Muốn có hành động, cần một **controller**.

6. Thử bẫy đặt tên sai (phải bị từ chối):
   ```bash
   sed 's/name: backups.ops.example.com/name: backup.ops.example.com/' backup-crd.yaml \
     | kubectl apply -f -
   # Lỗi: metadata.name must be spec.names.plural+"."+spec.group
   ```

### Phần B — Cài một Operator thật để thấy khác biệt

7. Cài `cert-manager` (một operator điển hình: CRD + controller):
   ```bash
   helm repo add jetstack https://charts.jetstack.io
   helm repo update
   helm install cert-manager jetstack/cert-manager \
     --namespace cert-manager --create-namespace \
     --set crds.enabled=true

   kubectl rollout status deployment cert-manager -n cert-manager
   ```

8. Quan sát cả **hai** nửa của operator:
   ```bash
   kubectl get crds | grep cert-manager          # Nửa thứ nhất: các CRD
   kubectl get pods -n cert-manager              # Nửa thứ hai: controller đang chạy
   kubectl api-resources --api-group=cert-manager.io
   ```

9. Tạo một custom resource và lần này **có** phản hồi:
   ```bash
   cat << 'EOF' | kubectl apply -f -
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: selfsigned
   spec:
     selfSigned: {}
   EOF

   sleep 10
   kubectl get clusterissuer selfsigned -o yaml | sed -n '/status:/,$p'
   ```
   > Khác biệt nằm ở đây: `.status` được **controller điền vào**. So với `nightly-db` ở bước 5 — vĩnh viễn không có status.

10. Luyện chuỗi truy vết operator:
    ```bash
    kubectl logs -n cert-manager deploy/cert-manager --tail=30
    kubectl describe clusterissuer selfsigned
    ```

### ✅ Kết quả mong đợi:
- `kubectl explain backup.spec.retention` hoạt động — schema đã vào API server thật sự.
- Hai object `bad-1`, `bad-2` bị **từ chối** bởi validation.
- `nightly-db` tồn tại nhưng **không bao giờ có `.status`** và không sinh ra workload nào.
- `ClusterIssuer selfsigned` **có** `.status` với condition `Ready=True` — bằng chứng có controller đang làm việc.

### 🧠 Ghi vào sổ tay phòng thi:
| Câu hỏi | Lệnh |
|---|---|
| "List all CRDs in the cluster" | `kubectl get crd` |
| "Which API group/version does kind X belong to?" | `kubectl api-resources \| grep -i X` |
| "What fields does this custom resource accept?" | `kubectl explain <kind>.spec` |
| "Install operator Y" | `helm install ...` hoặc `kubectl apply -f <bundle>.yaml` |
| "Custom resource does nothing" | Xem pod controller + `kubectl logs`, rồi mới xem `.status` |


---

## 🧹 Dọn dẹp:
```bash
kubectl delete deployment test-drain
kubectl delete ns mission-critical
kubectl delete backup nightly-db --ignore-not-found
kubectl delete crd backups.ops.example.com --ignore-not-found
helm uninstall cert-manager -n cert-manager 2>/dev/null
kubectl delete ns cert-manager --ignore-not-found
rm -f backup-crd.yaml kind-ha.yaml
```
