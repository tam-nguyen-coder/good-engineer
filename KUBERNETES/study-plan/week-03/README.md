# 🟨 Tuần 3 — Pod Scheduling, Affinity, QoS & Workload Autoscaling (HPA)

> **Domain:** Workloads & Scheduling (15%) + Troubleshooting (30%) · **Thời lượng:** ~13h (5 buổi) · **Vị trí:** Tuần 3/10
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

### 📈 Buổi C+ — Metrics Server, `kubectl top` & Workload Autoscaling (HPA) (~2h)

> 🆕 **Bổ sung theo curriculum CKA cập nhật 18/02/2025** — phủ hai competency: *"Configure workload autoscaling"* (Domain Workloads & Scheduling 15%) và *"Monitor cluster and application resource usage"* (Domain Troubleshooting 30%).

#### 1. Metrics Server — điều kiện tiên quyết

`kubectl top` và HPA **đều** lấy số liệu từ **Metrics Server** qua Metrics API (`metrics.k8s.io`). Không có nó thì cả hai đều chết.

```bash
# Metrics Server đã chạy chưa?
kubectl get deployment metrics-server -n kube-system
kubectl get apiservice v1beta1.metrics.k8s.io       # Cột AVAILABLE phải là True

# Cài (trên lab; trong phòng thi thường đã có sẵn)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

> ⚠️ **Bẫy lab Kind/Minikube:** kubelet dùng chứng chỉ self-signed nên Metrics Server sẽ `CrashLoopBackOff` với lỗi `x509: cannot validate certificate`. Chỉ trong **lab local**, thêm cờ:
> ```bash
> kubectl patch deployment metrics-server -n kube-system --type=json \
>   -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
> ```
> Tuyệt đối **không** làm điều này trên production.

#### 2. `kubectl top` — đọc mức tiêu thụ thực tế

```bash
kubectl top nodes
kubectl top nodes --sort-by=memory

kubectl top pods -A --sort-by=memory
kubectl top pods -n prod --sort-by=cpu
kubectl top pod <pod> --containers          # Tách theo từng container trong Pod

# Dạng task hay ra thi: ghi tên Pod ngốn RAM nhất ra file
kubectl top pods -n monitoring --sort-by=memory --no-headers \
  | head -n 1 | awk '{print $1}' > /opt/highest-memory-pod.txt
```

> 🧠 **Phân biệt cho chắc:** `kubectl top` = **mức dùng THỰC TẾ** (đo từ kubelet/cAdvisor).
> `kubectl describe node` phần *Allocated resources* = **tổng requests/limits đã ĐẶT CHỖ**, không phải mức dùng thật. Scheduler xếp Pod dựa trên **requests**, không dựa trên `top`.

#### 3. HorizontalPodAutoscaler (autoscaling/v2)

Cách nhanh nhất — lệnh imperative:
```bash
kubectl autoscale deployment web --cpu-percent=70 --min=2 --max=10 -n prod

kubectl get hpa -n prod
kubectl get hpa web -n prod -o yaml
kubectl describe hpa web -n prod       # Đọc phần Events khi nó không scale
```

Manifest đầy đủ khi đề yêu cầu nhiều metric hoặc tinh chỉnh hành vi:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web
  namespace: prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization        # % so với REQUESTS, không phải so với limits
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: AverageValue       # Giá trị tuyệt đối, không phải %
          averageValue: 500Mi
  behavior:                        # Tuỳ chọn: chống "flapping"
    scaleDown:
      stabilizationWindowSeconds: 300
```

**Công thức HPA tính số replica mong muốn:**

```text
desiredReplicas = ceil( currentReplicas × ( currentMetricValue / desiredMetricValue ) )
```

Ví dụ: 3 replica đang dùng trung bình 90% CPU, target 70% → `ceil(3 × 90/70) = ceil(3.86) = 4` replica.

#### 4. Troubleshooting HPA — bảng triệu chứng

| Triệu chứng | Nguyên nhân gốc | Cách sửa |
|---|---|---|
| `TARGETS` hiển thị `<unknown>/70%` | Container **không khai báo `resources.requests.cpu`** — HPA không có mẫu số để tính % | Thêm `requests.cpu` vào Pod template |
| `TARGETS` hiển thị `<unknown>` và `kubectl top` cũng lỗi | Metrics Server chưa cài / đang crash | `kubectl get apiservice v1beta1.metrics.k8s.io`, xem log metrics-server |
| HPA không scale dù CPU cao | Đã chạm `maxReplicas`, hoặc đang trong `stabilizationWindowSeconds` | `kubectl describe hpa` đọc mục `Conditions` + `Events` |
| Replica nhảy lên xuống liên tục | Thiếu cửa sổ ổn định | Đặt `behavior.scaleDown.stabilizationWindowSeconds` |
| HPA và `kubectl scale` đánh nhau | HPA liên tục ghi đè số replica thủ công | Đây là hành vi đúng — muốn chỉnh tay thì phải xoá/tạm dừng HPA |

> ⚠️ **Bẫy số 1 của HPA trong đề thi:** `averageUtilization` là **phần trăm của `requests`**, không phải của `limits` và cũng không phải của dung lượng node. Pod **không có `requests.cpu`** thì HPA vĩnh viễn báo `<unknown>` — đây là tình huống debug hay ra thi nhất.

#### 5. Ba loại autoscaler — đừng nhầm

| Loại | Điều chỉnh cái gì | Phạm vi |
|---|---|---|
| **HPA** (Horizontal Pod Autoscaler) | **Số lượng** Pod | Trong cluster, có sẵn, **là phần của CKA** |
| **VPA** (Vertical Pod Autoscaler) | **requests/limits** của Pod (phải restart Pod) | Add-on riêng, chỉ cần biết khái niệm |
| **Cluster Autoscaler** | **Số lượng Node** | Do cloud provider lo, chỉ cần biết khái niệm |

> 🧠 **Mẹo ghi nhớ:** **H**orizontal = **nhiều bản sao hơn**. **V**ertical = **mỗi bản sao to hơn**. **Cluster** = **nhiều máy hơn**.

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
5. [ ] `kubectl get hpa` báo `TARGETS: <unknown>/70%`. Hai nguyên nhân gốc khả dĩ nhất là gì? *(Đáp án: (1) Container **không khai báo `resources.requests.cpu`** nên HPA không có mẫu số để tính phần trăm; (2) **Metrics Server** chưa cài hoặc đang crash — kiểm tra `kubectl get apiservice v1beta1.metrics.k8s.io`).*
6. [ ] `averageUtilization: 70` trong HPA là 70% của cái gì? *(Đáp án: 70% của **`resources.requests`**, KHÔNG phải của `limits` và cũng không phải của dung lượng node).*
7. [ ] Khác nhau giữa `kubectl top node` và phần *Allocated resources* trong `kubectl describe node`? *(Đáp án: `top` = mức tiêu thụ **thực tế** đo từ kubelet/cAdvisor; `describe` = tổng **requests/limits đã đặt chỗ**. Scheduler ra quyết định dựa trên requests, không dựa trên mức dùng thật).*
8. [ ] HPA đang chạy mà bạn gõ `kubectl scale --replicas=1` thì sao? *(Đáp án: HPA sẽ ghi đè lại ở vòng đồng bộ kế tiếp. Muốn chỉnh tay phải xoá HPA trước).*
