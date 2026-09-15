# 🧪 Hands-on Labs — Tuần 7: PersistentVolumes, Claims & StorageClass

> Thực hành Static Provisioning (PV/PVC hostPath), mount vào Pod và kiểm tra bảo toàn dữ liệu khi Pod bị crash/recreated.
> Về [plan tuần 7](README.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

---

## Lab 7.1 — Cấu hình PersistentVolume & Claim (Static Provisioning)

**🎯 Mục tiêu:** Tạo một PV dung lượng 1Gi, tạo PVC bind vào PV, mount vào Pod Nginx và kiểm chứng dữ liệu không bị mất khi Pod bị xoá.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. Khởi tạo thư mục dữ liệu trên worker node của Kind:
   ```bash
   docker exec -it cka-cluster-worker mkdir -p /mnt/data/web
   docker exec -it cka-cluster-worker sh -c 'echo "Persistent Storage Working!" > /mnt/data/web/index.html'
   ```

2. Tạo PersistentVolume khai báo kiểu `hostPath`:
   ```bash
   cat << 'EOF' > pv.yaml
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: local-pv-1gi
   spec:
     capacity:
       storage: 1Gi
     accessModes:
       - ReadWriteOnce
     persistentVolumeReclaimPolicy: Retain
     storageClassName: manual
     hostPath:
       path: /mnt/data/web
   EOF

   kubectl apply -f pv.yaml
   kubectl get pv local-pv-1gi
   ```
   *Quan sát: PV ở trạng thái `Available`.*

3. Tạo PersistentVolumeClaim yêu cầu dung lượng 500Mi:
   ```bash
   cat << 'EOF' > pvc.yaml
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: web-pvc
   spec:
     accessModes:
       - ReadWriteOnce
     storageClassName: manual
     resources:
       requests:
         storage: 500Mi
   EOF

   kubectl apply -f pvc.yaml
   ```

4. Kiểm tra trạng thái Binding:
   ```bash
   kubectl get pvc web-pvc
   kubectl get pv local-pv-1gi
   ```
   *Quan sát: Cả 2 đều chuyển sang trạng thái `Bound`! Cột VOLUME của PVC trỏ đúng tên `local-pv-1gi`.*

5. Tạo Pod mount PVC này:
   ```bash
   cat << 'EOF' > pod-pvc.yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: web-storage-pod
   spec:
     # Buộc Pod chạy trên worker node nơi có thư mục hostPath
     nodeName: cka-cluster-worker
     containers:
     - name: nginx
       image: nginx:alpine
       ports:
       - containerPort: 80
       volumeMounts:
       - name: storage-vol
         mountPath: /usr/share/nginx/html
     volumes:
     - name: storage-vol
       persistentVolumeClaim:
         claimName: web-pvc
   EOF

   kubectl apply -f pod-pvc.yaml
   ```

6. Kiểm tra nội dung trang web từ Pod:
   ```bash
   kubectl exec web-storage-pod -- cat /usr/share/nginx/html/index.html
   ```
   *Output: `Persistent Storage Working!`.*

7. **Thực nghiệm chứng minh tính bất biến (Persistence):**
   Xoá Pod hoàn toàn:
   ```bash
   kubectl delete pod web-storage-pod
   ```
   Tạo lại Pod mới với tên khác:
   ```bash
   kubectl run web-reborn --image=nginx:alpine --overrides='{"spec":{"nodeName":"cka-cluster-worker","volumes":[{"name":"v","persistentVolumeClaim":{"claimName":"web-pvc"}}],"containers":[{"name":"c","image":"nginx:alpine","volumeMounts":[{"name":"v","mountPath":"/usr/share/nginx/html"}]}]}}'
   ```
   Kiểm tra lại nội dung trên Pod mới:
   ```bash
   kubectl exec web-reborn -- cat /usr/share/nginx/html/index.html
   ```
   *Quan sát: Dữ liệu vẫn còn nguyên vẹn 100%!*

---

## Lab 7.2 — Thí nghiệm Reclaim Policy: Retain vs Delete

**🎯 Mục tiêu:** Hiểu rõ điều gì xảy ra với PV khi PVC bị xoá ở từng chính sách thu hồi.
**⏱️ ~20 phút**

### Các bước thực hiện:

1. Xoá PVC `web-pvc`:
   ```bash
   kubectl delete pod web-reborn
   kubectl delete pvc web-pvc
   ```

2. Kiểm tra trạng thái của PV:
   ```bash
   kubectl get pv local-pv-1gi
   ```
   *Quan sát: Trạng thái của PV chuyển thành `Released` (chứ không phải `Available`). PV này KHÔNG THỂ bind cho PVC mới ngay vì nó vẫn còn dữ liệu cũ.*

3. Để tái sử dụng lại PV này, Admin cần xoá claimRef trong metadata của PV:
   ```bash
   kubectl patch pv local-pv-1gi --type=json -p='[{"op": "remove", "path": "/spec/claimRef"}]'
   kubectl get pv local-pv-1gi
   ```
   *Quan sát: PV đã quay trở lại trạng thái `Available` và sẵn sàng nhận PVC mới.*

---

## 🧹 Dọn dẹp:
```bash
kubectl delete pv local-pv-1gi
```
