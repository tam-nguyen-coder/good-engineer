# Question #39 - Topic 1

A company maintains a searchable repository of items on its website. The data is stored in an Amazon RDS for MySQL database table that contains more than 10 million rows. The database has 2 TB of General Purpose SSD storage. There are millions of updates against this data every day through the company's website. The company has noticed that some insert operations are taking 10 seconds or longer. The company has determined that the database storage performance is the problem. Which solution addresses this performance issue?

## Options

**A.** Change the storage type to Provisioned IOPS SSD.

**B.** Change the DB instance to a memory optimized instance class.

**C.** Change the DB instance to a burstable performance instance class.

**D.** Enable Multi-AZ RDS read replicas with MySQL native asynchronous replication.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty duy trì kho lưu trữ dữ liệu có khả năng tìm kiếm trên website. Dữ liệu được cập nhật liên tục thông qua website.
- **Existing Resources:** `Amazon RDS for MySQL`, bảng dữ liệu có hơn 10 triệu rows, dung lượng lưu trữ 2 TB `General Purpose SSD`.
- **Current Issue/Goal:** Hàng triệu thao tác cập nhật mỗi ngày. Các lệnh `INSERT` mất 10 giây hoặc hơn. Đã xác định **storage performance** là nguyên nhân. Cần chọn giải pháp khắc phục vấn đề hiệu năng lưu trữ.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `General Purpose SSD` | Loại storage gp2/gp3, phù hợp workload phổ thông nhưng có giới hạn IOPS/thông lượng dựa trên kích thước volume và burst balance. |
| Millions of updates | Workload write-intensive, tạo áp lực I/O lớn và liên tục lên storage layer. |
| Insert operations 10+ seconds | Dấu hiệu rõ ràng của I/O latency cao, thường do storage không đáp ứng đủ IOPS cho thao tác ghi ngẫu nhiên. |
| Database storage performance is the problem | Xác định rõ root cause nằm ở tầng lưu trữ (disk I/O), không phải CPU, memory hay network. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Problem solving / Performance optimization.
- **Constraints:** Phải giải quyết đúng bottleneck là storage performance trên workload nặng về ghi (write-heavy).

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**
**Giải thích:** Đề bài đã chỉ rõ **storage performance** là vấn đề. `General Purpose SSD` (gp2/gp3) có thể đạt ngưỡng giới hạn IOPS hoặc thông lượng khi phải xử lý hàng triệu thao tác ghi (`INSERT`/`UPDATE`) mỗi ngày trên bộ dữ liệu 2 TB, dẫn đến độ trễ cao. `Provisioned IOPS SSD` (`io1`/`io2`) được thiết kế riêng cho các workload I/O-intensive, cung cấp IOPS ổn định, có thể dự đoán được và độ trễ thấp, giúp loại bỏ bottleneck ở tầng lưu trữ. Việc chuyển đổi storage type trực tiếp đánh vào nguyên nhân được xác định trong đề.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** Thay đổi sang `memory optimized instance class` (ví dụ `db.r6g`) giúp tăng RAM để cache dữ liệu, giảm read I/O từ disk. Tuy nhiên, đây là tối ưu compute/memory, không phải storage. Các thao tác `INSERT` (write) vẫn bắt buộc phải ghi xuống disk, nên nếu storage là bottleneck thì thêm memory không giải quyết được độ trễ ghi.

**❌ Đáp án C:** `Burstable performance instance class` (ví dụ `db.t3`, `db.t4g`) cung cấp CPU baseline thấp với khả năng burst tín dụng. Workload của công ty có hàng triệu updates mỗi ngày là sustained workload, hoàn toàn không phù hợp với burstable. Hơn nữa, đây cũng là thay đổi compute, không cải thiện storage performance.

**❌ Đáp án D:** `Multi-AZ` phục vụ mục đích High Availability (HA) thông qua synchronous standby, không cải thiện performance. `Read replicas` dùng để scale read traffic, nhưng đề bài đang gặp vấn đề với `INSERT` operations (write traffic). Read replicas không những không giúp tăng tốc write mà còn tạo thêm overhead replication cho primary instance.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài xác định rõ "storage performance" là vấn đề và workload nặng về ghi (insert/update) trên `General Purpose SSD` → nghĩ ngay đến `Provisioned IOPS SSD` (`io1`/`io2`). Thay đổi instance class (memory/burstable) chỉ tác động đến compute layer. Read replicas/Multi-AZ dùng cho read scaling và HA, không bao giờ là giải pháp cho write storage bottleneck.*


