# Question #20 - Topic 1

A company wants to improve its ability to clone large amounts of production data into a test environment in the same AWS Region. The data is stored in Amazon EC2 instances on Amazon Elastic Block Store (Amazon EBS) volumes. Modifications to the cloned data must not affect the production environment. The software that accesses this data requires consistently high I/O performance. A solutions architect needs to minimize the time that is required to clone the production data into the test environment. Which solution will meet these requirements?

## Options

**A.** Take EBS snapshots of the production EBS volumes. Restore the snapshots onto EC2 instance store volumes in the test environment.

**B.** Configure the production EBS volumes to use the EBS Multi-Attach feature. Take EBS snapshots of the production EBS volumes. Attach the production EBS volumes to the EC2 instances in the test environment.

**C.** Take EBS snapshots of the production EBS volumes. Create and initialize new EBS volumes. Attach the new EBS volumes to EC2 instances in the test environment before restoring the volumes from the production EBS snapshots.

**D.** Take EBS snapshots of the production EBS volumes. Turn on the EBS fast snapshot restore feature on the EBS snapshots. Restore the snapshots into new EBS volumes. Attach the new EBS volumes to EC2 instances in the test environment.



 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty cần sao chép (clone) lượng lớn dữ liệu production sang môi trường test trong cùng một `AWS Region`.
- **Existing Resources:** Dữ liệu được lưu trữ trên các `Amazon EC2` instances sử dụng `Amazon EBS` volumes.
- **Current Issue/Goal:** Cần tạo bản clone nhanh nhất có thể, đảm bảo các thay đổi trên môi trường test không ảnh hưởng đến production, và phần mềm yêu cầu hiệu năng I/O cao, ổn định (không bị giảm sút ban đầu).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `clone` / `test environment` | Cần tạo bản sao độc lập, không dùng chung volume gốc |
| `modifications must not affect production` | Yêu cầu tách biệt hoàn toàn (isolation), không được attach volume production vào test |
| `consistently high I/O performance` | Cần tránh hiện tượng `lazy loading` khi tạo volume từ snapshot |
| `minimize the time` | Cần giảm thời gian chờ đợi để volume đạt hiệu năng tối đa |
| `EBS fast snapshot restore` | Tính năng giúp volume mới từ snapshot đạt 100% hiệu năng ngay lập tức |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Best performance + Minimize time (tối ưu hiệu năng và thời gian thao tác)
- **Constraints:** Cùng `Region`, dữ liệu lớn, yêu cầu I/O ổn định, dữ liệu test phải độc lập với production

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- `EBS fast snapshot restore` (`FSR`) là tính năng cho phép tạo `EBS volume` mới từ `EBS snapshot` mà không bị độ trễ của quá trình `lazy loading` (tải dữ liệu từ `S3` khi block được truy cập lần đầu).
- Khi bật `FSR`, volume mới được khởi tạo với toàn bộ dữ liệu sẵn sàng ngay lập tức, đảm bảo `consistently high I/O performance` ngay từ những truy cập đầu tiên.
- Các `EBS volumes` mới được tạo từ snapshot và attach vào `EC2` trong môi trường test là hoàn toàn độc lập, nên mọi chỉnh sửa trên test đều không ảnh hưởng đến production.
- Giải pháp này giảm thiểu tối đa thời gian clone so với việc chờ volume tự warm-up hoặc copy dữ liệu thủ công.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Không thể restore `EBS snapshot` trực tiếp lên `EC2 instance store volumes`. `Instance store` là ephemeral storage, dữ liệu sẽ bị mất khi instance stop.
- Ngay cả khi copy gián tiếp, `instance store` không phù hợp cho yêu cầu lưu trữ persistent trong môi trường test.
- *Khi nào đúng:* Nếu đề bài yêu cầu temporary cache hoặc buffer tạm thời, không cần persist dữ liệu.

**❌ Đáp án B:**
- `EBS Multi-Attach` chỉ cho phép attach cùng một volume gốc đến nhiều `EC2 instances` trong cùng một `AZ` (chỉ hỗ trợ `io1`/`io2`), nhưng đây là chia sẻ volume chứ không phải clone.
- Nếu môi trường test thực hiện modifications, dữ liệu production sẽ bị thay đổi theo, vi phạm yêu cầu isolation.
- *Khi nào đúng:* Khi cần chia sẻ dữ liệu read-write giữa các node cluster trong cùng `AZ` (ví dụ: `WSFC`).

