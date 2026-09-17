# ✅ Answers & Explanations — Tuần 3: Pod Scheduling & QoS

> Mở file này sau khi đã tự làm 19 câu hỏi trong [questions.md](questions.md).
> Về [plan tuần 3](README.md) · [Bài Lab](labs.md) · [Kế hoạch tổng](../../K8S-STUDY-PLAN.md)

**Bảng đáp án nhanh:**
`1-B` · `2-C` · `3-B` · `4-B` · `5-B` · `6-C` · `7-C` · `8-B` · `9-B` · `10-B` · `11-A` · `12-B` · `13-B` · `14-C` · `15-B` · `16-B` · `17-B` · `18-C` · `19-C`

---

### Question 1 — Đáp án: **B**
- **Vì sao đúng:** Hiệu ứng `NoSchedule` chỉ áp dụng cho việc lập lịch các Pod mới. Nó hoàn toàn không ảnh hưởng đến các Pod đang chạy sẵn trên Node trước đó.
- 🧠 **Mẹo ghi nhớ:** `NoSchedule` = Không nhận thêm khách mới, khách cũ vẫn ở bình thường.

---

### Question 2 — Đáp án: **C**
- **Vì sao đúng:** `NoExecute` là hiệu ứng Taint mạnh nhất: không cho Pod mới vào VÀ đuổi (evict) ngay lập tức các Pod đang chạy sẵn nếu chúng không có toleration tương ứng.
- 🧠 **Mẹo ghi nhớ:** Đuổi Pod đang chạy trên node → Dùng **`NoExecute`**.

---

### Question 3 — Đáp án: **B**
- **Vì sao đúng:** Để gỡ bỏ một Taint trong Kubernetes, ta chạy lại câu lệnh taint trên node đó kèm theo một dấu trừ `-` ở cuối cùng của biểu thức (`key=value:effect-`).
- 🧠 **Mẹo ghi nhớ:** Gỡ bỏ Taint = Thêm dấu trừ `-` ở đuôi lệnh taint.

---

### Question 4 — Đáp án: **B**
- **Vì sao đúng:** `requiredDuringSchedulingIgnoredDuringExecution` là quy tắc cứng (Hard Rule): Pod bắt buộc phải được xếp vào node thoả mãn điều kiện; nếu không tìm được node nào, Pod sẽ ở trạng thái `Pending`. Ngược lại, `preferred...` là quy tắc mềm (Soft Rule), nếu không có node thoả mãn thì vẫn chạy ở node khác.
- 🧠 **Mẹo ghi nhớ:** `required...` = Bắt buộc; `preferred...` = Ưu tiên nếu có.

---

### Question 5 — Đáp án: **B**
- **Vì sao đúng:** Nhãn `kubernetes.io/hostname` là nhãn mặc định được Kubelet gán cho từng node, mang giá trị là hostname của máy. Đặt `topologyKey: "kubernetes.io/hostname"` đảm bảo Kube-scheduler coi mỗi node vật lý/ảo là một miền độc lập và không xếp 2 Pod cùng app lên chung một hostname.
- 🧠 **Mẹo ghi nhớ:** Phân tán Pod tránh chung Node → `topologyKey: "kubernetes.io/hostname"`.

---

### Question 6 — Đáp án: **C**
- **Vì sao đúng:** Để đạt chuẩn `Guaranteed`, MỌI container trong Pod phải có đủ cả CPU và Memory, và giá trị `requests == limits` ở từng thông số. Trong đề bài:
  - Container 1: req == lim (200m / 256Mi)
  - Container 2: req == lim (100m / 128Mi)
  Do đó Pod đạt danh hiệu `Guaranteed`.
- 🧠 **Mẹo ghi nhớ:** `Guaranteed` = Đủ CPU & RAM, requests bằng chằn chặn limits.

---

### Question 7 — Đáp án: **C**
- **Vì sao đúng:** Thứ tự tiêu diệt (Eviction) khi Node cạn kiệt tài nguyên (MemoryPressure):
  1. **`BestEffort`** (Bị giết đầu tiên vì không khai báo cam kết tài nguyên).
  2. **`Burstable`** (Bị giết tiếp theo nếu dùng vượt mức requests).
  3. **`Guaranteed`** (Được bảo vệ tối đa, chỉ bị giết cuối cùng khi không còn cách nào khác).
