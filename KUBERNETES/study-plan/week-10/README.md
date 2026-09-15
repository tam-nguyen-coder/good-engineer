# 🏁 Tuần 10 — Troubleshooting Toàn Tập (30% CKA) + Killer.sh Simulator + Thi

> **Domain:** Troubleshooting (30%) & Tổng hợp toàn bộ Domains · **Thời lượng:** ~15h · **Vị trí:** Tuần 10/10 (Tuần Về Đích)
>
> **Điều hướng:** [⬅️ Tuần 9](../week-09/README.md) · [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Làm chủ kỹ năng **Gỡ lỗi 3 tầng (3-Level Troubleshooting)** chiếm tới **30% tổng số điểm bài thi CKA**:
  1. **Tầng 1: Application / Pods** (`Pending`, `CrashLoopBackOff`, `ImagePullBackOff`, `OOMKilled`, `CreateContainerConfigError`).
  2. **Tầng 2: Cluster Nodes** (Node `NotReady`, Kubelet crashed, containerd runtime stopped, DiskPressure, MemoryPressure).
  3. **Tầng 3: Control Plane** (API Server down, etcd quorum loss, Controller Manager / Scheduler static pods crashed).
- Thuần thục bộ công cụ điều tra hệ thống cấp thấp: `journalctl -u kubelet -f`, `systemctl status containerd`, `crictl ps -a`, `crictl logs <id>`.
- Kích hoạt và hoàn thành **2 Sessions thi thử trên Killer.sh Simulator** trong điều kiện thời gian thực (120 phút).
- Đạt điểm Killer.sh **≥ 85/100** → Tự tin bước vào kỳ thi chính thức và lấy chứng chỉ CKA.

---

## 📚 Kỹ năng gỡ lỗi hệ thống toàn diện

### 🅰️ Cây quyết định Troubleshooting (Decision Tree)

```text
                                 GẶP SỰ CỐ TRONG CLUSTER
                                            |
                +---------------------------+---------------------------+
                |                                                       |
        [ POD BỊ LỖI ]                                           [ NODE BỊ LỖI ]
                |                                                       |
   +------------+------------+                              +-----------+-----------+
   |                         |                              |                       |
[ PENDING ]          [ CRASH / ERROR ]                [ NOT READY ]          [ DRAIN / CORDON ]
   |                         |                              |                       |
1. kubectl describe       1. kubectl logs                1. SSH vào Node         Kiểm tra cờ
2. Check Node Allocatable    (--previous)                2. systemctl status     --ignore-daemonsets
   (CPU / RAM requests)   2. Check Events                   kubelet              --delete-emptydir
3. Check Taints vs        3. Check Probes (exec/http)    3. journalctl -u        --force
   Tolerations            4. Mã 137 -> OOMKilled            kubelet -e
4. Check NodeSelector     5. Mã 1 -> Code Crash          4. crictl ps -a
                                                         5. Check Disk/RAM (df/free)
```

---

### 🅱️ Bảng tra cứu mã lỗi Pod & Cách xử lý ngay lập tức

| Triệu chứng lỗi | Nguyên nhân gốc rễ (Root Cause) | Lệnh điều tra & Giải pháp khắc phục |
|---|---|---|
| **`Pending`** | Không có Node nào thoả mãn: thiếu CPU/RAM, dính Taint mà Pod thiếu Toleration, sai nhãn `nodeSelector` | `kubectl describe pod <name>` xem mục `Events` cuối cùng. Sửa lại requests hoặc thêm tolerations. |
| **`ImagePullBackOff`** | Gõ sai tên image, sai tag, hoặc image nằm trong private registry mà thiếu `imagePullSecrets` | `kubectl describe pod <name>` để xem URL image. Chỉnh sửa lại đúng tag hoặc tạo Docker Registry Secret. |
| **`CrashLoopBackOff`** | Ứng dụng khởi động xong rồi exit ngay lập tức (lỗi code, thiếu file config, thiếu biến môi trường, hoặc command không chạy background) | `kubectl logs <name> --previous` để xem log của lần crash trước. Dùng `kubectl edit pod` sửa command. |
| **`OOMKilled` (Exit 137)** | Container sử dụng RAM vượt quá `resources.limits.memory` được cấp phát | `kubectl describe pod <name>` xem `Last State: Terminated, Reason: OOMKilled`. Tăng limit RAM cho Pod. |
| **`CreateContainerConfigError`** | Pod khai báo sử dụng `ConfigMap` hoặc `Secret` nhưng tài nguyên đó **chưa được tạo** trong namespace | `kubectl describe pod <name>`. Tạo ConfigMap/Secret đang bị thiếu. |

---

### 🅲 Gỡ lỗi Control Plane & Kubelet khi lệnh `kubectl` mất kết nối

Nếu bạn gõ `kubectl get nodes` mà nhận được thông báo:
`The connection to the server <host>:6443 was refused - did you specify the right host or port?`

**Quy trình cấp cứu Control Plane 4 bước:**
1. **Kiểm tra tiến trình Kubelet:**
   ```bash
   sudo systemctl status kubelet
   # Nếu Kubelet tắt -> bật lại:
   sudo systemctl restart kubelet
   ```
2. **Xem log Kubelet để tìm nguyên nhân:**
   ```bash
   sudo journalctl -u kubelet -e --no-pager
   ```
3. **Kiểm tra các Static Pods của Control Plane:**
   - Di chuyển vào `/etc/kubernetes/manifests/`.
   - Kiểm tra xem 4 file (`kube-apiserver.yaml`, `etcd.yaml`, `kube-controller-manager.yaml`, `kube-scheduler.yaml`) có bị gõ sai chính tả cú pháp YAML không.
4. **Dùng `crictl` để xem container cấp thấp khi API server đang chết:**
   ```bash
   crictl ps -a
   # Tìm container ID của kube-apiserver hoặc etcd đang ở trạng thái Exited
   crictl logs <container-id>
   ```

---

### 🅳 Chiến lược làm bài thi Killer.sh & Thi thật CKA

1. **Tuân thủ kỷ luật Context:**
   - Mỗi task thi CKA bắt đầu bằng 1 dòng chuyển context màu xanh lá. **LUÔN COPY VÀ PASTE DÒNG ĐẦU TIÊN NÀY**.
2. **Kỹ thuật "Time Boxing" (6 phút/task):**
   - Đề thi gồm 16–17 tasks trong 120 phút.
   - Các task gỡ lỗi (Troubleshooting) dễ làm bạn mất tập trung và "sa lầy" 15–20 phút.
   - **Quy tắc cứng:** Nếu debug 1 task quá 7 phút mà chưa tìm ra nguyên nhân gốc → **Bấm Flag** câu hỏi, ghi lại điểm số của task vào sổ nháp và NEXT ngay sang câu tiếp theo!
3. **Kiểm tra lại toàn bộ trước khi nộp bài:**
   - Dành 15 phút cuối cùng quay lại các câu đã Flag.
   - Luôn chạy `kubectl get <resource>` để xác nhận đối tượng thực sự `Running` và `1/1 Ready`.

---

## 🚪 Cổng tự kiểm tra Tuần 10 (Sẵn sàng thi)

- [ ] Bạn đã hoàn thành ít nhất 1 session Killer.sh và đạt điểm **≥ 80–85%**?
- [ ] Bạn có thể tìm và sửa lỗi Node `NotReady` do Kubelet crash trong vòng dưới **5 phút** không?
- [ ] Bạn có thể backup etcd và restore thành công trong vòng dưới **8 phút** không?
- [ ] Bạn đã thuần thục việc tạo Pod, Deployment, Service, RoleBinding bằng lệnh imperative không cần gõ YAML tay?

> 🎓 **NẾU TẤT CẢ LÀ "CÓ", BẠN ĐÃ SẴN SÀNG 100% ĐỂ THI VÀ ĐẬU CKA VỚI ĐIỂM SỐ XUẤT SẮC!**