**❌ Đáp án C:**
- Khi tạo `EBS volume` từ snapshot mà không sử dụng `fast snapshot restore`, volume sẽ hoạt động ở chế độ `lazy loading`. Các block được truy cập lần đầu sẽ có độ trễ cao do phải fetch từ `S3`.
- Điều này vi phạm yêu cầu `consistently high I/O performance` trong giai đoạn đầu sử dụng.
- Việc "initialize" thủ công không hiệu quả bằng `FSR` và vẫn tốn thời gian warm-up.
- *Khi nào đúng:* Nếu đề bài không yêu cầu hiệu năng cao ngay lập tứ


---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty cần sao chép (clone) lượng lớn dữ liệu production sang môi trường test trong cùng một AWS Region.
- **Existing Resources:** Dữ liệu production nằm trên `Amazon EC2` instances sử dụng `Amazon EBS` volumes.
- **Current Issue/Goal:** 
  - Dữ liệu test phải được cách ly hoàn toàn (thay đổi trên test không ảnh hưởng production).
  - Ứng dụng trong môi trường test cần `consistently high I/O performance` ngay từ đầu.
  - Cần giảm thiểu thời gian để có một bản clone sẵn sàng hoạt động.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `clone` / `test environment` | Cần tạo bản sao độc lập, không chia sẻ volume với production |
| `modifications must not affect the production environment` | Yêu cầu cách ly dữ liệu tuyệt đối giữa test và prod |
| `consistently high I/O performance` | Không chấp nhận latency cao hoặc throughput bị giảm trong giai đoạn khởi tạo |
| `minimize the time that is required to clone` | Cần rút ngắn thời gian volume đạt hiệu năng tối đa và sẵn sàng cho ứng dụng |
| `EBS fast snapshot restore` | Tính năng cho phép volume mới khôi phục từ snapshot đạt 100% provisioned performance ngay lập tức, tránh `lazy loading` |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Chọn giải pháp kiến trúc tối ưu (Solution selection).
- **Constraints:** 
  - Cùng AWS Region.
  - Cách ly dữ liệu (không dùng chung volume với production).
  - Hiệu năng I/O cao và ổn định ngay từ đầu.
  - Giảm thiểu thời gian clone.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:** Để tạo bản clone cách ly, ta dùng `EBS snapshots` của production volumes rồi tạo `new EBS volumes` từ các snapshot này. Tuy nhiên, volume mới tạo từ snapshot thông thường sẽ bị hiện tượng `lazy loading` (dữ liệu thực sự nằm trên `S3`, chỉ được tải xuống khi block được truy cập), gây ra I/O latency cao trong giai đoạn đầu. Bật tính năng `EBS fast snapshot restore` (FSR) trên snapshot trước khi tạo volume sẽ khắc phục điều này, giúp volume mới đạt ngay `provisioned IOPS` và throughput tối đa ngay khi attach vào `EC2` instances trong môi trường test. Điều này đáp ứng cả yêu cầu cách ly (volume mới hoàn toàn độc lập) lẫn yêu cầu hiệu năng cao ổn định.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** Không thể restore `EBS snapshots` trực tiếp lên `EC2 instance store volumes`. `Instance store` là ephemeral storage gắn liền với phần cứng host, không hỗ trợ việc restore snapshot trực tiếp và dữ liệu sẽ bị mất khi instance dừng. Giải pháp này không khả thi về mặt kỹ thuật và không đảm bảo tính bền vững của dữ liệu test.

**❌ Đáp án B:** `EBS Multi-Attach` cho phép gắn cùng một volume vào nhiều instance, nhưng như vậy test environment sẽ truy cập trực tiếp `production EBS volumes`. Mọi thay đổi trên test sẽ ghi trực tiếp lên production data, vi phạm nghiêm trọng yêu cầu "modifications must not affect the production environment". Hơn nữa, `Multi-Attach` chỉ hỗ trợ trên một số loại volume (`io1`/`io2`) và không tạo ra "clone" như đề bài yêu cầu.

**❌ Đáp án C:** Workflow "tạo volume trống, attach trước, rồi mới restore từ snapshot" là không hợp lý về mặt kiến trúc `EBS`, vì snapshot restore được thực hiện bằng cách **tạo mới** volume từ
