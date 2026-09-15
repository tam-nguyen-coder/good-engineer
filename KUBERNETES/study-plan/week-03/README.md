# 🟨 Tuần 3 — Pod Scheduling & Advanced Placement: Taints, Tolerations, Affinity & QoS

> **Domain:** Workloads & Scheduling (15%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 3/10
>
> **Điều hướng:** [⬅️ Tuần 2](../week-02/README.md) · [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [Tuần 4 ➡️](../week-04/README.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Phân biệt bản chất giữa **`nodeSelector`** (khớp nhãn đơn giản) và **`nodeAffinity`** (biểu thức linh hoạt: `In`, `NotIn`, `Exists`, `Gt`, `Lt`).
- Làm chủ 2 điều kiện lập lịch: **`requiredDuringSchedulingIgnoredDuringExecution`** (ràng buộc cứng - Hard rule) và **`preferredDuringSchedulingIgnoredDuringExecution`** (ưu tiên mềm - Soft rule).
- Cấu hình **`podAntiAffinity`** kết hợp `topologyKey` để phân tán các bản sao Pod trên các Node hoặc Availability Zones khác nhau, chống Single Point of Failure (SPOF).
- Hiểu rõ cơ chế **`Taints`** (đặt trên Node) và **`Tolerations`** (đặt trên Pod). Phân biệt 3 hiệu ứng: `NoSchedule`, `PreferNoSchedule`, và `NoExecute`.
- Nắm vững cơ chế tính toán **Resource Requests & Limits**, phân loại 3 lớp **QoS Classes** (`Guaranteed`, `Burstable`, `BestEffort`) và thứ tự bị Eviction khi Node cạn tài nguyên.
- Cấu hình **`LimitRange`** (giới hạn trên từng Pod) và **`ResourceQuota`** (trần tổng tài nguyên trên Namespace).

---

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Taints & Tolerations: Cô lập hạ tầng (~3h)

#### 1. Nguyên lý cơ bản
- **Taint (Vết bẩn):** Đặt trên **Node**. Báo hiệu rằng node này không chấp nhận các Pod thông thường, trừ khi Pod có "sức đề kháng" phù hợp.
- **Toleration (Khả năng chịu đựng):** Khai báo trong **PodSpec**. Cho phép Pod được lập lịch lên các Node có Taint tương ứng.
- **LƯU Ý CỐT LÕI:** Toleration **KHÔNG ÉP** Pod phải chạy trên Node có Taint! Nó chỉ cho phép Pod *được phép* chạy ở đó nếu Scheduler chọn. (Muốn ép Pod vào node cụ thể, phải kết hợp thêm `nodeSelector` hoặc `nodeAffinity`).

#### 2. Ba hiệu ứng Taint Effect (Effect Values)
1. **`NoSchedule`**: Nếu Pod không có toleration phù hợp → Kube-scheduler sẽ **không bao giờ xếp Pod** lên node này. (Các Pod đang chạy sẵn không bị ảnh hưởng).
2. **`PreferNoSchedule`**: Scheduler sẽ **cố gắng tránh** xếp Pod lên node này, nhưng nếu toàn cụm không còn node nào khác trống thì vẫn có thể xếp vào (Soft rule).
3. **`NoExecute`**: Nếu Pod không có toleration phù hợp → Không những không được xếp lên, mà **các Pod đang chạy sẵn trên Node cũng sẽ bị ĐUỔI NGAY LẬP TỨC (Evicted)**!
   - Có thể chỉ định thêm `tolerationSeconds` (ví dụ 3600s: cho phép chạy thêm 1 tiếng sau khi node bị taint trước khi bị đuổi).

#### 3. Cú pháp CLI thần tốc phòng thi
```bash
# Thêm Taint NoSchedule vào node worker1:
kubectl taint nodes worker1 tier=backend:NoSchedule

# Thêm Taint NoExecute vào node worker2:
kubectl taint nodes worker2 dedicated=gpu:NoExecute

# GỠ BỎ Taint (Bắt buộc thêm dấu trừ '-' ở cuối):
kubectl taint nodes worker1 tier=backend:NoSchedule-
```

---

### 🅱️ Buổi B — NodeAffinity & PodAntiAffinity (~3.5h)

#### 1. NodeAffinity
Thay thế cho `nodeSelector` cũ kỹ bằng cú pháp biểu thức mạnh mẽ:
```yaml
affinity:
  nodeAffinity:
    # 1. RÀNG BUỘC CỨNG: Bắt buộc node phải có nhãn zone=us-east-1a hoặc 1b
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: topology.kubernetes.io/zone
          operator: In
          values:
          - us-east-1a
          - us-east-1b
    # 2. ƯU TIÊN MỀM: Thích chạy trên node có đĩa SSD hơn, nhưng không bắt buộc
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 80
      preference:
        matchExpressions:
        - key: disktype
          operator: In
          values:
          - ssd
```

#### 2. PodAntiAffinity (Phân tán Pod chống sập cụm)
Ví dụ: Đảm bảo không có 2 Pod web nào chạy chung trên cùng một Node:
```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app
          operator: In
          values:
          - web
      topologyKey: "kubernetes.io/hostname" # Tiêu chí phân định: theo hostname của node
```

---

### 🅲 Buổi C — Resource Management & Pod QoS Classes (~2.5h)

#### 1. Requests vs Limits
- **`requests`**: Lượng tài nguyên Kube-scheduler dùng để **tính toán xếp chỗ** trên Node. Nếu Node không còn đủ CPU/Memory trống bằng mức requests, Pod sẽ bị kẹt `Pending`.
- **`limits`**: Ngưỡng trần tối đa Kubelet cho phép container sử dụng:
  - Vượt CPU Limit: Ứng dụng bị **bóp băng thông (CPU Throttling)**, không bị kill.
  - Vượt Memory Limit: Ứng dụng bị nhân Linux **tiêu diệt ngay lập tức (`OOMKilled`, Exit Code 137)**.

#### 2. Ba cấp độ QoS (Quality of Service)
Kubernetes tự động gán nhãn QoS cho Pod dựa trên cách khai báo resources:

| QoS Class | Điều kiện đạt được | Mức độ ưu tiên khi Node thiếu RAM |
|---|---|---|
| **`Guaranteed`** | Mọi container đều khai báo cả CPU & Memory, và **`requests == limits`** | ⭐⭐⭐ **Cao nhất** — Chỉ bị kill cuối cùng khi toàn bộ Pod khác đã bị dọn sạch |
| **`Burstable`** | Khai báo requests và limits nhưng **`requests < limits`** | ⭐⭐ **Trung bình** — Bị kill sau khi BestEffort đã hết |
| **`BestEffort`** | Hoàn toàn **không khai báo requests và limits** | ⭐ **Thấp nhất** — Bị Kubelet tiêu diệt ĐẦU TIÊN khi Node gặp MemoryPressure |

---

### 🅳 Buổi D — Practice & Review (~2h)

- Hoàn thành bài lab gán nhãn node, taint node và phân tích QoS trong [labs.md](labs.md).
- Thực hành câu hỏi tình huống: Tìm xem Pod nào vi phạm ResourceQuota khiến Deployment không scale được.

---

## 🚪 Cổng tự kiểm tra Tuần 3 (Self-check Gate)

1. [ ] Làm thế nào để gỡ bỏ một Taint khỏi Node bằng lệnh `kubectl`? *(Đáp án: Chạy lại lệnh taint kèm dấu trừ `-` ở cuối key=effect).*
2. [ ] Pod có QoS Class là `Guaranteed` khi nào? *(Đáp án: Khi tất cả container có đủ cả cpu/memory requests và limits, và giá trị requests bằng đúng limits).*
3. [ ] Nếu một container dùng quá CPU Limit thì điều gì xảy ra? Dùng quá Memory Limit thì điều gì xảy ra? *(Đáp án: CPU bị Throttling; Memory bị OOMKilled).*
4. [ ] Sự khác biệt giữa Taint `NoSchedule` và `NoExecute` là gì? *(Đáp án: `NoSchedule` chỉ ảnh hưởng Pod mới; `NoExecute` đuổi luôn cả các Pod đang chạy sẵn).*
