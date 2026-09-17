# 🧪 Hands-on Labs — Tuần 1: Kiến trúc K8s + Setup Lab Multi-node + `kubectl` Imperative Pro

> Lab cầm tay chỉ việc, chạy được trên máy tính cá nhân (Mac/Linux/WSL2).
> ⚙️ Yêu cầu: Đã cài Docker Desktop / Colima / OrbStack.
> Về [plan tuần 1](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

---

## Lab 1.1 — Khởi tạo cụm Kubernetes Multi-node bằng Kind (Kubernetes in Docker)

**🎯 Mục tiêu:** Tạo một cụm gồm 1 Control-Plane và 2 Worker Nodes chạy trên Docker container để mô phỏng chính xác môi trường thi CKA.
**⏱️ ~15 phút**

### Các bước thực hiện:

1. Cài đặt công cụ `kind` và `kubectl` (nếu chưa có):
   ```bash
   # Trên macOS:
   brew install kind kubectl

   # Kiểm tra phiên bản:
   kind version
   kubectl version --client
   ```

2. Tạo file cấu hình cluster `kind-config.yaml`:
   ```bash
   cat <<EOF > kind-config.yaml
   kind: Cluster
   apiVersion: kind.x-k8s.io/v1alpha4
   name: cka-cluster
   nodes:
   - role: control-plane
     image: kindest/node:v1.35.0
   - role: worker
     image: kindest/node:v1.35.0
   - role: worker
     image: kindest/node:v1.35.0
   EOF
   ```

3. Khởi tạo cluster:
   ```bash
   kind create cluster --config kind-config.yaml
   ```

4. Kiểm tra danh sách Nodes và các Pods hệ thống:
   ```bash
   kubectl get nodes -o wide
   kubectl get pods -n kube-system
   ```

   **Output mong muốn:**
   ```text
   NAME                        STATUS   ROLES           AGE   VERSION
   cka-cluster-control-plane   Ready    control-plane   2m    v1.35.0
   cka-cluster-worker          Ready    <none>          90s   v1.35.0
   cka-cluster-worker2         Ready    <none>          90s   v1.35.0
   ```

---

## Lab 1.2 — Thiết lập môi trường Terminal chuẩn thi CKA

**🎯 Mục tiêu:** Cấu hình shell để tăng tốc độ gõ lệnh lên gấp 5 lần, giảm thiểu nguy cơ sai lỗi cú pháp YAML.
**⏱️ ~10 phút**

### Các bước thực hiện:

1. Thêm cấu hình vào file shell rc (`~/.bashrc` hoặc `~/.zshrc`):
   ```bash
   # Mở file rc tương ứng với shell bạn dùng:
   cat << 'EOF' >> ~/.bashrc

   # 1. Alias kubectl
   alias k=kubectl
   complete -o default -F __start_kubectl k

   # 2. Biến tắt cho dry-run và xoá nhanh
   export do="--dry-run=client -o yaml"
   export now="--force --grace-period=0"

   # 3. Alias xem tài nguyên thông dụng
   alias kgp="kubectl get pods -o wide"
   alias kgs="kubectl get svc -o wide"
   alias kgd="kubectl get deploy -o wide"
   alias kgn="kubectl get nodes -o wide"
   alias kdes="kubectl describe"

   EOF

   # Nạp lại cấu hình:
   source ~/.bashrc
   ```

2. Cấu hình Vim Editor tối ưu cho định dạng YAML (`~/.vimrc`):
   ```bash
   cat << 'EOF' > ~/.vimrc
   set tabstop=2
   set shiftwidth=2
   set expandtab
   set autoindent
   set smartindent
   set paste
   set number
   EOF
   ```

3. Kiểm tra thử nghiệm alias:
   ```bash
   k get nodes
   ```

---

## Lab 1.3 — Bài tập phản xạ Imperative CLI (Tạo YAML trong 5 giây)

**🎯 Mục tiêu:** Luyện phản xạ tạo nhanh các đối tượng K8s mà không cần mở tài liệu hay viết YAML thủ công.
**⏱️ ~25 phút**

### Các bài tập thực hành:

1. **Task 1: Tạo Namespace và Pod**
   Yêu cầu: Tạo namespace `staging`. Sau đó tạo Pod tên `web-front` chạy image `nginx:1.25-alpine` trong namespace `staging`, gán nhãn `app=frontend`, mở cổng `80`.
   ```bash
   # Bước 1: Tạo namespace
   k create ns staging

   # Bước 2: Tạo Pod bằng imperative
   k run web-front --image=nginx:1.25-alpine -n staging --labels="app=frontend" --port=80
   ```

2. **Task 2: Tạo YAML template cho Pod có biến môi trường**
   Yêu cầu: Sinh file manifest `db-pod.yaml` cho Pod `db-redis` image `redis:7-alpine`, namespace `staging`, có biến môi trường `DB_PORT=6379`.
   ```bash
   k run db-redis --image=redis:7-alpine -n staging --env="DB_PORT=6379" $do > db-pod.yaml

   # Kiểm tra nội dung file:
   cat db-pod.yaml

   # Áp dụng tạo Pod:
   k apply -f db-pod.yaml
   ```

3. **Task 3: Expose Pod thành Service nhanh**
   Yêu cầu: Expose Pod `web-front` vừa tạo thành Service tên `web-front-svc` kiểu `ClusterIP` lắng nghe cổng 8080 và trỏ về targetPort 80 của container.
   ```bash
   k expose pod web-front -n staging --name=web-front-svc --port=8080 --target-port=80 --type=ClusterIP

   # Kiểm tra Service và Endpoints:
   k get svc web-front-svc -n staging
   k get ep web-front-svc -n staging
   ```

4. **Task 4: Trích xuất thông tin bằng JSONPath**
   Yêu cầu: Lấy toàn bộ IP của các Pod trong namespace `staging` mà không cần xem bảng biểu.
   ```bash
   k get pods -n staging -o jsonpath='{.items[*].status.podIP}'
   ```

---

## Lab 1.4 — Multi-container Pods, Init Containers & Native Sidecars

**🎯 Mục tiêu:** Hiểu rõ sự khác biệt giữa Container chính, Init Container truyền thống và Native Sidecar container (tính năng K8s 1.28+).
**⏱️ ~30 phút**

### Kịch bản thực hành:

Ứng dụng web cần 2 tác vụ phụ trợ:
1. Một **Init Container** tải file `index.html` mẫu trước khi web server chạy.
2. Một **Native Sidecar Container** chạy ngầm liên tục để đọc file log của web server.

### Các bước thực hiện:

1. Tạo file manifest `multi-pod.yaml`:
   ```bash
   cat << 'EOF' > multi-pod.yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: multi-container-demo
     namespace: default
     labels:
       app: web-suite
   spec:
     # 1. INIT CONTAINER: Chạy xong mới tới container khác
     initContainers:
     - name: init-downloader
       image: busybox:1.28
       command: ['sh', '-c', 'echo "<h1>Welcome to Kubernetes CKA Labs</h1>" > /workdir/index.html']
       volumeMounts:
       - name: web-content
         mountPath: /workdir

     # 2. NATIVE SIDECAR CONTAINER: Chạy song song suốt vòng đời
     - name: log-sidecar
       image: busybox:1.28
       restartPolicy: Always # <-- Thuộc tính biến container thành Native Sidecar
       command: ['sh', '-c', 'tail -F /var/log/nginx/access.log']
       volumeMounts:
       - name: log-dir
         mountPath: /var/log/nginx

     # 3. CONTAINER CHÍNH
     containers:
     - name: nginx-server
       image: nginx:alpine
       ports:
       - containerPort: 80
       volumeMounts:
       - name: web-content
         mountPath: /usr/share/nginx/html
       - name: log-dir
         mountPath: /var/log/nginx

     volumes:
     - name: web-content
       emptyDir: {}
     - name: log-dir
       emptyDir: {}
   EOF
   ```

2. Áp dụng manifest và quan sát tiến trình khởi động:
   ```bash
   k apply -f multi-pod.yaml
   k get pod multi-container-demo -w
   ```
   *Quan sát: Pod sẽ chuyển từ `Init:0/2` -> `Init:1/2` -> `PodInitializing` -> `Running` với trạng thái `2/2 Ready` (1 main container + 1 native sidecar).*

3. Kiểm tra log của từng container trong Pod:
   ```bash
   # Xem log của container chính
   k logs multi-container-demo -c nginx-server

   # Xem log của sidecar container
   k logs multi-container-demo -c log-sidecar
   ```

4. Tạo traffic và kiểm tra sidecar bắt log:
   ```bash
   # Lấy Pod IP
   POD_IP=$(k get pod multi-container-demo -o jsonpath='{.status.podIP}')

   # Gửi request từ temporary pod
   k run curl-test --image=curlimages/curl --rm -it --restart=Never -- curl http://$POD_IP

   # Xem lại log của sidecar container:
   k logs multi-container-demo -c log-sidecar
   ```

---

## Lab 1.5 — Khám phá Static Pods trên Control-plane Node

**🎯 Mục tiêu:** Hiểu cách thức hoạt động của Static Pods tại `/etc/kubernetes/manifests/` — nền tảng của các thành phần Control Plane.
**⏱️ ~20 phút**

### Các bước thực hiện:

1. Mở shell truy cập trực tiếp vào container Control Plane của Kind:
   ```bash
   docker exec -it cka-cluster-control-plane bash
   ```

2. Di chuyển vào thư mục static pod manifest:
   ```bash
   cd /etc/kubernetes/manifests
   ls -la
   ```
   *Bạn sẽ thấy 4 file:*
   - `etcd.yaml`
   - `kube-apiserver.yaml`
   - `kube-controller-manager.yaml`
   - `kube-scheduler.yaml`

3. Tạo một Static Pod mới tên `my-static-web`:
   ```bash
   cat << 'EOF' > my-static-web.yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: my-static-web
   spec:
     containers:
     - name: web
       image: nginx:alpine
   EOF
   ```

4. Thoát khỏi container (`exit`) và quay lại máy host:
   ```bash
   kubectl get pods -A | grep my-static-web
   ```
   *Quan sát tên Pod: `my-static-web-cka-cluster-control-plane` (Kubelet tự động thêm tên Node vào sau tên Static Pod).*

5. Thử xoá Static Pod bằng `kubectl delete`:
   ```bash
   kubectl delete pod my-static-web-cka-cluster-control-plane
   kubectl get pods -A | grep my-static-web
   ```
   *Nhận xét: Pod bị xoá nhưng lập tức xuất hiện lại! Vì Kubelet trên Node thấy file manifest trong `/etc/kubernetes/manifests` vẫn còn, nó sẽ tự động tạo lại.*

6. Dọn dẹp Static Pod:
   ```bash
   docker exec -it cka-cluster-control-plane rm /etc/kubernetes/manifests/my-static-web.yaml
   kubectl get pods -A | grep my-static-web
   ```
   *(Pod sẽ tự động biến mất hoàn toàn).*

---

## 🧹 Dọn dẹp môi trường cuối tuần:

```bash
# Xoá cluster Kind khi học xong tuần 1:
kind delete cluster --name cka-cluster
```
