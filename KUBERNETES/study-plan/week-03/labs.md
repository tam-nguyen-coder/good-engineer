# 🧪 Hands-on Labs — Tuần 3: Taints, Tolerations, Affinity & QoS

> Thực hành cô lập hạ tầng bằng Taints/Tolerations, lập lịch Pod với NodeAffinity, phân tán Pod với PodAntiAffinity và kiểm chứng các lớp QoS.
> Về [plan tuần 3](README.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

---

## Lab 3.1 — Thí nghiệm Taints & Tolerations

**🎯 Mục tiêu:** Đặt Taint lên một Worker Node và kiểm chứng hành vi của Pod thường vs Pod có Tolerations.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Xác định danh sách các Node trong cluster:
   ```bash
   kubectl get nodes
   ```
   *(Giả sử ta có `cka-cluster-worker` và `cka-cluster-worker2`).*

2. Đặt Taint lên `cka-cluster-worker`:
   ```bash
   kubectl taint nodes cka-cluster-worker tier=special:NoSchedule
   ```

3. Kiểm tra Taint đã được áp dụng:
   ```bash
   kubectl describe node cka-cluster-worker | grep Taints
   ```

4. Tạo một Pod thông thường (không có toleration):
   ```bash
   kubectl run regular-pod --image=nginx --replicas=1
   ```
   Kiểm tra Pod chạy trên Node nào:
   ```bash
   kubectl get pod regular-pod -o wide
   ```
   *Quan sát: Pod sẽ được Kube-scheduler tự động đẩy sang `cka-cluster-worker2` (tránh xa node bị Taint).*

5. Tạo một Pod có chứa `tolerations` phù hợp:
   ```bash
   cat << 'EOF' > tolerant-pod.yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: tolerant-pod
   spec:
     containers:
     - name: nginx
       image: nginx:alpine
     tolerations:
     - key: "tier"
       operator: "Equal"
       value: "special"
       effect: "NoSchedule"
   EOF

   kubectl apply -f tolerant-pod.yaml
   ```

6. Kiểm tra lại sự phân bổ Pod:
   ```bash
   kubectl get pods -o wide
   ```
   *Quan sát: `tolerant-pod` có thể chạy thành công trên node `cka-cluster-worker`.*

7. **Thử nghiệm NoExecute:**
   Chuyển Taint trên `cka-cluster-worker` sang `NoExecute`:
   ```bash
   kubectl taint nodes cka-cluster-worker tier=special:NoSchedule-
   kubectl taint nodes cka-cluster-worker maintenance=true:NoExecute
   ```
   *Quan sát: Mọi Pod đang chạy trên node này (kể cả tolerant-pod vì không có toleration cho `maintenance=true`) sẽ bị Kubelet TRỤC XUẤT NGAY LẬP TỨC!*

8. Gỡ Taint hoàn toàn:
   ```bash
   kubectl taint nodes cka-cluster-worker maintenance=true:NoExecute-
   ```

---

## Lab 3.2 — Cấu hình NodeAffinity & PodAntiAffinity

**🎯 Mục tiêu:** Bắt buộc Pod chỉ chạy trên Node có nhãn môi trường và phân tán các Pod tránh chung Node.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Gán nhãn cho các Worker Node:
   ```bash
   kubectl label nodes cka-cluster-worker env=prod zone=zone-a
   kubectl label nodes cka-cluster-worker2 env=prod zone=zone-b
   ```

2. Tạo Deployment với `nodeAffinity` và `podAntiAffinity`:
   ```bash
   cat << 'EOF' > affinity-deploy.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: secure-web
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: secure-web
     template:
       metadata:
         labels:
           app: secure-web
       spec:
         affinity:
           # 1. Bắt buộc chạy trên node có nhãn env=prod
           nodeAffinity:
             requiredDuringSchedulingIgnoredDuringExecution:
               nodeSelectorTerms:
               - matchExpressions:
                 - key: env
                   operator: In
                   values:
                   - prod
           # 2. Không cho phép 2 Pod secure-web chạy chung trên 1 node hostname
           podAntiAffinity:
             requiredDuringSchedulingIgnoredDuringExecution:
             - labelSelector:
                 matchExpressions:
                 - key: app
                   operator: In
                   values:
                   - secure-web
               topologyKey: "kubernetes.io/hostname"
         containers:
         - name: nginx
           image: nginx:alpine
   EOF

   kubectl apply -f affinity-deploy.yaml
   ```

3. Kiểm tra vị trí phân bổ của 2 Pods:
   ```bash
   kubectl get pods -o wide -l app=secure-web
   ```
   *Quan sát: Đúng 1 Pod nằm trên `worker` và 1 Pod nằm trên `worker2` (phân tán hoàn hảo).*

4. Thử tăng replicas lên 3:
   ```bash
   kubectl scale deployment secure-web --replicas=3
   kubectl get pods -o wide -l app=secure-web
   ```
   *Quan sát: Pod thứ 3 sẽ bị kẹt ở trạng thái `Pending`! Vì toàn cụm chỉ có 2 node thoả mãn điều kiện, Pod thứ 3 nếu được xếp vào bất kỳ node nào cũng sẽ vi phạm luật `podAntiAffinity`!*

---

## Lab 3.3 — Phân tích thực nghiệm 3 lớp QoS Classes

**🎯 Mục tiêu:** Tự tay tạo 3 Pod đại diện cho `Guaranteed`, `Burstable`, `BestEffort` và kiểm tra trường `status.qosClass`.
**⏱️ ~20 phút**

### Các bước thực hiện:

1. Tạo file manifest chứa 3 Pod:
   ```bash
   cat << 'EOF' > qos-pods.yaml
   # 1. GUARANTEED (requests == limits)
   apiVersion: v1
   kind: Pod
   metadata:
     name: qos-guaranteed
   spec:
     containers:
     - name: app
       image: busybox:1.28
       command: ["sleep", "3600"]
       resources:
         requests:
           cpu: "100m"
           memory: "128Mi"
         limits:
           cpu: "100m"
           memory: "128Mi"
   ---
   # 2. BURSTABLE (requests < limits)
   apiVersion: v1
   kind: Pod
   metadata:
     name: qos-burstable
   spec:
     containers:
     - name: app
       image: busybox:1.28
       command: ["sleep", "3600"]
       resources:
         requests:
           memory: "64Mi"
         limits:
           memory: "128Mi"
   ---
   # 3. BESTEFFORT (hoàn toàn không set requests & limits)
   apiVersion: v1
   kind: Pod
   metadata:
     name: qos-besteffort
   spec:
     containers:
     - name: app
       image: busybox:1.28
       command: ["sleep", "3600"]
   EOF

   kubectl apply -f qos-pods.yaml
   ```

2. Kiểm tra trường `qosClass` của từng Pod bằng `kubectl get`:
   ```bash
   kubectl get pod qos-guaranteed -o jsonpath='{.status.qosClass}{"\n"}'
   # Output: Guaranteed

   kubectl get pod qos-burstable -o jsonpath='{.status.qosClass}{"\n"}'
   # Output: Burstable

   kubectl get pod qos-besteffort -o jsonpath='{.status.qosClass}{"\n"}'
   # Output: BestEffort
   ```

---

## 🧹 Dọn dẹp:
```bash
kubectl delete pod regular-pod tolerant-pod qos-guaranteed qos-burstable qos-besteffort
kubectl delete deployment secure-web
kubectl label nodes cka-cluster-worker env- zone-
kubectl label nodes cka-cluster-worker2 env- zone-
```
