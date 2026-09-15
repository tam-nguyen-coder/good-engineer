# 🧪 Hands-on Labs — Tuần 5: Services, Endpoints & CoreDNS Debugging

> Thực hành cấu hình ClusterIP, NodePort, Headless Services và kiểm tra phân giải DNS nội bộ.
> Về [plan tuần 5](README.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

---

## Lab 5.1 — Tạo và kiểm tra Service ClusterIP vs NodePort

**🎯 Mục tiêu:** Expose ứng dụng bằng cả ClusterIP và NodePort, quan sát cách Endpoints tự động cập nhật khi scale Pod.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Tạo một Deployment backend gồm 2 replicas:
   ```bash
   kubectl create deployment backend-api --image=nginx:alpine --replicas=2 --port=80
   ```

2. Expose thành Service `ClusterIP`:
   ```bash
   kubectl expose deployment backend-api --name=backend-svc --port=8080 --target-port=80 --type=ClusterIP
   kubectl get svc backend-svc
   kubectl get ep backend-svc
   ```
   *Quan sát: Cột `ENDPOINTS` hiển thị 2 IP tương ứng với 2 Pod backend.*

3. Scale Deployment lên 4 replicas và kiểm tra lại Endpoints:
   ```bash
   kubectl scale deployment backend-api --replicas=4
   sleep 3
   kubectl get ep backend-svc
   ```
   *Quan sát: Endpoints tự động tăng lên 4 IP ngay lập tức.*

4. Expose thêm một Service kiểu `NodePort` trên cổng 30088:
   ```bash
   cat << 'EOF' > nodeport-svc.yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: backend-nodeport
   spec:
     type: NodePort
     selector:
       app: backend-api
     ports:
     - port: 80
       targetPort: 80
       nodePort: 30088
   EOF

   kubectl apply -f nodeport-svc.yaml
   ```

5. Kiểm tra kết nối qua NodePort từ máy host:
   ```bash
   # Lấy IP của bất kỳ Node nào:
   NODE_IP=$(kubectl get nodes -o jsonpath='{.items[1].status.addresses[?(@.type=="InternalIP")].address}')
   curl http://$NODE_IP:30088
   ```
   *Quan sát: Nginx phản hồi mã 200 OK từ bên ngoài.*

---

## Lab 5.2 — Debug CoreDNS & Test phân giải tên miền FQDN

**🎯 Mục tiêu:** Sử dụng Temporary DNS Utility Pod để kiểm chứng các kịch bản phân giải tên miền cùng namespace, khác namespace và FQDN.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Tạo 2 namespace riêng biệt:
   ```bash
   kubectl create ns team-alpha
   kubectl create ns team-beta
   ```

2. Triển khai service trong `team-alpha`:
   ```bash
   kubectl run alpha-web --image=nginx:alpine -n team-alpha --labels="tier=web"
   kubectl expose pod alpha-web -n team-alpha --name=alpha-svc --port=80 --target-port=80
   ```

3. Khởi tạo một Pod kiểm tra trong `team-beta`:
   ```bash
   kubectl run dns-tester --image=busybox:1.28 -n team-beta --rm -it --restart=Never -- sh
   ```

4. Trong shell của `dns-tester`, thực hiện các câu lệnh `nslookup`:
   ```sh
   # 1. Thử gọi trực tiếp bằng tên ngắn (SẼ THẤT BẠI vì khác namespace):
   nslookup alpha-svc

   # 2. Thử gọi kèm namespace (THÀNH CÔNG):
   nslookup alpha-svc.team-alpha

   # 3. Thử gọi FQDN đầy đủ (THÀNH CÔNG CHUẨN XÁC):
   nslookup alpha-svc.team-alpha.svc.cluster.local

   # 4. Thử gửi HTTP request:
   wget -qO- http://alpha-svc.team-alpha.svc.cluster.local

   # Thoát khỏi pod:
   exit
   ```

---

## Lab 5.3 — Headless Service cho StatefulSet

**🎯 Mục tiêu:** Cấu hình Headless Service (`clusterIP: None`) và quan sát kết quả trả về của DNS query.
**⏱️ ~20 phút**

### Các bước thực hiện:

1. Tạo Headless Service và 2 Pod có nhãn tương ứng:
   ```bash
   cat << 'EOF' > headless-demo.yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: db-cluster
   spec:
     clusterIP: None # <-- ĐẶC ĐIỂM CỦA HEADLESS SERVICE
     selector:
       role: db
     ports:
     - port: 5432
       targetPort: 5432
   ---
   apiVersion: v1
   kind: Pod
   metadata:
     name: db-master
     labels:
       role: db
   spec:
     containers:
     - name: db
       image: busybox:1.28
       command: ["sleep", "3600"]
   ---
   apiVersion: v1
   kind: Pod
   metadata:
     name: db-replica
     labels:
       role: db
   spec:
     containers:
     - name: db
       image: busybox:1.28
       command: ["sleep", "3600"]
   EOF

   kubectl apply -f headless-demo.yaml
   ```

2. Kiểm tra Service vừa tạo:
   ```bash
   kubectl get svc db-cluster
   ```
   *Quan sát cột CLUSTER-IP: hiển thị `None`.*

3. Truy vấn DNS của Headless Service bằng utility pod:
   ```bash
   kubectl run dns-lookup --image=busybox:1.28 --rm -it --restart=Never -- nslookup db-cluster
   ```
   *Quan sát: Khác với Service thường (chỉ trả về 1 ClusterIP duy nhất), CoreDNS trả về DANH SÁCH TẤT CẢ CÁC IP CỦA TỪNG POD (`db-master` và `db-replica`).*

---

## 🧹 Dọn dẹp:
```bash
kubectl delete deployment backend-api
kubectl delete svc backend-svc backend-nodeport db-cluster
kubectl delete pod db-master db-replica
kubectl delete ns team-alpha team-beta
```
