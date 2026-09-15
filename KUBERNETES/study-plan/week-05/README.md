# 🟦 Tuần 5 — Services & Cluster Networking Core: ClusterIP, NodePort, Headless & CoreDNS

> **Domain:** Services & Networking (20%) · **Thời lượng:** ~11h (4 buổi) · **Vị trí:** Tuần 5/10
>
> **Điều hướng:** [⬅️ Tuần 4](../week-04/README.md) · [🏠 Kế hoạch tổng](../../K8S-STUDY-PLAN.md) · [Tuần 6 ➡️](../week-06/README.md) · [🧪 Bài Lab](labs.md) · [❓ Câu hỏi luyện tập](questions.md) · [💡 Đáp án chi tiết](answers.md)

---

## 🎯 Mục tiêu tuần này

- Nắm vững mô hình mạng **Kubernetes IP-per-Pod Model**: Mọi Pod có 1 IP duy nhất; mọi Pod nói chuyện với mọi Pod không qua NAT; Node nói chuyện với Pod không qua NAT.
- Phân biệt bản chất và trường hợp sử dụng của 4 loại Service: **`ClusterIP`**, **`NodePort`**, **`LoadBalancer`**, và **`Headless Service`** (`clusterIP: None`).
- Hiểu sâu mối liên hệ giữa **`Service`**, **`Endpoints`**, và **`EndpointSlices`** (cơ chế phân tán scale > 1000 pods).
- Làm chủ kiến trúc **`CoreDNS`** và cấu trúc phân giải tên miền FQDN chuẩn của Kubernetes (`<service>.<namespace>.svc.cluster.local`).
- Hiểu cách **`kube-proxy`** can thiệp vào tầng kernel bằng `iptables` hoặc `IPVS` để định tuyến lưu lượng ảo mà không tiêu tốn CPU xử lý gói tin.

---

## 📚 Nội dung học chi tiết

### 🅰️ Buổi A — Bản chất 4 loại Service trong K8s (~3h)

```text
1. ClusterIP (Nội bộ cụm)
   Client Pod --------> [ Virtual ClusterIP: 10.96.0.100 ]
                                   |
                  (Kube-proxy iptables load-balance)
                                   |
                     +-------------+-------------+
                     v                           v
              [ Pod 1 (10.244.1.5) ]      [ Pod 2 (10.244.2.8) ]

2. NodePort (Expose ra ngoài qua IP của Node: Port 30000-32767)
   External Client ----> [ Node 1 IP : 30080 ] ----> Kube-proxy ----> [ Pod Backend ]
   External Client ----> [ Node 2 IP : 30080 ] ----> Kube-proxy ----> [ Pod Backend ]

3. LoadBalancer (Tích hợp Cloud Provider: AWS NLB/ALB, GCP LB)
   Internet Client ----> [ Cloud Load Balancer ] ----> NodePort ----> ClusterIP ----> Pod

4. Headless Service (clusterIP: None)
   Client Pod --------> CoreDNS query "db-service"
                              |
               (Trả về trực tiếp danh sách Pod IPs: 10.244.1.5, 10.244.2.8)
                              |
                     Client Pod kết nối thẳng tới Pod
```

- **`Headless Service` (`clusterIP: None`):**
  - Không được cấp phát bất kỳ IP ảo nào!
  - Không có kube-proxy đứng giữa cân bằng tải.
  - Khi client truy vấn DNS tên của Headless Service, CoreDNS sẽ **trả về trực tiếp danh sách A records chứa IP thực của tất cả các Pod backend**. Dành riêng cho `StatefulSet` để client tự chọn node Master/Replica.

---

### 🅱️ Buổi B — Endpoints, EndpointSlices & CoreDNS (~3.5h)

#### 1. Endpoints & EndpointSlices
- Khi tạo một Service có `spec.selector`:
  - Kubernetes Endpoint Controller sẽ tự động tìm tất cả các Pod thoả mãn selector đó và tạo một đối tượng **`Endpoints`** cùng tên, chứa IP và Port của các Pod này.
  - Từ K8s 1.21+, **`EndpointSlices`** trở thành mặc định, chia nhỏ danh sách endpoint thành từng nhóm tối đa 100 endpoints để tránh quá tải etcd và network traffic khi service có hàng ngàn Pods.
- **Kỹ năng gỡ lỗi hàng đầu:** Nếu Service không gọi được Pod → Chạy `kubectl get ep <svc-name>`. Nếu cột Endpoints rỗng (`<none>`), 99% nguyên nhân là do **Label Selector trên Service viết sai chính tả, không khớp với Labels của Pod**!

#### 2. CoreDNS FQDN (Fully Qualified Domain Name)
Định dạng tên miền chuẩn mực trong K8s:
- Truy vấn Service trong **CÙNG Namespace**: Chỉ cần gọi tên service: `http://backend-svc`
- Truy vấn Service ở **Namespace KHÁC**: Gọi dạng `<svc-name>.<namespace>`: `http://backend-svc.development`
- FQDN đầy đủ (truy vấn chuẩn tuyệt đối): `<svc-name>.<namespace>.svc.cluster.local`
- Truy vấn Pod trực tiếp (Headless): `<pod-ip-thay-dấu-chấm-bằng-gạch>.<namespace>.pod.cluster.local` (ví dụ: `10-244-1-15.default.pod.cluster.local`).

---

### 🅲 Buổi C — kube-proxy & CNI Fundamentals (~2.5h)

- **`kube-proxy` modes:**
  - **iptables mode (Mặc định):** Sử dụng các chuỗi (chains) `KUBE-SERVICES`, `KUBE-SVC-XXX`, `KUBE-SEP-XXX` trong iptables với thuật toán chọn ngẫu nhiên (`-m statistic --mode random`) để cân bằng tải. Nhược điểm: Chậm khi có trên 10,000 services vì iptables duyệt tuần tự O(N).
  - **IPVS mode:** Sử dụng bảng băm trong Linux kernel (Hash table), độ phức tạp O(1), hỗ trợ nhiều thuật toán cân bằng tải hơn (round-robin, least connections).
- **CNI (Container Network Interface):**
  - K8s không tự cấp IP cho Pod! Việc này do plugin CNI (như Calico, Flannel, AWS VPC CNI, Cilium) đảm nhiệm.
  - Cài đặt plugin CNI vào thư mục `/etc/cni/net.d/` và `/opt/cni/bin/`.

---

### 🅳 Buổi D — Practice & Review (~2h)

- Hoàn thành toàn bộ bài tập trong [labs.md](labs.md): Tạo Service ClusterIP, NodePort, Headless Service; dùng Pod debug CoreDNS.

---

## 🚪 Cổng tự kiểm tra Tuần 5 (Self-check Gate)

1. [ ] Dải cổng mặc định của Service kiểu `NodePort` trong Kubernetes là bao nhiêu? *(Đáp án: `30000 – 32767`).*
2. [ ] Nếu chạy `kubectl get endpoints my-svc` mà thấy giá trị `<none>`, bạn cần kiểm tra điều gì đầu tiên? *(Đáp án: Kiểm tra `spec.selector` của Service có khớp chính xác với `metadata.labels` của các Pods hay không).*
3. [ ] Cú pháp FQDN đầy đủ để một Pod ở namespace `prod` gọi tới service `auth-service` ở namespace `security` là gì? *(Đáp án: `auth-service.security.svc.cluster.local`).*
4. [ ] Khác biệt lớn nhất khi truy vấn DNS của Service thường vs Headless Service là gì? *(Đáp án: Service thường trả về 1 IP ảo (ClusterIP); Headless Service trả về danh sách IP thực của tất cả các Pod backend).*
