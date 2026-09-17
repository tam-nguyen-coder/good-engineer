# ✅ Answers & Explanations — Tuần 9: Cluster Maintenance & etcd

> Mở file này sau khi đã hoàn thành 21 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 9](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-B` · `2-A` · `3-B` · `4-A` · `5-B` · `6-B` · `7-B` · `8-A` · `9-A` · `10-B` · `11-A` · `12-B` · `13-A` · `14-A` · `15-C` · `16-B` · `17-C` · `18-B` · `19-B` · `20-C` · `21-C`

---

### Question 1 — Đáp án: **B**
- **Vì sao đúng:** Trên các bản **etcdctl cũ (< v3.4)**, client mặc định trỏ về API v2 nên phải export **`export ETCDCTL_API=3`** thì mới thao tác được với database v3 của Kubernetes. Đây vẫn là đáp án đúng của câu hỏi này vì nó là biến duy nhất điều khiển phiên bản API của `etcdctl`.
- ⚠️ **Cập nhật cho môi trường thi v1.35:** Từ **etcdctl v3.4 trở đi API v3 đã là mặc định**, và cụm thi CKA hiện chạy etcd 3.5/3.6 → **bạn KHÔNG bắt buộc phải export biến này**. Gõ thêm thì vô hại, nhưng nếu đáp án mẫu hay tài liệu chính thức không có nó thì cũng đừng hoang mang.
- 🧠 **Mẹo ghi nhớ:** `ETCDCTL_API=3` = *phao cứu sinh cho etcdctl đời cũ*. Thứ **thật sự bắt buộc** trong phòng thi là bộ 4 cờ: `--endpoints`, `--cacert`, `--cert`, `--key`.

---

### Question 2 — Đáp án: **A**
- **Vì sao đúng:** Lệnh `etcdctl snapshot restore` yêu cầu một thư mục trống hoặc chưa tồn tại. Nếu bạn trỏ trực tiếp vào thư mục data đang chạy `/var/lib/etcd`, lệnh sẽ từ chối thực hiện để tránh làm hỏng database. Thao tác chuẩn: Khôi phục vào một thư mục mới (ví dụ `/var/lib/etcd-restored`) rồi sửa static pod manifest trỏ sang thư mục mới đó.
- 🧠 **Mẹo ghi nhớ:** Restore etcd **bắt buộc dùng `--data-dir` mới**!

---

### Question 3 — Đáp án: **B**
- **Vì sao đúng:** Các Pod có gắn volume kiểu `emptyDir` sẽ bị mất dữ liệu khi bị xoá khỏi node. Do đó, lệnh `kubectl drain` mặc định sẽ dừng lại để bảo vệ bạn khỏi mất dữ liệu vô ý. Thêm cờ **`--delete-emptydir-data`** để xác nhận đồng ý xoá dữ liệu tạm đó và tiếp tục drain.
- 🧠 **Mẹo ghi nhớ:** Drain dính emptyDir -> Thêm **`--delete-emptydir-data`**.

---

### Question 4 — Đáp án: **A**
- **Vì sao đúng:** Các Pod thuộc `DaemonSet` được gắn chặt vào từng node. Nếu drain đuổi nó đi thì nó cũng không thể chạy ở node khác. Do đó lệnh `kubectl drain` bắt buộc phải có cờ **`--ignore-daemonsets`** để bỏ qua và để nguyên DaemonSet pods tiếp tục chạy.
- 🧠 **Mẹo ghi nhớ:** Drain node luôn kèm **`--ignore-daemonsets`**.

---

### Question 5 — Đáp án: **B**
- **Vì sao đúng:** Quy trình nâng cấp Control Plane chuẩn bằng kubeadm:
  1. Drain node controlplane.
  2. Nâng cấp binary `kubeadm`.
  3. Chạy `kubeadm upgrade apply v1.35.0` để nâng cấp cấu hình cluster.
  4. Nâng cấp binary `kubelet` và `kubectl`.
  5. Restart service `kubelet`.
  6. Uncordon node.
- 🧠 **Mẹo ghi nhớ:** Quy trình CP: Drain -> Upgrade kubeadm -> Apply -> Upgrade kubelet/kubectl -> Restart -> Uncordon.

---

### Question 6 — Đáp án: **B**
- **Vì sao đúng:** Khác với Control Plane đầu tiên (dùng `kubeadm upgrade apply`), tất cả các Worker Nodes (và các secondary CP nodes) đều sử dụng lệnh **`kubeadm upgrade node`** để cập nhật cấu hình local.
- 🧠 **Mẹo ghi nhớ:** Nâng cấp Worker Node dùng **`kubeadm upgrade node`**.

---

### Question 7 — Đáp án: **B**
- **Vì sao đúng:** Theo chính sách Kubernetes Version Skew Policy, Kubelet trên Worker Node có thể chạy phiên bản cũ hơn API Server tối đa 2 minor versions (và lên tới 3 minor versions từ K8s v1.28 trở đi). Tuy nhiên, Kubelet **KHÔNG BAO GIỜ được phép có phiên bản cao hơn** API Server.
- 🧠 **Mẹo ghi nhớ:** Kubelet có thể thấp hơn API Server, nhưng **không bao giờ được cao hơn**.

---

### Question 8 — Đáp án: **A**
- **Vì sao đúng:**
  - `kubectl cordon`: Chỉ đổi trạng thái node sang `SchedulingDisabled`, chặn Pod mới, để nguyên Pod cũ.
  - `kubectl drain`: Vừa cordon, vừa thực hiện trục xuất (evict) toàn bộ các Pod đang chạy sang các node khác để sẵn sàng tắt máy.
- 🧠 **Mẹo ghi nhớ:** Cordon = Chặn vào; Drain = Chặn vào + Đuổi người đang ở ra.

---

### Question 9 — Đáp án: **A**
- **Vì sao đúng:** Chuẩn của `kubeadm` lưu trữ chứng chỉ etcd tại thư mục riêng biệt:
  - CA: `/etc/kubernetes/pki/etcd/ca.crt`
  - Cert: `/etc/kubernetes/pki/etcd/server.crt`
  - Key: `/etc/kubernetes/pki/etcd/server.key`
- 🧠 **Mẹo ghi nhớ:** Chứng chỉ etcd nằm tại **`/etc/kubernetes/pki/etcd/`**.

---

### Question 10 — Đáp án: **B**
- **Vì sao đúng:** Kubelet có tính năng File Watcher đối với thư mục manifest địa phương (`/etc/kubernetes/manifests/`). Khi bạn chỉnh sửa bất kỳ file nào trong thư mục này (như `etcd.yaml`), Kubelet tự động phát hiện mã băm (hash) của file thay đổi và tự động restart Pod tương ứng trong vòng vài giây mà không cần can thiệp thủ công.
- 🧠 **Mẹo ghi nhớ:** Sửa static pod YAML -> Kubelet **tự động restart pod**.

---

### Question 11 — Đáp án: **A**
- **Vì sao đúng:** Để đảm bảo tính ổn định của hạ tầng, các gói K8s trên Ubuntu luôn được đặt ở trạng thái `hold` bằng lệnh `apt-mark hold`. Khi cần nâng cấp, ta phải `unhold` để trình quản lý APT cho phép cài đặt phiên bản mới.
- 🧠 **Mẹo ghi nhớ:** Nâng cấp Ubuntu K8s: `apt-mark unhold ...` trước khi `apt install`.

---

### Question 12 — Đáp án: **B**
- **Vì sao đúng:** Lệnh `etcdctl --write-out=table snapshot status <file.db>` in ra bảng chi tiết chứa thông tin Revision, Total Keys, và Total Size của file backup, chứng minh snapshot không bị corrupt.
- 🧠 **Mẹo ghi nhớ:** Xem status snapshot: `etcdctl --write-out=table snapshot status ...`.

---

### Question 13 — Đáp án: **A**
- **Vì sao đúng:** Lệnh `kubeadm certs check-expiration` quét toàn bộ thư mục `/etc/kubernetes/pki` và hiển thị bảng hạn dùng còn lại của tất cả các chứng chỉ (apiserver, etcd, front-proxy, scheduler, controller-manager).
- 🧠 **Mẹo ghi nhớ:** Kiểm tra hạn cert: **`kubeadm certs check-expiration`**.

---

### Question 14 — Đáp án: **A**
- **Vì sao đúng:** Lệnh `kubeadm certs renew all` gia hạn tất cả các chứng chỉ nội bộ thêm 1 năm trong vòng 1 giây duy nhất.
- 🧠 **Mẹo ghi nhớ:** Gia hạn toàn bộ chứng chỉ: **`kubeadm certs renew all`**.

---

### Question 15 — Đáp án: **C**
- **Vì sao đúng:** Lệnh `kubectl uncordon <node-name>` gỡ bỏ trạng thái `SchedulingDisabled`, đưa Node trở lại trạng thái `Ready` để tiếp tục nhận các Pod mới từ Kube-scheduler.
- 🧠 **Mẹo ghi nhớ:** Bảo trì xong mở cửa lại cho Node: **`kubectl uncordon`**.

---

### Question 16 — Đáp án: **B**
- **Vì sao đúng:** Quorum của Raft là `(N/2) + 1`. Với N=3 → quorum 2 → chịu được mất **1**. Với N=4 → quorum 3 → vẫn chỉ chịu được mất **1**. Bạn tốn thêm một máy, thêm một thứ có thể hỏng, mà khả năng chịu lỗi **không đổi**. Muốn chịu được 2 lỗi thì phải lên **5** member (quorum 3).
- **Vì sao các đáp án khác sai:** **A** tính sai quorum; **C** Raft không "chia phiếu đều" — nó cần **quá bán tuyệt đối**, hoà phiếu chỉ gây bầu lại; **D** etcd không giới hạn ở 3, chỉ là 5 gần như luôn là trần thực dụng (càng nhiều member, ghi càng chậm vì phải replicate rộng hơn).
- 🧠 **Mẹo ghi nhớ:** Bảng thuộc lòng: **1→0 · 3→1 · 5→2**. Số chẵn luôn vô nghĩa.

---

### Question 17 — Đáp án: **C**
- **Vì sao đúng:** `--control-plane-endpoint` được nhúng vào **SAN của chứng chỉ API server**, vào `clusterConfiguration` trong ConfigMap `kubeadm-config`, và vào `server:` của mọi kubeconfig (`admin.conf`, `kubelet.conf`, `controller-manager.conf`, `scheduler.conf`). Không có nó, mọi thứ trỏ cứng vào IP `10.0.1.10` của node đầu tiên — node đó chết là cả cụm mất control plane, và không thể chen load balancer vào giữa. Chính vì vậy tài liệu kubeadm khuyến nghị **luôn** đặt `--control-plane-endpoint` ngay từ `init` đầu tiên, kể cả khi mới có một node.
- **Vì sao các đáp án khác sai:** **A** `kubeadm join --control-plane` sẽ thất bại vì cụm không được cấu hình cho HA; **B** sửa kubeconfig không cứu được phần SAN trong certificate; **D** `kubeadm upgrade apply` không nhận cờ đó.
- 🧠 **Mẹo ghi nhớ:** `--control-plane-endpoint` là **quyết định một lần, không quay đầu**. Luôn trỏ vào DNS/VIP, không bao giờ trỏ vào IP của một node.

---

### Question 18 — Đáp án: **B**
- **Vì sao đúng:** `kube-apiserver` **stateless** hoàn toàn — mọi state nằm ở etcd — nên cả 3 bản chạy song song và load balancer rải request tuỳ ý. Ngược lại, `kube-scheduler` và `kube-controller-manager` **bắt buộc** chỉ được có một bản hoạt động, nếu không hai scheduler sẽ cùng gán một Pod vào hai node khác nhau. Chúng dùng **leader election** qua Lease:
  ```bash
  kubectl get lease -n kube-system kube-scheduler kube-controller-manager
  kubectl get lease -n kube-system kube-scheduler -o jsonpath='{.spec.holderIdentity}{"\n"}'
  ```
- **Vì sao các đáp án khác sai:** **A** sẽ gây tranh chấp lập lịch; **C** apiserver là active-active, không phải standby; **D** leader election diễn ra **độc lập cho từng component**, không phải bầu ra một node "chủ" chạy tất cả.
- 🧠 **Mẹo ghi nhớ:** **Stateless → active-active** (apiserver). **Có quyền ra quyết định → active-passive** (scheduler, controller-manager).

---

### Question 19 — Đáp án: **B**
- **Vì sao đúng:** API server kiểm tra rất nghiêm: `metadata.name` của CRD **phải** bằng chính xác `<spec.names.plural>.<spec.group>`. Ở đây plural là `backups` nên tên đúng là `backups.ops.example.com`. Viết `backup.` (số ít) là bị từ chối với thông báo kiểu *"must be spec.names.plural+\".\"+spec.group"*.
- **Vì sao các đáp án khác sai:** **A** `kind` theo quy ước là **PascalCase** (`Backup`) — đúng như đề đã viết; **C** không có hạn chế nào về tên miền; **D** một version là đủ (miễn có đúng một version `storage: true`).
- 🧠 **Mẹo ghi nhớ:** Tên CRD = **số nhiều** + dấu chấm + group. Copy thẳng từ `spec.names.plural`, đừng gõ lại bằng tay.

---

### Question 20 — Đáp án: **C**
- **Vì sao đúng:** CRD chỉ làm đúng ba việc: **đăng ký** một kind mới với API server, **validate** object theo OpenAPI schema, và **lưu** chúng vào etcd. Nó hoàn toàn không mang theo logic nào. Muốn có hành động thật phải có **controller** watch kind đó và chạy vòng lặp reconcile. Đây là lý do một operator luôn gồm **hai phần**: bundle CRD + Deployment của controller. Cài thiếu phần thứ hai (hoặc pod của nó `CrashLoopBackOff`) sẽ cho ra đúng triệu chứng trong đề.
- **Vì sao các đáp án khác sai:** **A** `additionalPrinterColumns` chỉ làm đẹp output `kubectl get`; **B** `scope` quyết định object nằm trong namespace hay toàn cụm, không liên quan tới việc có ai xử lý nó; **D** không tồn tại annotation này.
- 🧠 **Mẹo ghi nhớ:** **CRD = cái hộp. Controller = người mở hộp.** Không người mở thì hộp cứ nằm đó.

---

### Question 21 — Đáp án: **C**
- **Vì sao đúng:** `.status` rỗng là bằng chứng rằng **chưa có controller nào chạm vào object**. Controller nào hoạt động cũng sẽ ghi ít nhất một condition vào `.status`. Trình tự truy vết đúng đi từ "ai lẽ ra phải làm việc này" ra ngoài:
  ```bash
  kubectl get pods -n <operator-ns>                     # Controller có Running không?
  kubectl logs -n <operator-ns> deploy/<controller>     # Nó báo lỗi gì? (RBAC? webhook?)
  kubectl describe <cr-kind> <name>                     # Có event nào không?
  kubectl get <cr-kind> <name> -o yaml                  # .status nói gì?
  ```
  Nguyên nhân thường gặp nhất: controller thiếu **RBAC** để watch CRD, hoặc nó đang watch một **version khác** với version bạn dùng để tạo object.
- **Vì sao các đáp án khác sai:** **A** xoá CRD sẽ **xoá sạch mọi custom object** — phá hoại chứ không phải chẩn đoán; **B** đổi giá trị trong `spec` chẳng có tác dụng gì khi không có ai đọc nó; **D** `kube-controller-manager` **không** quản lý custom resource — mỗi operator tự mang controller riêng.
- 🧠 **Mẹo ghi nhớ:** `.status` rỗng = **không ai đang lắng nghe**. Đi thẳng tới log của controller, đừng đụng vào CRD.

