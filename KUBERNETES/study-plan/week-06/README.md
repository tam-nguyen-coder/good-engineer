# 🟨 Tuần 6 — Ingress, Gateway API & Network Policies: L7 Routing & Pod Microsegmentation

> **Domain:** Services & Networking (20%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 6/10 (Checkpoint giữa kỳ)
>
> **Điều hướng:** [⬅️ Tuần 5](../week-05/README.md) · [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [Tuần 7 ➡️](../week-07/README.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Phân biệt rõ **Ingress Controller** (tiến trình thực thi chạy trong cluster, ví dụ Nginx/Traefik) và **Ingress Resource** (file cấu hình YAML định tuyến Layer 7).
- Viết thành thạo Ingress Resource cấu hình **Host-based routing** (`app.example.com` vs `api.example.com`), **Path-based routing** (`/v1` vs `/v2`), và **TLS Termination** sử dụng TLS Secret.
- Làm quen với **Kubernetes Gateway API (GA v1.0+)**: Hiểu mô hình phân tách trách nhiệm giữa Hạ tầng (`GatewayClass`), Quản trị mạng (`Gateway`), và Lập trình viên (`HTTPRoute`).
- Làm chủ **NetworkPolicy**: Hiểu cơ chế `Default Deny All`, cấu hình chính sách lọc Ingress và Egress bằng `podSelector`, `namespaceSelector`, và `ipBlock`.
- 🎯 **VƯỢT QUA CHECKPOINT MINI-MOCK 1 (Đạt ≥ 75%):** Khảo sát toàn diện kiến thức Tuần 1 đến Tuần 6.

---

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Ingress Resources & TLS Termination (~3h)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-host-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: / # Annotation rewrite path
spec:
  ingressClassName: nginx # Chỉ định Controller tiếp nhận
  tls:
  - hosts:
    - "portal.example.com"
    - "api.example.com"
    secretName: wildcard-tls-secret # Secret type kubernetes.io/tls
  rules:
  - host: "portal.example.com"
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: portal-service
            port:
              number: 80
  - host: "api.example.com"
    http:
      paths:
      - path: /users
        pathType: Exact
        backend:
          service:
            name: user-service
            port:
              number: 8080
```

- **Mẹo phòng thi Ingress:**
  - Luôn sử dụng API chuẩn: `apiVersion: networking.k8s.io/v1` (tuyệt đối không dùng `extensions/v1beta1` cũ).
  - Trường `pathType` là **bắt buộc**: chọn `Prefix` (khớp tiền tố) hoặc `Exact` (khớp chính xác tuyệt đối).
  - Lệnh sinh Ingress nhanh:
    ```bash
    kubectl create ingress simple-ing --rule="foo.com/bar=my-svc:8080" $do > ing.yaml
    ```

---

### 🅱️ Buổi B — Kubernetes Gateway API (Chuẩn thế hệ mới) (~3.5h)

Gateway API ra đời để giải quyết sự hạn chế của Ingress (vốn phụ thuộc quá nhiều vào các annotations không chuẩn hoá giữa các nhà cung cấp):

```text
+--------------------------------------------------------------+
| Infra Provider (Cloud/Admin) -> Tạo [ GatewayClass ]         |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
| Cluster Operator / DevOps   -> Tạo [ Gateway ]               |
|                                (IP, Cổng 80/443, TLS Certs)  |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
| App Developer (Team A, B)   -> Tạo [ HTTPRoute / GRPCRoute ] |
|                                (Match Header, Path, Split %) |
+--------------------------------------------------------------+
```

- **`GatewayClass`**: Định nghĩa loại bộ điều khiển (ví dụ: `cilium`, `istio`, `envoy`).
- **`Gateway`**: Cấp phát điểm tiếp nhận lưu lượng (IP, Port, Protocol).
- **`HTTPRoute`**: Định nghĩa luật định tuyến chi tiết, hỗ trợ Canary Deployment (traffic weight splitting: 90% v1 / 10% v2) ngay trong cấu hình chuẩn mà không cần tool ngoài.

---

### 🅲 Buổi C — NetworkPolicy: Pod Microsegmentation (~2.5h)

```text
               +--------------------------------------+
               |          Target Pod: db-pod          |
               |       (labels: role=database)        |
               +--------------------------------------+
                                  ^
                                  | (INGRESS)
                 +----------------+----------------+
                 |                                 |
                 | [ALLOW]                         | [DROP]
                 |                                 |
       [ frontend-pod ]                   [ any-other-pod ]
    (labels: role=frontend)              (Không có nhãn đúng)
```

#### 1. Quy tắc Default Deny All Ingress
Khi áp dụng file sau, TẤT CẢ traffic đi vào các Pod trong namespace sẽ bị chặn sạch:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all-ingress
  namespace: secure-zone
spec:
  podSelector: {} # Áp dụng cho mọi Pod trong namespace
  policyTypes:
  - Ingress
```

#### 2. Phân biệt AND vs OR trong NetworkPolicy (Bẫy đề thi CKA kinh điển!)
- **Trường hợp 1: Điều kiện OR (2 dấu gạch đầu dòng riêng biệt):**
  ```yaml
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          team: dev
    - podSelector:
        matchLabels:
          role: frontend
  ```
  *(Cho phép traffic từ bất kỳ Pod nào thuộc namespace có nhãn team=dev **HOẶC** từ Pod có nhãn role=frontend trong cùng namespace).*

- **Trường hợp 2: Điều kiện AND (Chung 1 dấu gạch đầu dòng):**
  ```yaml
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          team: dev
      podSelector:
        matchLabels:
          role: frontend
  ```
  *(Chỉ cho phép traffic từ Pod CÓ NHÃN role=frontend VÀ ĐỒNG THỜI PHẢI NẰM TRONG namespace có nhãn team=dev).*

---

### 🅳 Buổi D — Mini-mock Checkpoint 1 (~2h)

- Kiểm tra tổng hợp kiến thức từ Tuần 1 đến Tuần 6:
  - Cấu hình Deployment + RollingUpdate.
  - Tạo Ingress có TLS.
  - Thiết lập NetworkPolicy khóa chặt Database Pod.
  - **Yêu cầu vượt qua:** Hoàn thành 5 bài test trong [labs.md](labs.md) dưới 40 phút với tỉ lệ đúng ≥ 75%.

---

## 🚪 Cổng tự kiểm tra Tuần 6 (Self-check Gate)

1. [ ] Nếu cụm Kubernetes sử dụng CNI plugin là Flannel (bản thuần), NetworkPolicy có hoạt động được không? *(Đáp án: KHÔNG. Flannel không hỗ trợ NetworkPolicy. Cần dùng Calico, Cilium hoặc kết hợp Flannel + Canal).*
2. [ ] Trong cấu hình Ingress v1, trường `pathType` hỗ trợ những giá trị nào? *(Đáp án: `Prefix`, `Exact`, `ImplementationSpecific`).*
3. [ ] Làm sao để chỉ định điều kiện AND giữa `namespaceSelector` và `podSelector` trong NetworkPolicy? *(Đáp án: Khai báo cả 2 selector dưới cùng 1 mục gạch đầu dòng `-` duy nhất).*