- 🧠 **Mẹo ghi nhớ:** Thứ tự trảm: BestEffort -> Burstable -> Guaranteed.

---

### Question 8 — Đáp án: **B**
- **Vì sao đúng:** CPU là tài nguyên có thể nén được (Compressible Resource). Khi ứng dụng cố tình dùng quá mức `limits.cpu`, Linux cgroups sẽ bóp nghẹt chu kỳ CPU (CPU Throttling), làm ứng dụng chạy chậm lại chứ KHÔNG bao giờ kill tiến trình.
- 🧠 **Mẹo ghi nhớ:** Vượt CPU limit = **Throttling** (không chết).

---

### Question 9 — Đáp án: **B**
- **Vì sao đúng:** Memory là tài nguyên không thể nén (Incompressible Resource). Khi tiến trình đòi cấp phát thêm RAM vượt quá `limits.memory`, nhân Linux không thể cho thêm và buộc phải kích hoạt OOM-killer gửi `SIGKILL` tiêu diệt container ngay lập tức (Exit Code 137).
- 🧠 **Mẹo ghi nhớ:** Vượt Memory limit = **OOMKilled** (Mã 137).

---

### Question 10 — Đáp án: **B**
- **Vì sao đúng:** `nodeSelector` là cú pháp đơn giản nhất dạng Key-Value để gán Pod vào node có nhãn tương ứng.
- 🧠 **Mẹo ghi nhớ:** Gán nhãn đơn giản = `nodeSelector`.

---

### Question 11 — Đáp án: **A**
- **Vì sao đúng:**
  - `LimitRange`: Quy định mức tối thiểu (min), tối đa (max), hoặc giá trị mặc định (default request/limit) cho **từng Container / Pod**.
  - `ResourceQuota`: Đặt mức trần tổng cộng (ví dụ: tổng namespace chỉ được dùng tối đa 10 CPU và 20Gi RAM, hoặc tối đa 20 Pods).
- 🧠 **Mẹo ghi nhớ:** LimitRange = Quy chế từng cá nhân; ResourceQuota = Ngân sách cả phòng ban.

---

### Question 12 — Đáp án: **B**
- **Vì sao đúng:** Khi một Pod có trường `spec.nodeName` được điền sẵn tên của một Node cụ thể, Kube-scheduler sẽ **HOÀN TOÀN BỎ QUA** Pod này! Kubelet trên node đó sẽ tự động phát hiện và khởi chạy Pod ngay lập tức. Đây là kỹ thuật lập lịch thủ công (Manual Scheduling).
- 🧠 **Mẹo ghi nhớ:** Ép Pod vào node không cần Scheduler: Điền **`spec.nodeName`**.

---

### Question 13 — Đáp án: **B**
- **Vì sao đúng:**
  - `operator: "Equal"`: Bắt buộc cả key, value và effect phải trùng khớp.
  - `operator: "Exists"`: Chỉ cần Taint có chứa `key` đó là Pod chịu đựng được, bất kể `value` là gì.
- 🧠 **Mẹo ghi nhớ:** `operator: Exists` = Chỉ cần có mặt key, không quan tâm value.

---

### Question 14 — Đáp án: **C**
- **Vì sao đúng:** `BestEffort` là lớp thấp nhất, dành cho các Pod "vô gia cư" hoàn toàn không đặt bất kỳ một thông số `requests` hay `limits` nào.
- 🧠 **Mẹo ghi nhớ:** Không set gì cả = **`BestEffort`**.

---

### Question 15 — Đáp án: **B**
- **Vì sao đúng:** `PriorityClass` gán trọng số ưu tiên cho Pod. Khi cluster không đủ tài nguyên để xếp Pod quan trọng (Priority cao), Scheduler sẽ tự động đuổi (Preempt / Evict) các Pod có độ ưu tiên thấp hơn ra khỏi Node để lấy chỗ cho Pod quan trọng.
- 🧠 **Mẹo ghi nhớ:** PriorityClass = Quyền ưu tiên chen hàng & cướp chỗ (Preemption).

