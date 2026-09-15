# 🧪 Hands-on Labs — Tuần 10: Break-and-Fix K8s Troubleshooting Masterclass

> Thực hành xử lý 3 kịch bản sự cố kinh điển trong kỳ thi CKA: Node NotReady, CrashLoopBackOff Pod, và API Server sập do hỏng cấu hình static pod.
> Về [plan tuần 10](README.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

---

## Lab 10.1 — Kịch bản 1: Cứu hộ Worker Node bị `NotReady`

**🎯 Mục tiêu:** Cố tình làm hỏng Kubelet trên Worker Node và khắc phục sự cố đưa Node trở lại `Ready`.
**⏱️ ~20 phút**

### Các bước thực hiện:

1. SSH vào worker node của Kind:
   ```bash
   docker exec -it cka-cluster-worker bash
   ```

2. **Cố tình tạo lỗi:** Đổi sai địa chỉ server trong file cấu hình Kubelet kubeconfig hoặc dừng service containerd:
   ```bash
   # Dừng runtime containerd
   systemctl stop containerd
   # Khởi động lại kubelet
   systemctl restart kubelet
   ```

3. Thoát ra máy host và kiểm tra danh sách Node:
   ```bash
   exit
   kubectl get nodes
   ```
   *Quan sát: Node `cka-cluster-worker` sau khoảng 40 giây sẽ chuyển sang trạng thái `NotReady`.*

4. **Bắt đầu quy trình cứu hộ:**
   SSH lại vào node bị lỗi:
   ```bash
   docker exec -it cka-cluster-worker bash
   ```

5. Kiểm tra trạng thái service Kubelet:
   ```bash
   systemctl status kubelet
   ```
   *Quan sát: Kubelet báo lỗi kết nối tới CRI socket `/run/containerd/containerd.sock`.*

6. Xem log chi tiết bằng `journalctl`:
   ```bash
   journalctl -u kubelet -e --no-pager
   ```
   *Log ghi rõ: `failed to connect to container runtime: connect: connection refused`.*

7. Khắc phục: Khởi động lại Container Runtime:
   ```bash
   systemctl start containerd
   systemctl restart kubelet
   systemctl status kubelet
   ```
   *Quan sát: Kubelet chuyển sang trạng thái `active (running)`.*

8. Thoát ra máy host và kiểm chứng:
   ```bash
   exit
   kubectl get nodes
   ```
   *Quan sát: Node đã trở lại trạng thái `Ready` thành công!*

---

## Lab 10.2 — Kịch bản 2: Gỡ lỗi Pod bị kẹt `CrashLoopBackOff`

**🎯 Mục tiêu:** Phân tích log của container bị crash trong quá khứ (`--previous`) và sửa lỗi lệnh khởi động.
**⏱️ ~20 phút**

### Các bước thực hiện:

1. Tạo một Pod bị lỗi cấu hình lệnh khởi động:
   ```bash
   cat << 'EOF' > broken-pod.yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: broken-runner
   spec:
     containers:
     - name: runner
       image: busybox:1.28
       command: ["sh", "-c", "echo 'Application starting...'; cat /etc/missing-config.json; exit 1"]
   EOF

   kubectl apply -f broken-pod.yaml
   ```

2. Quan sát trạng thái:
   ```bash
   kubectl get pod broken-runner -w
   ```
   *Quan sát: Pod sẽ chuyển từ `Error` sang `CrashLoopBackOff`.*

3. **Điều tra nguyên nhân bằng lệnh chuyên dụng:**
   ```bash
   # 1. Đọc log của lần chạy gần nhất đã bị chết:
   kubectl logs broken-runner --previous

   # 2. Xem các Events cảnh báo:
   kubectl describe pod broken-runner
   ```
   *Quan sát: Log chỉ rõ: `cat: can't open '/etc/missing-config.json': No such file or directory`.*

4. Sửa lỗi:
   Tạo file cấu hình hoặc chỉnh sửa lại lệnh chạy:
   ```bash
   kubectl get pod broken-runner -o yaml > fixed-pod.yaml
   # Sửa lệnh command thành lệnh chạy nền ổn định:
   sed -i '' 's/cat \/etc\/missing-config.json; exit 1/while true; do sleep 30; done/g' fixed-pod.yaml
   kubectl replace --force -f fixed-pod.yaml
   ```

5. Kiểm tra kết quả:
   ```bash
   kubectl get pod broken-runner
   ```
   *Quan sát: Pod chuyển sang trạng thái `Running` `1/1 Ready`.*

---

## Lab 10.3 — Kịch bản 3: Sửa lỗi `kube-apiserver` bị sập do sai Static Manifest

**🎯 Mục tiêu:** Khắc phục tình trạng toàn bộ cụm mất kết nối do gõ sai tham số trong static pod manifest của API Server.
**⏱️ ~25 phút**

### Các bước thực hiện:

1. SSH vào Control Plane:
   ```bash
   docker exec -it cka-cluster-control-plane bash
   ```

2. **Cố tình tạo lỗi:** Sửa sai cổng hoặc cờ trong `/etc/kubernetes/manifests/kube-apiserver.yaml`:
   ```bash
   # Thêm một cờ sai cú pháp vào file apiserver
   sed -i 's/--secure-port=6443/--secure-port=6443\n    - --non-existent-broken-flag=true/' /etc/kubernetes/manifests/kube-apiserver.yaml
   ```

3. Thoát ra máy host và thử chạy `kubectl`:
   ```bash
   exit
   kubectl get nodes
   ```
   *KẾT QUẢ: `The connection to the server <host>:6443 was refused - did you specify the right host or port?` Lệnh kubectl hoàn toàn tê liệt!*

4. **Bắt đầu gỡ lỗi cấp thấp:**
   SSH lại vào Control Plane:
   ```bash
   docker exec -it cka-cluster-control-plane bash
   ```

5. Vì API server đã chết, `kubectl` không dùng được. Dùng **`crictl`** để xem container bị exit:
   ```bash
   crictl ps -a | grep kube-apiserver
   ```
   *Lấy Container ID của container kube-apiserver vừa bị exit.*

6. Xem log container bằng crictl:
   ```bash
   crictl logs <container-id-vừa-lấy>
   ```
   *Output chỉ rõ: `unknown flag: --non-existent-broken-flag`.*

7. Khắc phục: Mở file `/etc/kubernetes/manifests/kube-apiserver.yaml`, xoá dòng cờ sai đó đi và lưu lại.

8. Thoát ra host và kiểm tra lại:
   ```bash
   exit
   # Đợi 20 giây cho Kubelet start lại API server:
   kubectl get nodes
   ```
   *Quan sát: Toàn bộ cụm đã hồi sinh và hoạt động bình thường! Bạn đã chinh phục được kỹ năng gỡ lỗi đỉnh cao nhất của CKA.*

---

## 🧹 Dọn dẹp:
```bash
kubectl delete pod broken-runner
```
