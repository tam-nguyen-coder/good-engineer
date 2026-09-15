# 🟫 Tuần 7 — Storage Architecture: Volumes, PV, PVC, StorageClass & Dynamic Provisioning

> **Domain:** Storage (10%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 7/10
>
> **Điều hướng:** [⬅️ Tuần 6](../week-06/README.md) · [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [Tuần 8 ➡️](../week-08/README.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Phân biệt rõ sự khác nhau giữa **Ephemeral Volumes** (`emptyDir`, `hostPath`) và **Persistent Storage** (PV, PVC).
- Hiểu trọn vẹn **Vòng đời 4 pha của Persistent Storage**: `Provisioning` -> `Binding` -> `Using` -> `Reclaiming`.
- Phân biệt 3 chính sách thu hồi **`reclaimPolicy`**: `Retain` (giữ lại dữ liệu thủ công), `Delete` (xoá ổ đĩa vật lý khi xoá PVC), và `Recycle` (đã deprecated).
- Làm chủ 4 chế độ truy cập **`accessModes`**: `ReadWriteOnce` (RWO), `ReadOnlyMany` (ROX), `ReadWriteMany` (RWX), và `ReadWriteOncePod` (RWOP - chuẩn v1.29+).
- Cấu hình **`StorageClass`** phục vụ **Dynamic Provisioning** (tự động tạo PV khi có PVC) và phân biệt 2 chế độ **`volumeBindingMode`**: `Immediate` vs `WaitForFirstConsumer`.
- Thực hành thao tác **mở rộng dung lượng ổ đĩa trực tiếp (Volume Expansion)** mà không làm mất dữ liệu.

---

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — PV vs PVC: Cơ chế Tách biệt Trách nhiệm (~3h)

Kubernetes tách biệt vai trò quản trị lưu trữ thành 2 lớp rõ rệt:

```text
[ Cluster Administrator ]
          |
          v
Creates [ PersistentVolume (PV) ] (Dung lượng: 10Gi, Access: RWO, HostPath / Cloud Disk)
          ^
          | (K8s Control Plane BINDING theo dung lượng & AccessMode phù hợp)
          v
Creates [ PersistentVolumeClaim (PVC) ] (Yêu cầu: 5Gi, Access: RWO)
          ^
          | (ClaimName gắn vào Volume của Pod)
[ Application Developer ]
          |
          v
Creates [ Pod / Deployment ]
```

- **Quy tắc Binding giữa PVC và PV:**
  - Dung lượng của PV phải **lớn hơn hoặc bằng** dung lượng yêu cầu trong PVC.
  - Các `accessModes` của PV phải bao hàm `accessModes` trong PVC.
  - `storageClassName` phải trùng khớp (hoặc cùng để trống).
  - Một PV khi đã được Bind vào một PVC thì ở trạng thái **`Bound`** và không thể dùng chung cho PVC khác (tỉ lệ 1:1).

---

### 🅱️ Buổi B — StorageClass & Dynamic Provisioning (~3.5h)

Thay vì Admin phải tạo thủ công hàng trăm PV tĩnh (Static Provisioning):
1. Admin chỉ cần tạo một bản thiết kế mẫu: **`StorageClass`**.
2. Khi Developer gửi một `PersistentVolumeClaim` trỏ tới `storageClassName` đó, K8s Storage Controller sẽ tự động gọi CSI Driver (như AWS EBS, GCP PD, Ceph) để tạo ra ổ cứng thật và sinh ra PV tương ứng (Dynamic Provisioning).

#### Khác biệt sống còn: `volumeBindingMode`
- **`Immediate` (Mặc định):**
  - Ngay khi PVC được tạo, PV được cấp phát và gắn ngay lập tức.
  - **Rủi ro lớn trong môi trường Multi-AZ:** Ổ đĩa có thể được tạo ở Zone A, nhưng sau này Kube-scheduler lại xếp Pod vào Zone B (vì Zone B trống RAM hơn) -> Pod không thể start vì không thể mount đĩa xuyên Zone!
- **`WaitForFirstConsumer` (Khuyến nghị số 1 cho Cloud):**
  - Trì hoãn việc tạo và bind PV cho đến khi **Pod đầu tiên sử dụng PVC này được Kube-scheduler lập lịch vào 1 Node cụ thể**.
  - Nhờ đó, PV sẽ luôn được tạo chính xác tại Zone của Node mà Pod đang chạy!

---

### 🅲 Buổi C — Volume Expansion & Access Modes (~2.5h)

#### 1. Mở rộng kích thước volume (Resize PVC)
Để mở rộng dung lượng PVC mà không làm gián đoạn:
1. `StorageClass` phải có cờ: **`allowVolumeExpansion: true`**.
2. Người dùng chỉ cần sửa PVC: tăng `spec.resources.requests.storage` từ `10Gi` lên `20Gi` (Lưu ý: **Chỉ được tăng, không được giảm dung lượng**).

#### 2. 4 loại AccessModes
- **`ReadWriteOnce` (RWO)**: Volume chỉ có thể được mount đọc-ghi bởi các Pod trên **DUY NHẤT 1 NODE** (các Pod trên node khác không mount được).
- **`ReadOnlyMany` (ROX)**: Nhiều Pod trên **NHIỀU NODE KHÁC NHAU** có thể cùng mount volume ở chế độ **CHỈ ĐỌC**.
- **`ReadWriteMany` (RWX)**: Nhiều Pod trên **NHIỀU NODE KHÁC NHAU** có thể cùng mount volume ở chế độ **ĐỌC VÀ GHI** (yêu cầu storage dạng mạng như NFS, AWS EFS, CephFS).
- **`ReadWriteOncePod` (RWOP - Chuẩn mới v1.29+)**: Chỉ DUY NHẤT **1 POD** trong toàn bộ cluster được phép mount volume đọc-ghi tại một thời điểm (ngăn chặn tình trạng 2 pod trên cùng 1 node ghi đè dữ liệu lên nhau).

---

### 🅳 Buổi D — Practice & Review (~2h)

- Hoàn thành trọn vẹn 3 bài lab trong [labs.md](labs.md): Tạo PV tĩnh, tạo PVC, gắn vào Pod và kiểm chứng dữ liệu tồn tại sau khi xoá Pod; thử nghiệm Dynamic Provisioning với `WaitForFirstConsumer`.

---

## 🚪 Cổng tự kiểm tra Tuần 7 (Self-check Gate)

1. [ ] Nếu xoá một PVC mà PV tương ứng có `reclaimPolicy: Retain` thì PV sẽ chuyển sang trạng thái gì? Dữ liệu có bị xoá không? *(Đáp án: Chuyển sang trạng thái `Released`. Dữ liệu vẫn được giữ nguyên an toàn, chưa thể gán cho PVC khác cho đến khi Admin xử lý).*
2. [ ] Khi nào nên sử dụng `volumeBindingMode: WaitForFirstConsumer` thay vì `Immediate`? *(Đáp án: Khi cụm chạy trên nhiều Availability Zones, giúp đảm bảo PV được tạo đúng Zone của Node mà Pod được lập lịch).*
3. [ ] Có thể giảm dung lượng của một PVC đang chạy từ 20Gi xuống 10Gi được không? *(Đáp án: KHÔNG. Kubernetes và các hệ thống file bên dưới chỉ cho phép mở rộng (expand), không cho phép thu nhỏ volume).*
