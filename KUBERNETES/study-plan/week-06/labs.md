# 🧪 Hands-on Labs — Tuần 6: Ingress Routing & NetworkPolicy Firewall

> Thực hành cấu hình Ingress đa domain và thiết lập tường lửa NetworkPolicy microsegmentation.
> Về [plan tuần 6](README.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

---

## Lab 6.1 — Cài đặt Nginx Ingress Controller & Cấu hình Routing

**🎯 Mục tiêu:** Triển khai Nginx Ingress Controller trên Kind và viết Ingress Resource định tuyến theo Host và Path.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Triển khai Nginx Ingress Controller chính thức cho Kind:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
   ```

2. Chờ Ingress Controller Pod chuyển sang trạng thái `Running`:
   ```bash
   kubectl wait --namespace ingress-nginx \
     --for=condition=ready pod \
     --selector=app.kubernetes.io/component=controller \
     --timeout=90s
   ```

3. Tạo 2 ứng dụng web mẫu:
   ```bash
   kubectl create deployment web-one --image=nginx:alpine --port=80
   kubectl expose deployment web-one --port=80

   kubectl create deployment web-two --image=httpd:alpine --port=80
   kubectl expose deployment web-two --port=80
   ```

4. Tạo file Ingress định tuyến:
   ```bash
   cat << 'EOF' > app-ingress.yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: sample-ingress
     annotations:
       ingress.class: nginx
   spec:
     rules:
     - host: "app.local"
       http:
         paths:
         - path: /one
           pathType: Prefix
           backend:
             service:
               name: web-one
               port:
                 number: 80
         - path: /two
           pathType: Prefix
           backend:
             service:
               name: web-two
               port:
                 number: 80
   EOF

   kubectl apply -f app-ingress.yaml
   ```

5. Kiểm tra kiểm chứng:
   ```bash
   kubectl get ingress sample-ingress
   ```

---

## Lab 6.2 — Thiết lập NetworkPolicy bảo vệ Database Pod (Microsegmentation)

**🎯 Mục tiêu:** Cấu hình NetworkPolicy chặn mọi truy cập vào Database, ngoại trừ các request đến từ Backend Pod trên cổng 5432.
**⏱️ ~30 phút**

### Các bước thực hiện:

1. Tạo namespace và 3 Pods đại diện cho 3 tầng: Frontend, Backend, và Database:
   ```bash
   kubectl create ns app-stack

   # 1. Frontend Pod (nhãn: role=frontend)
   kubectl run frontend --image=busybox:1.28 -n app-stack --labels="role=frontend" -- sleep 3600

   # 2. Backend Pod (nhãn: role=backend)
   kubectl run backend --image=busybox:1.28 -n app-stack --labels="role=backend" -- sleep 3600

   # 3. Database Pod (nhãn: role=database) chạy lắng nghe cổng 5432
   kubectl run database --image=nginx:alpine -n app-stack --labels="role=database" --port=5432
   ```

2. Trước khi có NetworkPolicy, test kết nối từ Frontend vào Database:
   ```bash
   DB_IP=$(kubectl get pod database -n app-stack -o jsonpath='{.status.podIP}')
   kubectl exec frontend -n app-stack -- nc -zv $DB_IP 80
   ```
   *Quan sát: Kết nối thành công (open).*

3. Áp dụng NetworkPolicy chỉ cho phép Backend gọi Database trên cổng 80:
   ```bash
   cat << 'EOF' > db-policy.yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: allow-backend-to-db
     namespace: app-stack
   spec:
     podSelector:
       matchLabels:
         role: database # Áp dụng bảo vệ cho Database Pod
     policyTypes:
     - Ingress
     ingress:
     - from:
       - podSelector:
           matchLabels:
             role: backend # CHỈ cho phép từ Pod có nhãn role=backend
       ports:
       - protocol: TCP
         port: 80
   EOF

   kubectl apply -f db-policy.yaml
   ```

4. **Kiểm tra kết quả:**
   - Thử kết nối từ **Frontend** (Bị DROP / Timeout):
     ```bash
     kubectl exec frontend -n app-stack -- nc -zv -w 3 $DB_IP 80
     ```
     *Quan sát: Bị timeout! Frontend hoàn toàn không thể chạm tới Database.*

   - Thử kết nối từ **Backend** (Thành công ngay lập tức):
     ```bash
     kubectl exec backend -n app-stack -- nc -zv -w 3 $DB_IP 80
     ```
     *Quan sát: Kết nối thành công (open)! Microsegmentation hoạt động hoàn hảo.*

---

## 🧹 Dọn dẹp:
```bash
kubectl delete deployment web-one web-two
kubectl delete svc web-one web-two
kubectl delete ingress sample-ingress
kubectl delete ns app-stack
```
