# 🧪 Hands-on Labs — Tuần 3: Taints, Tolerations, Affinity & QoS

> Thực hành cô lập hạ tầng bằng Taints/Tolerations, lập lịch Pod với NodeAffinity, phân tán Pod với PodAntiAffinity, kiểm chứng các lớp QoS, và cấu hình **HPA + Metrics Server**.
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

## Lab 3.4 — Metrics Server, `kubectl top` & HorizontalPodAutoscaler

**🎯 Mục tiêu:** Cài Metrics Server, đọc mức tiêu thụ thật bằng `kubectl top`, dựng HPA, **tái hiện lỗi `<unknown>` rồi tự sửa**, và quan sát HPA scale up dưới tải thật.
**⏱️ ~35 phút**

### Các bước thực hiện:

1. Cài và xác minh Metrics Server:
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

   # Trên Kind/Minikube: kubelet dùng cert self-signed -> phải bỏ qua verify (CHỈ Ở LAB)
   kubectl patch deployment metrics-server -n kube-system --type=json \
     -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

   kubectl rollout status deployment metrics-server -n kube-system
   kubectl get apiservice v1beta1.metrics.k8s.io     # AVAILABLE phải là True
   ```

2. Đọc mức tiêu thụ thực tế (chờ ~60s để có mẫu đầu tiên):
   ```bash
   kubectl top nodes
   kubectl top pods -A --sort-by=memory | head

   # So sánh với phần ĐẶT CHỖ (requests/limits) — hai con số khác nhau hoàn toàn
   kubectl describe node cka-cluster-worker | sed -n '/Allocated resources/,/Events/p'
   ```

3. **Tái hiện lỗi `<unknown>`** — cố tình tạo Deployment **không có** `requests`:
   ```bash
   kubectl create deployment hpa-demo --image=registry.k8s.io/hpa-example --port=80
   kubectl expose deployment hpa-demo --port=80
   kubectl autoscale deployment hpa-demo --cpu-percent=50 --min=1 --max=8

   sleep 60
   kubectl get hpa hpa-demo        # TARGETS: <unknown>/50%  <-- Đúng như dự đoán
   kubectl describe hpa hpa-demo | tail -15
   ```
   > Đọc kỹ Events: `failed to get cpu utilization: missing request for cpu`. Đây chính xác là thông điệp bạn sẽ gặp trong phòng thi.

4. **Sửa lỗi** bằng cách bổ sung `requests`:
   ```bash
   kubectl set resources deployment hpa-demo --requests=cpu=100m --limits=cpu=300m
   kubectl rollout status deployment hpa-demo

   sleep 60
   kubectl get hpa hpa-demo        # Giờ phải hiện dạng  1%/50%
   ```

5. Đổ tải và quan sát HPA scale up:
   ```bash
   # Terminal 1: theo dõi liên tục
   kubectl get hpa hpa-demo -w

   # Terminal 2: bắn request dồn dập
   kubectl run load-generator --image=busybox:1.28 --restart=Never -- \
     /bin/sh -c "while true; do wget -q -O- http://hpa-demo.default.svc.cluster.local; done"
   ```
   Sau 1–3 phút, `REPLICAS` sẽ tăng dần. Đối chiếu với công thức:
   ```text
   desiredReplicas = ceil( currentReplicas × currentUtilization / targetUtilization )
   ```

6. Dừng tải và quan sát scale down (chậm hơn nhiều — mặc định có cửa sổ ổn định 300s):
   ```bash
   kubectl delete pod load-generator
   kubectl get hpa hpa-demo -w      # Kiên nhẫn ~5 phút mới thấy giảm
   ```

7. Viết HPA dạng manifest `autoscaling/v2` với cả CPU lẫn memory:
   ```bash
   cat << 'EOF' | kubectl apply -f -
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: hpa-demo-v2
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: hpa-demo
     minReplicas: 2
     maxReplicas: 8
     metrics:
       - type: Resource
         resource:
           name: cpu
           target:
             type: Utilization
             averageUtilization: 60
       - type: Resource
         resource:
           name: memory
           target:
             type: AverageValue
             averageValue: 200Mi
     behavior:
       scaleDown:
         stabilizationWindowSeconds: 60
   EOF

   kubectl get hpa
   ```

### ✅ Kết quả mong đợi:
- Bước 3: HPA báo `<unknown>/50%` và Events nói rõ `missing request for cpu`.
- Bước 4: Sau khi thêm `requests.cpu`, `TARGETS` chuyển sang con số phần trăm thật.
- Bước 5: `REPLICAS` tăng lên, dừng lại ở `maxReplicas: 8` nếu tải đủ nặng.
- Bước 6: Scale down diễn ra **chậm hơn hẳn** scale up — đó là cơ chế chống flapping có chủ đích.

### 🧠 Ghi vào sổ tay phòng thi:
- HPA `<unknown>` → kiểm tra theo đúng thứ tự: (1) Pod có `requests.cpu` không → (2) `kubectl top pods` có chạy không → (3) `kubectl get apiservice v1beta1.metrics.k8s.io`.
- Scale **up** nhanh, scale **down** chậm — đừng ngồi chờ rồi tưởng HPA hỏng.
- `averageUtilization` = % của **requests**; `averageValue` = **con số tuyệt đối**.


---

## 🧹 Dọn dẹp:
```bash
kubectl delete pod regular-pod tolerant-pod qos-guaranteed qos-burstable qos-besteffort
kubectl delete deployment secure-web
kubectl label nodes cka-cluster-worker env- zone-
kubectl label nodes cka-cluster-worker2 env- zone-
kubectl delete deployment hpa-demo --ignore-not-found
kubectl delete svc hpa-demo --ignore-not-found
kubectl delete hpa hpa-demo hpa-demo-v2 --ignore-not-found
kubectl delete pod load-generator --ignore-not-found
```
