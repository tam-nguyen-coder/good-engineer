# ✅ Answers & Explanations — Tuần 5: Services & Networking

> Mở file này sau khi đã hoàn thành 15 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 5](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-B` · `2-C` · `3-A` · `4-B` · `5-B` · `6-A` · `7-B` · `8-B` · `9-A` · `10-B` · `11-B` · `12-A` · `13-A` · `14-B` · `15-A`

---

### Question 1 — Đáp án: **B**
- **Vì sao đúng:** Kubernetes chỉ định sẵn dải cổng dành riêng cho Service kiểu `NodePort` là **`30000 – 32767`**. Bất kỳ cổng nào nằm ngoài dải này khi khai báo thủ công sẽ bị API Server từ chối.
- 🧠 **Mẹo ghi nhớ:** Dải NodePort chuẩn: **`30000 – 32767`**.

---

### Question 2 — Đáp án: **C**
- **Vì sao đúng:** Đối tượng `Endpoints` được tạo ra tự động dựa trên `spec.selector` của Service. Nếu giá trị selector không khớp chính xác với nhãn của Pod (ví dụ sai chữ hoa/thường, sai key), Endpoints Controller sẽ không thể tìm thấy Pod nào và cột `ENDPOINTS` sẽ hiển thị `<none>`.
- 🧠 **Mẹo ghi nhớ:** Service không gọi được Pod + Endpoints `<none>` → **Sai Label Selector**.

---

### Question 3 — Đáp án: **A**
- **Vì sao đúng:** Service có `clusterIP: None` được gọi là **Headless Service**. CoreDNS sẽ không gán IP ảo mà trả về trực tiếp bản ghi DNS kiểu A chứa danh sách toàn bộ IP của các Pod backend phía sau.
- 🧠 **Mẹo ghi nhớ:** `clusterIP: None` = Headless Service = Trả về trực tiếp IP của từng Pod.

---

### Question 4 — Đáp án: **B**
- **Vì sao đúng:** Cú pháp FQDN (Fully Qualified Domain Name) đầy đủ trong Kubernetes:
  `<service-name>.<namespace>.svc.cluster.local`.
  Với service `inventory-svc` ở namespace `warehouse`:
  `inventory-svc.warehouse.svc.cluster.local`.
- 🧠 **Mẹo ghi nhớ:** Công thức FQDN: `<svc>.<ns>.svc.cluster.local`.

---

### Question 5 — Đáp án: **B**
- **Vì sao đúng:** `iptables` là chế độ mặc định của `kube-proxy` kể từ K8s v1.2 đến nay trên phần lớn các phân phối Linux tiêu chuẩn.
- 🧠 **Mẹo ghi nhớ:** Kube-proxy mặc định chạy ở chế độ **`iptables`**.

---

### Question 6 — Đáp án: **A**
- **Vì sao đúng:** `EndpointSlices` chia nhỏ danh sách hàng ngàn endpoints thành các mảnh nhỏ (mỗi slice tối đa 100 endpoints). Nhờ đó, khi một Pod scale hoặc chết đi, K8s chỉ cần cập nhật và gửi 1 EndpointSlice nhỏ thay vì truyền tải toàn bộ danh sách khổng lồ, giảm thiểu nghẽn mạng và tải trên etcd.
- 🧠 **Mẹo ghi nhớ:** EndpointSlices = Chia nhỏ endpoints để scale lớn không quá tải etcd.

---

### Question 7 — Đáp án: **B**
- **Vì sao đúng:** Lệnh `kubectl expose deployment web-deploy --port=80 --target-port=8080 --type=ClusterIP` tự động kế thừa label selector của Deployment và tạo Service trong 1 lệnh duy nhất.
- 🧠 **Mẹo ghi nhớ:** Expose nhanh: `k expose deploy <name> --port=... --target-port=...`.

---

### Question 8 — Đáp án: **B**
- **Vì sao đúng:**
  - `port`: Cổng của Service (nơi client gửi request tới Service).
  - `targetPort`: Cổng của container bên trong Pod (nơi Service chuyển tiếp traffic vào).
- 🧠 **Mẹo ghi nhớ:** `port` = Cổng của Service; `targetPort` = Cổng của Pod.

---

### Question 9 — Đáp án: **A**
- **Vì sao đúng:** Service `type: ExternalName` không có selectors hay endpoints. Nó chỉ đơn giản trả về một bản ghi CNAME trỏ ra một tên miền bên ngoài cụm, giúp code ứng dụng có thể gọi tên service nội bộ mà vẫn trỏ ra database bên ngoài.
- 🧠 **Mẹo ghi nhớ:** `ExternalName` = CNAME alias trỏ ra dịch vụ bên ngoài.

---

### Question 10 — Đáp án: **B**
- **Vì sao đúng:** CoreDNS được quản lý dưới dạng một `Deployment` trong namespace hệ thống `kube-system`, thường có 2 replicas để đảm bảo tính sẵn sàng cao.
- 🧠 **Mẹo ghi nhớ:** CoreDNS nằm ở **`kube-system`**, quản lý bởi **`Deployment`**.

---

### Question 11 — Đáp án: **B**
- **Vì sao đúng:** Khi quy mô cụm lên tới hàng chục nghìn service, `iptables` duyệt các rules tuần tự $O(N)$ dẫn đến CPU tăng cao và độ trễ lớn. `IPVS` sử dụng IPVS kernel module với bảng băm Hash Table, cho tốc độ tra cứu $O(1)$ bất kể số lượng service lớn đến đâu.
- 🧠 **Mẹo ghi nhớ:** Quy mô siêu lớn (> 10.000 services) -> Chuyển sang **kube-proxy IPVS mode** ($O(1)$).

---

### Question 12 — Đáp án: **A**
- **Vì sao đúng:** `spec.sessionAffinity: ClientIP` kích hoạt tính năng sticky session ở tầng Layer 4, chuyển tiếp tất cả các request từ cùng một Client IP đến cùng một Pod backend trong suốt phiên làm việc.
- 🧠 **Mẹo ghi nhớ:** Sticky session ở Service: `sessionAffinity: ClientIP`.

---

### Question 13 — Đáp án: **A**
- **Vì sao đúng:** Mô hình mạng cốt lõi của Kubernetes (IP-per-Pod) quy định: Mọi Pod đều có một địa chỉ IP riêng biệt và có thể giao tiếp với mọi Pod khác trong toàn bộ cụm mà hoàn toàn KHÔNG CẦN QUA NAT.
- 🧠 **Mẹo ghi nhớ:** K8s Network Model = Pod-to-Pod **không NAT**.

---

### Question 14 — Đáp án: **B**
- **Vì sao đúng:** Service kiểu NodePort mở cổng trên **TẤT CẢ CÁC NODE** trong cụm. Nhờ có `kube-proxy`, request gửi tới bất kỳ node nào cũng sẽ tự động được định tuyến qua mạng nội bộ tới đúng Node đang chứa Pod backend.
- 🧠 **Mẹo ghi nhớ:** NodePort mở trên mọi node; Kube-proxy tự động chuyển tiếp sang node chứa Pod.

---

### Question 15 — Đáp án: **A**
- **Vì sao đúng:** CoreDNS là trái tim phân giải tên miền trong K8s. Nếu CoreDNS pods bị `Pending` hoặc `CrashLoopBackOff` (thường do lỗi CNI chưa cấp IP hoặc port 53 bị xung đột), toàn bộ cluster sẽ mất khả năng phân giải tên miền service.
- 🧠 **Mẹo ghi nhớ:** DNS hỏng -> Kiểm tra ngay Pod `coredns` trong namespace `kube-system`.
