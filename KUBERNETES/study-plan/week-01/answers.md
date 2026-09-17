# ✅ Answers & Explanations — Tuần 1: Kiến trúc K8s & `kubectl` Imperative

> Mở file này sau khi bạn đã tự mình làm hết 20 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 1](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-B` · `2-B` · `3-C` · `4-B` · `5-C` · `6-B` · `7-B` · `8-B` · `9-C` · `10-A` · `11-C` · `12-AC` · `13-B` · `14-B` · `15-B` · `16-B` · `17-B` · `18-B` · `19-C` · `20-A` · `21-B` · `22-C` · `23-B`

---

### Question 1 — Đáp án: **B**
- **Vì sao đúng:** `kube-scheduler` chỉ chịu trách nhiệm tìm node thích hợp và gán `nodeName` cho các Pod mới được tạo. Các Pod hiện tại đã được gán Node và đang chạy trực tiếp dưới sự quản lý của `kubelet` trên worker node nên hoàn toàn **không bị ảnh hưởng**. Tuy nhiên, các Pod mới sinh ra sẽ không có ai gán node và bị kẹt vô thời hạn ở trạng thái `Pending`.
- **Vì sao các đáp án khác sai:**
  - A sai vì Worker Node độc lập chạy container, không phụ thuộc vào scheduler.
  - C sai vì Kubelet không có chức năng tự chọn node thay cho scheduler.
  - D sai vì API Server vẫn hoạt động bình thường, `kubectl get pods` vẫn trả về mã 200 OK.
- 🧠 **Mẹo ghi nhớ / Bẫy đề:** "Scheduler chết" → Pod cũ chạy bình thường, **Pod mới kẹt `Pending`**.

---

### Question 2 — Đáp án: **B**
- **Vì sao đúng:** `etcd` sử dụng thuật toán đồng thuận Raft, yêu cầu phải có đa số phiếu (Quorum) để duy trì hoạt động ghi: `Quorum = (N/2) + 1` (lấy phần nguyên). Với cụm 5 node: `Quorum = (5/2) + 1 = 2 + 1 = 3 node`. Để duy trì tối thiểu 3 node hoạt động, số node tối đa có thể chết cùng lúc là `5 - 3 = 2 node`.
- **Vì sao các đáp án khác sai:** Nếu chết 3 node, cụm chỉ còn 2 node (< 3), mất Quorum và etcd chuyển sang chế độ Read-only.
- 🧠 **Mẹo ghi nhớ / Bẫy đề:** Cụm 3 node chịu chết **1**; cụm 5 node chịu chết **2**; cụm 7 node chịu chết **3**. Luôn chọn số node lẻ!

---

### Question 3 — Đáp án: **C**
- **Vì sao đúng:** `kubelet` là thành phần DUY NHẤT trên Worker Node giao tiếp trực tiếp với Container Runtime (containerd, CRI-O) qua Container Runtime Interface (CRI) Unix socket.
- **Vì sao các đáp án khác sai:**
  - `kube-proxy` chỉ quản lý networking/iptables.
  - `kube-apiserver` và `kube-controller-manager` chạy trên Control Plane và không tương tác trực tiếp với runtime trên worker.
- 🧠 **Mẹo ghi nhớ:** Kubelet = "Quản đốc công trường" trên Node, người duy nhất ra lệnh cho runtime tạo/xóa container.

---

### Question 4 — Đáp án: **B**
- **Vì sao đúng:** Khi sự kiện ghi `0/3 nodes are available: 3 Insufficient memory`, đây là thông báo từ `kube-scheduler` trong pha lọc (Filtering/Predicates). Không có node nào có lượng bộ nhớ khả dụng (allocatable memory trừ đi tổng requests của các pod đang chạy) đủ để đáp ứng mức `requests.memory` được yêu cầu trong PodSpec.
- **Vì sao các đáp án khác sai:**
  - A & C sai vì Pod chưa hề được gán vào Node nên container chưa khởi động, không thể bị OOMKilled.
  - D sai vì thiếu memory chứ không phải disk-pressure.
- 🧠 **Mẹo ghi nhớ:** `Pending` + `0/X nodes available` → **Bị chặn ở tầng Scheduler** do vi phạm Requests, Taints hoặc NodeSelector.

---

### Question 5 — Đáp án: **C**
- **Vì sao đúng:** Các container trong `initContainers` chạy tuần tự và **bắt buộc phải kết thúc thành công với Exit Code 0**. Nếu bất kỳ init container nào bị lỗi (Exit Code khác 0), Kubelet sẽ không khởi động các container tiếp theo mà sẽ restart lại init container đó theo `restartPolicy` của Pod.
- **Vì sao các đáp án khác sai:**
  - A & B sai vì init container là điều kiện tiên quyết, không bao giờ bị bỏ qua.
  - D sai vì Kubelet không tự xoá Pod, chỉ restart container.
- 🧠 **Mẹo ghi nhớ:** Init Container = "Người dọn đường", phải chạy xong 100% không lỗi thì mới đến lượt container chính.

---

### Question 6 — Đáp án: **B**
- **Vì sao đúng:** Kể từ Kubernetes v1.28 (beta) và v1.29 (GA), Native Sidecars được triển khai bằng cách đặt container vào danh sách `initContainers[]` và bổ sung thêm thuộc tính **`restartPolicy: Always`**.
- **Vì sao các đáp án khác sai:**
  - A, C, D là các cú pháp không tồn tại trong chuẩn Kubernetes API.
- 🧠 **Mẹo ghi nhớ:** Native Sidecar = `initContainers` + `restartPolicy: Always`.

---

### Question 7 — Đáp án: **B**
- **Vì sao đúng:** Cú pháp `--dry-run=client -o yaml` yêu cầu `kubectl` chỉ format đối tượng ở phía client mà không gửi request tạo lên cluster, kết hợp `>` để chuyển hướng output ra file. Đây là kỹ năng vàng trong phòng thi CKA.
- **Vì sao các đáp án khác sai:**
  - A sẽ gửi lệnh tạo Pod thật lên cluster.
  - C cờ `--export` đã bị loại bỏ từ các bản K8s cũ.
  - D chỉ dùng được khi Pod đã tồn tại.
- 🧠 **Mẹo ghi nhớ:** Công thức bất tử phòng thi: `k run <name> --image=<img $do > file.yaml`.

---

### Question 8 — Đáp án: **B**
- **Vì sao đúng:** Static Pod do Kubelet tự quản lý. Kubelet sẽ tự động tạo một "Mirror Pod" tương ứng trên API Server để hiển thị thông tin, và tên của nó luôn tự động có hậu tố `-<node-name>`.
- **Vì sao các đáp án khác sai:**
  - A sai vì Scheduler hoàn toàn không can thiệp vào Static Pod.
  - C sai vì nếu xoá Mirror Pod bằng kubectl, Kubelet sẽ đọc file local và tự tái tạo lại ngay lập tức.
  - D sai vì Static Pod gắn chặt vào file hệ thống của Node đó.
- 🧠 **Mẹo ghi nhớ:** Muốn xoá vĩnh viễn Static Pod → Phải SSH vào Node và xoá file YAML trong `/etc/kubernetes/manifests/`.

---

### Question 9 — Đáp án: **C**
- **Vì sao đúng:** `kube-proxy` lắng nghe các Service và Endpoints từ API server, sau đó ghi các quy tắc vào `iptables` hoặc bảng băm `IPVS` trên Linux kernel của Node để thực hiện dịch địa chỉ mạng (DNAT) từ ClusterIP ảo sang IP thật của Pod.
- **Vì sao các đáp án khác sai:**
  - A do CNI plugin phụ trách.
  - B do CoreDNS phụ trách.
  - D do Service Mesh hoặc PKI phụ trách.
- 🧠 **Mẹo ghi nhớ:** Kube-proxy = "Bộ định tuyến iptables/IPVS" trên từng node.

---

### Question 10 — Đáp án: **A**
- **Vì sao đúng:** Cú pháp vòng lặp JSONPath chuẩn: `{range .items[*]}{.metadata.name}{"\t"}{.status.podIP}{"\n"}{end}`.
- **Vì sao các đáp án khác sai:**
  - B sai vì cú pháp JSONPath không hỗ trợ truy cập thuộc tính mảng trực tiếp như vậy.
  - C dùng `custom-columns` chứ không phải `jsonpath`.
  - D sai cú pháp.
- 🧠 **Mẹo ghi nhớ:** Vòng lặp JSONPath trong K8s luôn bắt đầu bằng `{range .items[*]}` và kết thúc bằng `{end}`.

---

### Question 11 — Đáp án: **C**
- **Vì sao đúng:** `kubelet` gọi `containerd` trực tiếp trên máy thông qua socket nội bộ Unix Domain Socket (`/run/containerd/containerd.sock`) mà không đi qua mạng hay API Server.
- **Vì sao các đáp án khác sai:**
  - Scheduler, Controller Manager, Kubectl đều phải đi qua `kube-apiserver`. Không thành phần nào được phép truy cập trực tiếp `etcd` ngoại trừ API Server.
- 🧠 **Mẹo ghi nhớ:** Cửa ngõ duy nhất vào `etcd` là **`kube-apiserver`**. Mọi thành phần đều chỉ nói chuyện với API Server.

---

### Question 12 — Đáp án: **A, C**
- **Vì sao đúng:** Thứ tự xử lý tại API Server:
  1. **Authentication** (bạn là ai?) ->
  2. **Authorization** (bạn có quyền không?) ->
  3. **Mutating Admission Controllers** (sửa đổi request, inject sidecar, default values) ->
  4. Schema Validation ->
  5. **Validating Admission Controllers** (kiểm tra tính hợp lệ cuối cùng) ->
  6. Lưu vào **etcd**.
- **Vì sao các đáp án khác sai:** B sai vì Mutating chạy trước để Validating có thể kiểm tra dữ liệu sau cùng. D sai vì chỉ khi pass hết kiểm tra mới được ghi vào etcd. E sai thứ tự.
- 🧠 **Mẹo ghi nhớ:** "Xác thực danh tính trước (AuthN), Phân quyền sau (AuthZ), Sửa đổi trước (Mutate), Thẩm định sau (Validate)".

---

### Question 13 — Đáp án: **B**
- **Vì sao đúng:** Exit Code trong Linux: `128 + Signal Number`. Tín hiệu `SIGKILL` có mã số là `9` -> `128 + 9 = 137`. Trong Kubernetes, mã 137 hầu như luôn đồng nghĩa với việc tiến trình bị Linux OOM Killer tiêu diệt vì vượt quá giới hạn RAM (`limits.memory`).
- **Vì sao các đáp án khác sai:**
  - A thường là Exit Code 1 hoặc 2.
  - C là mã 143 (`128 + 15` SIGTERM).
- 🧠 **Mẹo ghi nhớ:** Exit Code **137 = OOMKilled**; Exit Code **143 = Graceful Shutdown**.

---

### Question 14 — Đáp án: **B**
- **Vì sao đúng:** Vòng lặp điều khiển của ReplicaSet (nằm trong `kube-controller-manager`) chịu trách nhiệm duy trì số lượng bản sao mong muốn. Nếu Controller Manager chết, API Server vẫn nhận lệnh xoá Pod và xoá thành công, nhưng không có ai phát hiện ra sự thiếu hụt để ra lệnh tạo Pod mới bù lại.
- **Vì sao các đáp án khác sai:** A sai vì API server vẫn sống và xoá bình thường. D sai vì Kubelet không quản lý logic số lượng bản sao của Deployment.
- 🧠 **Mẹo ghi nhớ:** Controller Manager = "Người duy trì trạng thái Desired State".

---

### Question 15 — Đáp án: **B**
- **Vì sao đúng:** Lệnh `kubectl create deployment` hỗ trợ đầy đủ các cờ `--image`, `--replicas` và `-n`.
- **Vì sao các đáp án khác sai:**
  - A sai vì `kubectl run` chỉ tạo **1 Pod đơn lẻ**, không hỗ trợ cờ `--replicas` (trước v1.18 có hỗ trợ nhưng đã bị bỏ).
  - C & D sai cú pháp lệnh kubectl.
- 🧠 **Mẹo ghi nhớ:** Muốn tạo Deployment có replicas dùng `kubectl create deployment`, không dùng `kubectl run`.

---

### Question 16 — Đáp án: **B**
- **Vì sao đúng:** Volume kiểu `emptyDir: {}` được tạo ra khi Pod được gán vào Node, tồn tại suốt vòng đời của Pod và được chia sẻ an toàn giữa tất cả các container trong Pod đó mà không phụ thuộc vào hạ tầng bên ngoài.
- **Vì sao các đáp án khác sai:**
  - A `hostPath` tiềm ẩn rủi ro bảo mật và để lại rác trên Node.
  - C NFS quá cồng kềnh cho nhu cầu file tạm.
  - D ConfigMap không dùng cho việc ghi dữ liệu tạm thời giữa các container.
- 🧠 **Mẹo ghi nhớ:** Chia sẻ file tạm giữa các container trong 1 Pod → **`emptyDir`**.

---

### Question 17 — Đáp án: **B**
- **Vì sao đúng:** Khi một Pod bị xoá, Kubelet gửi tín hiệu `SIGTERM` cho ứng dụng để nó đóng các kết nối dang dở (graceful shutdown). Kubelet sẽ đếm ngược thời gian bằng `terminationGracePeriodSeconds` (mặc định 30s). Nếu hết thời gian mà container vẫn chưa tắt, Kubelet sẽ gửi `SIGKILL` để tiêu diệt cưỡng bức.
- 🧠 **Mẹo ghi nhớ:** `terminationGracePeriodSeconds` = Thời gian ân hạn từ `SIGTERM` đến `SIGKILL` (mặc định 30s).

---

### Question 18 — Đáp án: **B**
- **Vì sao đúng:** Chuẩn của `kubeadm` lưu toàn bộ CA, server certificates, service account key pair tại thư mục `/etc/kubernetes/pki` (và etcd certs tại `/etc/kubernetes/pki/etcd`).
- 🧠 **Mẹo ghi nhớ:** Chứng chỉ K8s luôn nằm tại **`/etc/kubernetes/pki`**.

---

### Question 19 — Đáp án: **C**
- **Vì sao đúng:** Lệnh `kubectl config set-context --current --namespace=<name>` sửa đổi context hiện tại trong kubeconfig, chuyển namespace mặc định của tất cả các câu lệnh tiếp theo sang namespace mong muốn.
- **Vì sao các đáp án khác sai:** A, B, D là các lệnh không tồn tại trong kubectl chính thức (chỉ có trong tool ngoài như kubens).
- 🧠 **Mẹo ghi nhớ:** Muốn đổi namespace làm việc trong bài thi: `k config set-context --current --namespace=...`.

---

### Question 20 — Đáp án: **A**
- **Vì sao đúng:** Ambassador container đóng vai trò như một proxy đại diện cho container chính, giúp container chính chỉ cần kết nối tới `localhost` mà không cần biết logic phức tạp bên ngoài (như kết nối tới Redis cluster hay Cloud SQL proxy).
- **Vì sao các đáp án khác sai:**
  - B là mô hình Adapter Container.
  - C là nhiệm vụ của PreStop hook.
  - D là nhiệm vụ của Init Container.
- 🧠 **Mẹo ghi nhớ:**
  - **Sidecar:** Mở rộng/hỗ trợ (ghi log, sync dữ liệu).
  - **Adapter:** Chuẩn hoá output (format log/metrics).
  - **Ambassador:** Đại sứ kết nối mạng ra bên ngoài (proxy).

---

### Question 21 — Đáp án: **B**
- **Vì sao đúng:** Thông điệp `cni plugin not initialized` đến **thẳng từ kubelet** khi nó không tìm thấy một cấu hình CNI hợp lệ. Kubelet coi node là `NotReady` cho tới khi mạng Pod sẵn sàng. Trình tự kiểm tra:
  1. `ls /etc/cni/net.d/` — có file `*.conflist` không? (rỗng = chưa cài CNI)
  2. `ls /opt/cni/bin/` — có binary plugin không?
  3. `kubectl get pods -n kube-system -o wide | grep -Ei 'calico|cilium|flannel'` — DaemonSet CNI trên node đó có Running không?
- **Vì sao các đáp án khác sai:** **A** lỗi CRI sẽ báo về runtime/socket chứ không nhắc "network plugin"; **C** CSI chỉ liên quan tới volume; **D** device plugin không làm node `NotReady`.
- 🧠 **Mẹo ghi nhớ:** Node `NotReady` + chữ **`cni`** trong log = mạng, không phải kubelet. Nhìn `/etc/cni/net.d/` trước tiên.

---

### Question 22 — Đáp án: **C**
- **Vì sao đúng:** `NetworkPolicy` chỉ là **bản khai báo ý định** lưu trong etcd. Người *thực thi* nó là CNI plugin. Flannel thuần chỉ làm nhiệm vụ cấp IP và overlay, **không** implement NetworkPolicy — nên policy được API server chấp nhận nhưng không có ai áp dụng. Muốn có hiệu lực phải dùng CNI hỗ trợ: **Calico**, **Cilium**, Antrea, Weave Net (hoặc chạy Calico policy-only chồng lên Flannel, tức "Canal").
- **Vì sao các đáp án khác sai:** **A** thiếu `policyTypes` thì K8s tự suy ra từ các khối `ingress`/`egress` có mặt, không bị bỏ qua; **B** `kube-proxy` xử lý Service/iptables, không liên quan NetworkPolicy; **D** sai hoàn toàn — `default-deny-all` chặn cả hai chiều nếu khai báo đủ `policyTypes`.
- 🧠 **Mẹo ghi nhớ:** NetworkPolicy = **luật trên giấy**; CNI = **cảnh sát thi hành**. Không có cảnh sát thì luật vô nghĩa.

---

### Question 23 — Đáp án: **B**
- **Vì sao đúng:** PVC `Pending` mà `describe` **không có một event nào** là dấu hiệu đặc trưng: *không có provisioner nào nhận claim này*. Nếu driver tồn tại nhưng thất bại, bạn sẽ thấy event `ProvisioningFailed` kèm lý do. Hoàn toàn im lặng nghĩa là:
  - `storageClassName` trỏ tới một class không tồn tại (hoặc gõ sai), **hoặc**
  - PVC không ghi `storageClassName` và cluster **không có default StorageClass** (`kubectl get sc` — không class nào gắn nhãn `(default)`), **hoặc**
  - Class có tồn tại nhưng CSI driver đứng sau `provisioner` chưa được cài / pod của nó đang chết.
- **Vì sao các đáp án khác sai:** **A** `volumeattachments` liên quan tới giai đoạn attach, xảy ra **sau** khi đã bind xong; **C** không hề có ngưỡng tối thiểu 1Gi; **D** đổi `accessModes` sang RWX thường làm tình hình tệ hơn vì ít driver hỗ trợ.
- 🧠 **Mẹo ghi nhớ:** PVC `Pending` **im lặng tuyệt đối** = không ai nhận việc → soi `StorageClass` và CSI driver. PVC `Pending` **có event lỗi** = có người nhận nhưng làm hỏng → đọc thẳng event đó.

