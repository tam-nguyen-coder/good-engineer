# ✅ Answers & Explanations — Tuần 6: Ingress & NetworkPolicies

> Mở file này sau khi đã hoàn thành 15 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 6](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-A` · `2-A` · `3-A` · `4-A` · `5-B` · `6-B` · `7-B` · `8-C` · `9-B` · `10-B` · `11-B` · `12-A` · `13-A` · `14-A` · `15-B`

---

### Question 1 — Đáp án: **A**
- **Vì sao đúng:** Kể từ bản v1.22+, API `extensions/v1beta1` và `networking.k8s.io/v1beta1` đã bị loại bỏ hoàn toàn. Bắt buộc phải sử dụng **`apiVersion: networking.k8s.io/v1`**.
- 🧠 **Mẹo ghi nhớ:** Ingress hiện đại luôn là **`networking.k8s.io/v1`**.

---

### Question 2 — Đáp án: **A**
- **Vì sao đúng:** Chuẩn Ingress v1 chỉ hỗ trợ 3 giá trị `pathType`:
  - `Prefix`: Khớp theo tiền tố đường dẫn (ví dụ `/foo` khớp với `/foo`, `/foo/bar`).
  - `Exact`: Khớp chính xác tuyệt đối từng ký tự.
  - `ImplementationSpecific`: Tuỳ thuộc vào Ingress Controller xử lý.
- 🧠 **Mẹo ghi nhớ:** Ingress pathType: `Prefix`, `Exact`, `ImplementationSpecific`.

---

### Question 3 — Đáp án: **A**
- **Vì sao đúng:** Để kích hoạt Default Deny Ingress: đặt `podSelector: {}` (chọn mọi Pod trong namespace) và `policyTypes: ["Ingress"]`. Vì không khai báo bất kỳ rule nào trong mảng `ingress:`, Kubernetes sẽ chặn sạch toàn bộ lưu lượng đi vào.
- 🧠 **Mẹo ghi nhớ:** Default Deny All Ingress = `podSelector: {}` + `policyTypes: ["Ingress"]` (không có rule ingress).

---

### Question 4 — Đáp án: **A**
- **Vì sao đúng:** Flannel là CNI plugin đời đầu, chỉ chịu trách nhiệm cấp phát mạng overlay IP đơn giản và **hoàn toàn KHÔNG hỗ trợ NetworkPolicy**. Để NetworkPolicy hoạt động, bắt buộc phải dùng các CNI có hỗ trợ như Calico, Cilium, hoặc cài thêm daemon Canal.
- 🧠 **Mẹo ghi nhớ:** Flannel thuần **không hỗ trợ NetworkPolicy**.

---

### Question 5 — Đáp án: **B**
- **Vì sao đúng:** Chuẩn TLS Secret của Kubernetes có `type: kubernetes.io/tls`. Nó chứa 2 key bắt buộc: `tls.crt` (chứng chỉ) và `tls.key` (private key).
- 🧠 **Mẹo ghi nhớ:** Secret cho TLS Ingress = **`kubernetes.io/tls`**.

---

### Question 6 — Đáp án: **B**
- **Vì sao đúng:** Trong YAML, mỗi dấu gạch đầu dòng `-` đại diện cho một phần tử độc lập trong mảng. Khi `namespaceSelector` và `podSelector` nằm trên 2 dấu gạch `-` khác nhau, chúng là 2 phần tử riêng biệt trong danh sách `from`, tức là quan hệ **HOẶC (OR)**.
- 🧠 **Mẹo ghi nhớ:** Hai dấu gạch `-` riêng biệt = **Quan hệ OR**.

---

### Question 7 — Đáp án: **B**
- **Vì sao đúng:** Khi gộp `namespaceSelector` và `podSelector` vào chung **MỘT dấu gạch đầu dòng `-` duy nhất**, chúng trở thành các thuộc tính của cùng một đối tượng lọc, tạo thành quan hệ **VÀ (AND)**.
- 🧠 **Mẹo ghi nhớ:** Chung một dấu gạch `-` = **Quan hệ AND**.

---

### Question 8 — Đáp án: **C**
- **Vì sao đúng:** Trong Kubernetes Gateway API, đối tượng **`HTTPRoute`** (hoặc `GRPCRoute`, `TCPRoute`) được sinh ra dành riêng cho Application Developer để định cấu hình các luật ứng dụng cụ thể mà không cần can thiệp vào tầng hạ tầng mạng.
- 🧠 **Mẹo ghi nhớ:** App Developer trong Gateway API -> Dùng **`HTTPRoute`**.

---

### Question 9 — Đáp án: **B**
- **Vì sao đúng:** Đối tượng `Gateway` quản lý điểm tiếp nhận lưu lượng (IP, Port, TLS certificates) và thường do Cluster Operator / DevOps Engineer phụ trách.
- 🧠 **Mẹo ghi nhớ:** Cluster Operator quản lý **`Gateway`**; Infra Provider quản lý **`GatewayClass`**.

---

### Question 10 — Đáp án: **B**
- **Vì sao đúng:** Ingress Resource chỉ là dữ liệu cấu hình trong etcd. Nó hoàn toàn vô dụng nếu không có **Ingress Controller** (như ingress-nginx) chạy ngầm để đọc cấu hình đó và cấu hình bộ load balancer thật sự bên dưới.
- 🧠 **Mẹo ghi nhớ:** Ingress Resource = Bản thiết kế; Ingress Controller = Đội thợ thi công.

---

### Question 11 — Đáp án: **B**
- **Vì sao đúng:** Đây là một trong những cạm bẫy gây mất điểm nhiều nhất bài thi CKA! Khi bạn khai báo `policyTypes: ["Egress"]`, Kubernetes lập tức chuyển Pod sang trạng thái Isolated ở chiều gửi ra. Nếu bạn chỉ mở cổng database mà quên mở cổng 53 (DNS), Pod sẽ không thể hỏi CoreDNS IP của database là gì, dẫn đến lỗi kết nối.
- 🧠 **Mẹo ghi nhớ:** Cấu hình Egress luôn nhớ **mở cổng 53 (UDP/TCP)** cho CoreDNS!

---

### Question 12 — Đáp án: **A**
- **Vì sao đúng:** `nginx.ingress.kubernetes.io/rewrite-target: /` là annotation kinh điển của Nginx Ingress Controller để viết lại URL trước khi chuyển tiếp tới backend service.
- 🧠 **Mẹo ghi nhớ:** Rewrite URL Ingress: `nginx.ingress.kubernetes.io/rewrite-target`.

---

### Question 13 — Đáp án: **A**
- **Vì sao đúng:** Thuộc tính `ipBlock` hỗ trợ trường `cidr` để chỉ định dải mạng và trường `except: []` để loại trừ các địa chỉ IP hoặc dải mạng con bên trong.
- 🧠 **Mẹo ghi nhớ:** Lọc IP NetworkPolicy: `ipBlock.cidr` và `ipBlock.except`.

---

### Question 14 — Đáp án: **A**
- **Vì sao đúng:** Ingress v1 chuẩn hoá việc liên kết với Controller thông qua trường `spec.ingressClassName` (ví dụ `ingressClassName: nginx` hoặc `traefik`).
- 🧠 **Mẹo ghi nhớ:** Chọn Ingress Controller -> Điền **`spec.ingressClassName`**.

---

### Question 15 — Đáp án: **B**
- **Vì sao đúng:** Mặc định trong Kubernetes, mọi Pod mới tạo đều ở trạng thái **Non-isolated**. Chúng có thể tự do nhận lưu lượng từ mọi Pod khác và gửi lưu lượng đi bất cứ đâu. Pod chỉ chuyển sang trạng thái **Isolated** khi có ít nhất một NetworkPolicy chọn (select) nó.
- 🧠 **Mẹo ghi nhớ:** Chưa có NetworkPolicy = **Non-isolated (Mở tự do)**; Được chọn bởi NetworkPolicy = **Isolated (Bị khoá và lọc)**.