---

### Question 16 — Đáp án: **B**
- **Vì sao đúng:** Chi tiết quyết định nằm ở chỗ **`kubectl top` vẫn chạy tốt** → Metrics Server hoàn toàn khoẻ mạnh. HPA tính `utilization = usage / requests`. Không có `requests.cpu` thì **mẫu số bằng 0**, phép chia vô nghĩa, HPA đành báo `<unknown>`. Sửa bằng cách thêm requests vào Pod template:
  ```bash
  kubectl set resources deployment web -n prod --requests=cpu=200m
  ```
- **Vì sao các đáp án khác sai:** **A** nếu Metrics Server chết thì `kubectl top` cũng phải lỗi; **C** ngược lại, `autoscaling/v2` là bản khuyến nghị và hỗ trợ đầy đủ CPU; **D** cấu hình `min > max` sẽ bị API server từ chối ngay khi tạo.
- 🧠 **Mẹo ghi nhớ:** `<unknown>` + `top` **chạy được** = thiếu **requests**. `<unknown>` + `top` **cũng hỏng** = chết **Metrics Server**.

---

### Question 17 — Đáp án: **B**
- **Vì sao đúng:** `averageUtilization` **luôn** được tính theo phần trăm của **`resources.requests`**. Ở đây: `200m × 50% = 100m`. Giá trị `limits` hoàn toàn không tham gia vào công thức của HPA (nó chỉ là trần cưỡng chế của kernel/cgroup).
- **Vì sao các đáp án khác sai:** **A** nhầm requests với limits — đây chính là bẫy được cài; **C** không tồn tại khái niệm "điểm giữa"; **D** HPA đo theo Pod, không theo dung lượng node.
- 🧠 **Mẹo ghi nhớ:** HPA nhìn **REQUESTS**, kernel nhìn **LIMITS**.

---

### Question 18 — Đáp án: **C**
- **Vì sao đúng:** Chuỗi lệnh giải quyết đủ 4 yêu cầu: `kubectl top pods` lấy mức dùng **thực tế**; `--sort-by=memory` xếp giảm dần; `--no-headers` bỏ dòng tiêu đề (nếu không, `head -n 1` sẽ lấy nhầm chữ "NAME"); `awk '{print $1}'` cắt lấy đúng tên pod, loại bỏ các cột CPU/MEMORY.
- **Vì sao các đáp án khác sai:** **A** trả về rác về node chứ không phải tên pod; **B** sắp xếp theo **requests đã khai báo**, không phải mức tiêu thụ thật; **D** thiếu `--no-headers` nên lấy nhầm dòng tiêu đề, và còn kèm luôn các cột số.
- 🧠 **Mẹo ghi nhớ:** Đề bắt ghi ra file → công thức 4 nhịp: `top` → `--sort-by` → `--no-headers | head -1` → `awk '{print $1}'`. Xong luôn `cat` lại file để kiểm chứng.

---

### Question 19 — Đáp án: **C**
- **Vì sao đúng:** Vấn đề ở đây là **mỗi Pod được cấp phát quá ít RAM**, không phải thiếu số lượng Pod. Đó đúng là địa hạt của **VPA (Vertical Pod Autoscaler)**: nó quan sát mức dùng lịch sử rồi đề xuất/áp `requests` và `limits` mới. Vì việc đổi resource yêu cầu tạo lại container, VPA phải **restart Pod** để áp dụng.
- **Vì sao các đáp án khác sai:** **A** thêm replica **không** làm mỗi Pod có thêm RAM — chúng vẫn sẽ OOMKilled y như cũ; **B** node to hơn cũng vô ích khi chính `limits` của Pod mới là trần bóp nghẹt; **D** `kubectl top` chỉ **đo**, không hề tự điều chỉnh gì.
- 🧠 **Mẹo ghi nhớ:** Pod bị **OOMKilled** = bài toán **VERTICAL**. Pod **quá tải vì đông request** = bài toán **HORIZONTAL**.

