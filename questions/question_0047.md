# Question #47 - Topic 1

A company needs guaranteed Amazon EC2 capacity in three specific Availability Zones in a specific AWS Region for an upcoming event that will last 1 week. What should the company do to guarantee the EC2 capacity?

## Options

**A.** Purchase Reserved Instances that specify the Region needed.

**B.** Create an On-Demand Capacity Reservation that specifies the Region needed.

**C.** Purchase Reserved Instances that specify the Region and three Availability Zones needed.

**D.** Create an On-Demand Capacity Reservation that specifies the Region and three Availability Zones needed.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty chuẩn bị cho một sự kiện kéo dài 1 tuần và cần đảm bảo chắc chắn có đủ `Amazon EC2` capacity để launch instances.
- **Existing Resources:** Không đề cập tài nguyên hiện có.
- **Current Issue/Goal:** Cần guarantee capacity ở ba `Availability Zones` cụ thể trong một `AWS Region` cho khoảng thời gian ngắn (1 tuần).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `Guaranteed EC2 capacity` | Đảm bảo không gặp lỗi `Insufficient Instance Capacity` khi cần launch instance |
| `Three specific Availability Zones` | Yêu cầu capacity ở đúng 3 AZ đã chọn, không phải bất kỳ AZ nào trong Region |
| `1 week` | Thời gian sử dụng ngắn hạn, không phù hợp với cam kết dài hạn |
| `Reserved Instances` | Cam kết 1 hoặc 3 năm để đổi lấy giảm giá; `Zonal RI` mới reserve capacity |
| `On-Demand Capacity Reservation` | Đặt trước capacity ở mức giá On-Demand, không có thời hạn tối thiểu, có thể hủy bất cứ lúc nào |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Solution finding (tìm giải pháp đảm bảo capacity ngắn hạn ở các AZ cụ thể)
- **Constraints:** 
  - Phải guarantee capacity (không chỉ giảm giá)
  - Phải cover đúng 3 AZ cụ thể
  - Thời gian sử dụng chỉ 1 tuần
  - Phải chỉ định Region

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**
**Giải thích:** `On-Demand Capacity Reservation` (ODCR) cho phép bạn reserve capacity tại các `Availability Zones` cụ thể trong một `Region` với thời hạn hoàn toàn linh hoạt — không có cam kết tối thiểu, có thể tạo và hủy sau 1 tuần. Khi tạo ODCR, bạn phải chỉ định rõ `Availability Zone` và instance type, đảm bảo capacity luôn sẵn sàng để launch instances tại đúng các AZ đó. Điều này hoàn toàn phù hợp với yêu cầu ngắn hạn (1 tuần) và bảo đảm capacity ở 3 AZ cụ thể của đề bài.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `Regional Reserved Instances` chỉ cung cấp billing discount và flexibility khi chạy instance ở bất kỳ AZ nào trong Region, nhưng **không đảm bảo reserved capacity** ở các AZ cụ thể. Hơn nữa, `Reserved Instances` yêu cầu thời hạn tối thiểu 1 hoặc 3 năm, hoàn toàn không phù hợp cho nhu cầu 1 tuần.

**❌ Đáp án B:** `On-Demand Capacity Reservation` được tạo ở cấp `Availability Zone`, không phải cấp `Region`. Nếu chỉ specify Region mà không chỉ định cụ thể các AZ, AWS sẽ không biết cần reserve capacity ở đâu, do đó không thể đảm bảo capacity ở đúng 3 AZ yêu cầu.

**❌ Đáp án C:** Mặc dù `Zonal Reserved Instances` có thể reserve capacity ở một AZ cụ thể, nhưng `Reserved Instances` bắt buộc thời hạn tối thiểu 1 năm. Không thể mua RI chỉ cho 1 tuần, và việc mua RI cho 3 AZ sẽ gây lãng phí cực lớn cho nhu cầu ngắn hạn.

## 6. MẸO GHI NHỚ
🧠 *Cần capacity ngắn hạn (vài giờ/vài tuần) ở AZ cụ thể → `On-Demand Capacity Reservation`. Cần giảm giá dài hạn (1-3 năm) → `Reserved Instances`. Nhớ: `Regional RI` = giảm giá, không giữ chỗ; `Zonal RI` = giữ chỗ 1 AZ nhưng khóa 1-3 năm; `ODCR` = giữ chỗ + linh hoạt thời gian.*
