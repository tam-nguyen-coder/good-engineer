# 🟩 Tuần 2 — Workloads & Controllers: Deployments, Rollouts, DaemonSet, StatefulSet & Jobs

> **Domain:** Workloads & Scheduling (15%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 2/10
>
> **Điều hướng:** [⬅️ Tuần 1](../week-01/README.md) · [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [Tuần 3 ➡️](../week-03/README.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Hiểu sâu kiến trúc phân cấp: **Deployment quản lý ReplicaSet, ReplicaSet quản lý Pods**.
- Thành thạo chiến lược nâng cấp ứng dụng: **`RollingUpdate`** (cấu hình `maxSurge`, `maxUnavailable`) vs **`Recreate`**.
- Thuần thục quy trình vận hành Rollout trong phòng thi CKA: kiểm tra trạng thái (`rollout status`), xem lịch sử bản dựng (`rollout history`), tạm dừng (`pause`), tiếp tục (`resume`), và rollback khẩn cấp (`rollout undo`).
- Phân biệt bản chất và trường hợp sử dụng của **`DaemonSet`** (chạy trên mọi Node cho logging/monitoring) và **`StatefulSet`** (danh tính mạng ổn định, storage tách biệt cho DB).
- Khởi tạo và quản lý **`Job`** (chạy theo mẻ, `completions`, `parallelism`, `backoffLimit`) và **`CronJob`** (lập lịch cron, quản lý `concurrencyPolicy`).

---

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Deployment Strategies & Rollout Management (~3h)

#### 1. Cơ chế hoạt động của Deployment & ReplicaSet
- Deployment không trực tiếp tạo ra Pod! Deployment tạo ra và quản lý **ReplicaSet**. Mỗi lần thay đổi Pod Template (ví dụ đổi image), Deployment sẽ tạo ra một ReplicaSet MỚI.
- **Chiến lược RollingUpdate (Mặc định):**
  - Đảm bảo ứng dụng hoạt động liên tục không có thời gian chết (Zero-downtime).
  - Hai tham số điều tiết quan trọng:
    - **`maxSurge`**: Số lượng Pod tối đa được phép tạo VƯỢT QUÁ số lượng replicas mong muốn trong quá trình update (mặc định: `25%`).
    - **`maxUnavailable`**: Số lượng Pod tối đa được phép KHÔNG KHẢ DỤNG trong quá trình update (mặc định: `25%`).
- **Chiến lược Recreate:**
  - Xoá sạch toàn bộ các Pod cũ trước, sau đó mới tạo các Pod mới.
  - Chấp nhận có Downtime. Phù hợp khi ứng dụng không thể chạy 2 phiên bản song song (ví dụ: khoá database duy nhất).

#### 2. Bộ lệnh Rollout phản xạ nhanh (Bắt buộc cho CKA)
```bash
# 1. Cập nhật image trực tiếp
kubectl set image deployment/web-app nginx=nginx:1.25 --record

# 2. Xem tiến trình cập nhật thời gian thực
kubectl rollout status deployment/web-app

# 3. Xem lịch sử các lần cập nhật (revisions)
kubectl rollout history deployment/web-app

# 4. Xem chi tiết một revision cụ thể
kubectl rollout history deployment/web-app --revision=2

# 5. Hoàn tác về revision trước đó ngay lập tức (Rollback)
kubectl rollout undo deployment/web-app

# 6. Hoàn tác về một revision cụ thể trong quá khứ
kubectl rollout undo deployment/web-app --to-revision=1
```

---

### 🅱️ Buổi B — DaemonSet & StatefulSet (~3.5h)

#### 1. `DaemonSet` — Bản sao trên từng Node
- Đảm bảo **tất cả (hoặc một số) Node đều chạy chính xác 1 bản sao của Pod**.
- Khi một Node mới được thêm vào cluster, DaemonSet tự động xếp một Pod lên node đó. Khi node bị gỡ bỏ, Pod tự bị thu hồi rác.
- **Ứng dụng thực tế:**
  - Cluster Storage Daemons: `ceph`, `glusterd`.
  - Log Collection Daemons: `fluentd`, `filebeat`, `logstash`.
  - Node Monitoring Daemons: `prometheus-node-exporter`, `datadog-agent`.
- **Mẹo phòng thi:** Không có lệnh `kubectl create daemonset`!
  - Cách tạo nhanh: Dùng `kubectl create deployment <name> --image=... $do > ds.yaml`
  - Sau đó mở file `ds.yaml`: Đổi `kind: Deployment` -> `kind: DaemonSet`, xoá mục `replicas: ...` và xoá `strategy: ...`.

#### 2. `StatefulSet` — Ứng dụng có trạng thái
- Dành cho các ứng dụng cơ sở dữ liệu phân tán (MySQL, PostgreSQL, MongoDB, Kafka, ZooKeeper).
- **Đặc điểm sống còn:**
  - **Danh tính mạng duy nhất & ổn định:** Pod đặt tên theo chỉ số thứ tự tuần tự bắt đầu từ 0: `web-0`, `web-1`, `web-2`.
  - **Khởi tạo và huỷ tuần tự:** Tạo `web-0` xong mới tạo `web-1`. Khi scale down, tắt `web-2` trước rồi mới tới `web-1`.
  - **Headless Service (`clusterIP: None`):** Bắt buộc phải có để cung cấp bản ghi DNS trực tiếp tới từng Pod: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`.
  - **`volumeClaimTemplates`:** Mỗi bản sao Pod sẽ tự động yêu cầu một PV/PVC riêng biệt gắn chặt vào danh tính của Pod đó (khi `web-1` chết và sống lại, nó sẽ gắn lại đúng ổ đĩa của `web-1`).

---

### 🅲 Buổi C — Batch Workloads: Jobs & CronJobs (~2.5h)

#### 1. `Job` (Chạy tác vụ một lần)
- Đảm bảo một hoặc nhiều Pod chạy cho đến khi kết thúc thành công (`Exit Code 0`).
- **Các tham số quan trọng:**
  - `completions`: Số lần chạy thành công cần đạt được.
  - `parallelism`: Số lượng Pod được phép chạy đồng thời.
  - `backoffLimit`: Số lần thử lại tối đa khi Pod bị lỗi trước khi đánh dấu Job thất bại (mặc định là `6`).
  - `activeDeadlineSeconds`: Giới hạn thời gian chạy tối đa của Job (quá giờ sẽ bị cưỡng bức terminate).
- Lệnh tạo nhanh:
  ```bash
  kubectl create job process-data --image=busybox -- sh -c "echo Processing data; sleep 5"
  ```

#### 2. `CronJob` (Chạy tác vụ theo lịch biểu)
- Quản lý Job theo định dạng cron chuẩn (`phút giờ ngày_trong_tháng tháng ngày_trong_tuần`).
- **Chính sách đồng thời `concurrencyPolicy` (ĐIỂM THI HAY HỎI):**
  - `Allow` (Mặc định): Cho phép các Job mới chạy song song ngay cả khi Job cũ chưa kết thúc.
  - `Forbid`: Nếu Job cũ đang chạy mà lịch mới đã đến → **BỎ QUA** lần chạy mới, không cho chạy đè lên nhau.
  - `Replace`: Nếu Job cũ chưa xong → **HUỶ BỎ** Job cũ và chạy ngay Job mới.
- Lệnh tạo nhanh:
  ```bash
  kubectl create cronjob report-gen --image=busybox --schedule="*/5 * * * *" -- sh -c "date"
  ```

---

### 🅳 Buổi D — Practice & Review (~2h)

- Tự tay hoàn thành toàn bộ các bài thực hành trong [labs.md](labs.md).
- Thử nghiệm các tình huống lỗi: Rollout image không tồn tại dẫn đến `ImagePullBackOff`, sau đó rollback; cấu hình CronJob với `concurrencyPolicy: Forbid`.

---

## 🚪 Cổng tự kiểm tra Tuần 2 (Self-check Gate)

1. [ ] Làm thế nào để tạo một DaemonSet bằng CLI khi `kubectl` không hỗ trợ `kubectl create daemonset`?
2. [ ] Trong quá trình RollingUpdate, nếu `replicas: 4`, `maxSurge: 1`, `maxUnavailable: 0` thì tại một thời điểm có tối đa bao nhiêu Pod và tối thiểu bao nhiêu Pod hoạt động? *(Đáp án: Tối đa 5 Pod, tối thiểu 4 Pod hoạt động liên tục).*
3. [ ] StatefulSet bắt buộc phải đi kèm với loại Service nào để phân giải DNS trực tiếp tới từng Pod? *(Đáp án: Headless Service với `clusterIP: None`).*
4. [ ] Ý nghĩa của `concurrencyPolicy: Forbid` trong CronJob là gì? *(Đáp án: Không cho phép Job mới chạy nếu Job lần trước chưa kết thúc).*
